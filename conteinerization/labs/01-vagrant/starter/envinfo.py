"""Збір відомостей про середовище виконання та їх подання сторінкою HTML.

Модуль читає лише стандартні джерела Linux (/proc, /sys, /etc/os-release)
і читає дані студента зі змінних середовища; .env завантажує python-dotenv. Недоступні відомості
пропускаються, тому застосунок працює й там, де частини /proc немає.
"""
from __future__ import annotations

import html
import os
import platform
import pwd
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Змінні процесу мають пріоритет над локальним файлом.
load_dotenv(Path(__file__).with_name(".env"), encoding="utf-8-sig", interpolate=False)

STARTED_AT = time.time()

# Виробники та назви виробів, які DMI повідомляє у віртуальних машинах.
VM_SIGNATURES = (
    "virtualbox", "innotek", "vmware", "qemu", "kvm", "bochs", "xen",
    "amazon ec2", "amazon", "microsoft corporation", "parallels", "bhyve",
    "google", "alibaba cloud", "openstack", "nutanix",
)


def _text(path: str) -> str | None:
    """Вміст файла без кінцевих пропусків або None, якщо він недоступний."""
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return None


def _human_bytes(value: float) -> str:
    size = float(value)
    for unit in ("Б", "КіБ", "МіБ", "ГіБ", "ТіБ"):
        if size < 1024 or unit == "ТіБ":
            return f"{size:.1f} {unit}" if unit != "Б" else f"{int(size)} Б"
        size /= 1024
    return f"{size:.1f} ТіБ"


def _human_seconds(total: float) -> str:
    seconds = int(total)
    days, rest = divmod(seconds, 86400)
    hours, rest = divmod(rest, 3600)
    minutes, secs = divmod(rest, 60)
    parts = []
    if days:
        parts.append(f"{days} дн")
    if hours:
        parts.append(f"{hours} год")
    if minutes:
        parts.append(f"{minutes} хв")
    parts.append(f"{secs} с")
    return " ".join(parts)


def _os_release() -> dict[str, str]:
    data: dict[str, str] = {}
    for line in (_text("/etc/os-release") or "").splitlines():
        key, sep, value = line.partition("=")
        if sep:
            data[key] = value.strip().strip('"')
    return data


def _meminfo() -> dict[str, int]:
    data: dict[str, int] = {}
    for line in (_text("/proc/meminfo") or "").splitlines():
        key, sep, value = line.partition(":")
        if sep:
            number = value.strip().split(" ")[0]
            if number.isdigit():
                data[key] = int(number) * 1024
    return data


def _cpu_model() -> str | None:
    for line in (_text("/proc/cpuinfo") or "").splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip() in ("model name", "Model", "Processor"):
            return value.strip()
    return None


def _cpu_flags() -> set[str]:
    for line in (_text("/proc/cpuinfo") or "").splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip() == "flags":
            return set(value.split())
    return set()


def _detect_virt() -> str | None:
    """Відповідь systemd-detect-virt, якщо утиліта наявна в системі."""
    binary = shutil.which("systemd-detect-virt")
    if not binary:
        return None
    try:
        result = subprocess.run(
            [binary], capture_output=True, text=True, timeout=3, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


def _cgroup_path() -> str:
    """Шлях групи cgroup v2, до якої належить процес."""
    for line in (_text("/proc/self/cgroup") or "").splitlines():
        parts = line.split(":", 2)
        if len(parts) == 3 and parts[1] == "":
            return parts[2]
    return "/"


def _cgroup_value(v2: str, v1: str) -> str | None:
    """Обмеження cgroup: група процесу за схемою v2, далі корінь, далі v1."""
    base = _cgroup_path().strip("/")
    for candidate in (f"/sys/fs/cgroup/{base}/{v2}" if base else None,
                      f"/sys/fs/cgroup/{v2}",
                      f"/sys/fs/cgroup/{v1}"):
        if candidate is None:
            continue
        value = _text(candidate)
        if value is not None:
            return value
    return None


def _format_cpu_quota(raw: str | None) -> str:
    """Значення cpu.max у вигляді кількості процесорів."""
    if raw is None:
        return "невідомо"
    parts = raw.split()
    if parts[0] in ("max", "-1"):
        return "без обмеження"
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
        return f"{int(parts[0]) / int(parts[1]):.2f} процесора ({raw})"
    return raw


def _namespaces() -> dict[str, str]:
    result = {}
    for name in ("pid", "net", "mnt", "uts"):
        try:
            result[name] = os.readlink(f"/proc/self/ns/{name}")
        except OSError:
            continue
    return result


def _primary_ip() -> str | None:
    """Адреса інтерфейса, через який система виходить у мережу.

    З'єднання UDP не надсилає пакетів: ядро лише обирає маршрут.
    """
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.settimeout(1)
        probe.connect(("192.0.2.1", 9))
        return probe.getsockname()[0]
    except OSError:
        return None
    finally:
        probe.close()


def _platform_kind() -> tuple[str, list[str]]:
    """Тип середовища та перелік ознак, за якими його визначено."""
    evidence: list[str] = []

    if Path("/.dockerenv").exists():
        evidence.append("файл /.dockerenv")
    if Path("/run/.containerenv").exists():
        evidence.append("файл /run/.containerenv")
    if os.environ.get("container"):
        evidence.append(f"змінна container={os.environ['container']}")
    cgroup = _text("/proc/1/cgroup") or ""
    if any(mark in cgroup for mark in ("docker", "kubepods", "containerd", "lxc")):
        evidence.append("запис середовища у /proc/1/cgroup")
    if evidence:
        return "контейнер", evidence

    osrelease = (_text("/proc/sys/kernel/osrelease") or "").lower()
    if "microsoft" in osrelease or "wsl" in osrelease:
        return "віртуальна машина WSL2", [f"ядро {osrelease}"]

    detected = _detect_virt()
    if detected and detected != "none":
        evidence.append(f"systemd-detect-virt: {detected}")
    vendor = (_text("/sys/class/dmi/id/sys_vendor") or "").lower()
    product = (_text("/sys/class/dmi/id/product_name") or "").lower()
    for signature in VM_SIGNATURES:
        if signature in vendor or signature in product:
            evidence.append(f"DMI: {vendor or '—'} / {product or '—'}")
            break
    if "hypervisor" in _cpu_flags():
        evidence.append("ознака hypervisor у /proc/cpuinfo")

    if evidence:
        return "віртуальна машина", evidence
    return "фізична машина або тип не визначено", ["ознак віртуалізації не знайдено"]


def collect() -> dict[str, dict[str, object]]:
    """Відомості про середовище, згруповані за розділами."""
    uname = platform.uname()
    release = _os_release()
    memory = _meminfo()
    kind, evidence = _platform_kind()
    uptime = _text("/proc/uptime")
    affinity = os.sched_getaffinity(0) if hasattr(os, "sched_getaffinity") else None

    identity: dict[str, object] = {
        "hostname": socket.gethostname(),
        "time": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z"),
        "app_uptime": _human_seconds(time.time() - STARTED_AT),
    }

    machine: dict[str, object] = {"kind": kind, "evidence": evidence}
    vendor = _text("/sys/class/dmi/id/sys_vendor")
    product = _text("/sys/class/dmi/id/product_name")
    detected = _detect_virt()
    if vendor:
        machine["vendor"] = vendor
    if product:
        machine["product"] = product
    if detected:
        machine["detect_virt"] = detected

    operating_system: dict[str, object] = {
        "distro": release.get("PRETTY_NAME") or uname.system,
        "kernel": uname.release,
        "arch": uname.machine,
    }
    if uptime:
        operating_system["uptime"] = _human_seconds(float(uptime.split()[0]))

    cpu: dict[str, object] = {
        "logical": os.cpu_count(),
    }
    model = _cpu_model()
    if model:
        cpu["model"] = model
    if affinity is not None:
        cpu["available"] = len(affinity)
    cpu["quota"] = _format_cpu_quota(_cgroup_value("cpu.max", "cpu/cpu.cfs_quota_us"))
    try:
        cpu["loadavg"] = ", ".join(f"{value:.2f}" for value in os.getloadavg())
    except OSError:
        pass

    ram: dict[str, object] = {}
    if "MemTotal" in memory:
        ram["total"] = _human_bytes(memory["MemTotal"])
    if "MemAvailable" in memory:
        ram["available"] = _human_bytes(memory["MemAvailable"])
    limit = _cgroup_value("memory.max", "memory/memory.limit_in_bytes")
    if limit and limit.isdigit() and int(limit) < 2**60:
        ram["cgroup_limit"] = _human_bytes(int(limit))
    else:
        ram["cgroup_limit"] = "без обмеження"

    network: dict[str, object] = {
        "interfaces": ", ".join(name for _, name in socket.if_nameindex()),
    }
    address = _primary_ip()
    if address:
        network["primary_ip"] = address

    runtime: dict[str, object] = {
        "python": f"{platform.python_version()} ({sys.executable})",
        "venv": "так" if sys.prefix != sys.base_prefix else "ні",
        "pid": os.getpid(),
        "pid1": _text("/proc/1/comm") or "невідомо",
        "user": f"{pwd.getpwuid(os.getuid()).pw_name} (uid {os.getuid()})",
        "cwd": os.getcwd(),
    }
    namespaces = _namespaces()
    if namespaces:
        runtime["namespaces"] = ", ".join(f"{k}: {v}" for k, v in namespaces.items())

    return {
        "student": {
            "full_name": os.getenv("STUDENT_FULL_NAME", "").strip(),
            "group": os.getenv("STUDENT_GROUP", "").strip(),
            "year": os.getenv("STUDENT_YEAR", "").strip(),
            "programme": os.getenv("STUDENT_PROGRAMME", "").strip(),
        },
        "identity": identity,
        "machine": machine,
        "os": operating_system,
        "cpu": cpu,
        "memory": ram,
        "network": network,
        "runtime": runtime,
    }


def request_facts(request) -> dict[str, object]:
    """Відомості про поточний запит: адреси клієнта та сервера."""
    server = request.scope.get("server") or ("невідомо", 0)
    client = request.scope.get("client") or ("невідомо", 0)
    return {
        "listen": f"{server[0]}:{server[1]}",
        "host_header": request.headers.get("host", "—"),
        "client": f"{client[0]}:{client[1]}",
        "agent": request.headers.get("user-agent", "—"),
    }


TITLES = {
    "student": "Дані студента",
    "identity": "Ідентичність",
    "machine": "Тип машини",
    "os": "Операційна система",
    "cpu": "Процесор",
    "memory": "Оперативна пам'ять",
    "network": "Мережа",
    "runtime": "Процес застосунку",
    "request": "Поточний запит",
}

LABELS = {
    "full_name": "ПІБ",
    "group": "Номер групи",
    "year": "Курс навчання",
    "programme": "Освітня програма",
    "hostname": "Ім'я вузла",
    "time": "Час у системі",
    "app_uptime": "Застосунок працює",
    "kind": "Визначено як",
    "evidence": "Ознаки",
    "vendor": "Виробник (DMI)",
    "product": "Виріб (DMI)",
    "detect_virt": "systemd-detect-virt",
    "distro": "Дистрибутив",
    "kernel": "Ядро",
    "arch": "Архітектура",
    "uptime": "Система працює",
    "model": "Модель",
    "logical": "Логічних процесорів",
    "available": "Доступно процесу",
    "quota": "Квота cgroup",
    "loadavg": "Середнє навантаження",
    "total": "Усього",
    "cgroup_limit": "Обмеження cgroup",
    "interfaces": "Інтерфейси",
    "primary_ip": "Адреса маршруту за умовчанням",
    "python": "Python",
    "venv": "Віртуальне оточення",
    "pid": "PID",
    "pid1": "Процес PID 1",
    "user": "Користувач",
    "cwd": "Робочий каталог",
    "namespaces": "Простори імен",
    "listen": "Сервер прослуховує",
    "host_header": "Заголовок Host",
    "client": "Клієнт",
    "agent": "User-Agent",
}

STYLE = """
:root {
  color-scheme: light;
  --bg: #f1f4f7; --surface: #ffffff; --text: #12161a; --muted: #454d55;
  --border: #c2cad2; --accent: #10406f; --accent-ink: #ffffff;
}
@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: dark;
    --bg: #0f1214; --surface: #191d21; --text: #f3f6f9; --muted: #b8c2cb;
    --border: #39424b; --accent: #8ec2f2; --accent-ink: #0b1015;
  }
}
* { box-sizing: border-box; }
body { margin: 0; padding: 2.5rem 1.25rem; background: var(--bg); color: var(--text);
       font: 17px/1.55 system-ui, "Segoe UI", sans-serif; }
main { max-width: 64rem; margin: 0 auto; }
h1 { font-size: 1.75rem; line-height: 1.25; margin: 0 0 .6rem; }
h1 .host { font-family: ui-monospace, "Cascadia Code", monospace; }
.kind { display: inline-block; margin-bottom: 2rem; padding: .3rem .75rem; border-radius: .35rem;
        background: var(--accent); color: var(--accent-ink); font-weight: 600; font-size: .95rem; }
.grid { display: grid; gap: 1.25rem; grid-template-columns: repeat(auto-fit, minmax(21rem, 1fr)); }
section { background: var(--surface); border: 1px solid var(--border);
          border-radius: .5rem; padding: 1rem 1.15rem; }
h2 { margin: 0 0 .75rem; padding-bottom: .5rem; border-bottom: 2px solid var(--border);
     color: var(--accent); font-size: .8rem; text-transform: uppercase; letter-spacing: .08em; }
dl { display: grid; grid-template-columns: minmax(7rem, auto) 1fr; margin: 0; }
dt, dd { padding: .45rem 0; border-top: 1px solid var(--border); }
dl > dt:first-of-type, dl > dt:first-of-type + dd { border-top: 0; padding-top: 0; }
dt { color: var(--muted); padding-right: 1.25rem; }
dd { margin: 0; overflow-wrap: anywhere; font-size: .95rem;
     font-family: ui-monospace, "Cascadia Code", monospace; font-variant-numeric: tabular-nums; }
footer { margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--border);
         color: var(--muted); font-size: .95rem; }
code { padding: .05rem .3rem; border: 1px solid var(--border); border-radius: .25rem;
       background: var(--bg); color: var(--text); font-family: ui-monospace, monospace; }
a { color: var(--accent); text-underline-offset: .2em; }
a:hover code, a:focus-visible code { border-color: var(--accent); }
a code { color: inherit; }
"""


def _section(key: str, values: dict[str, object]) -> str:
    rows = []
    for field, value in values.items():
        if isinstance(value, list):
            value = "; ".join(str(item) for item in value)
        label = LABELS.get(field, field)
        rows.append(
            f"<dt>{html.escape(label)}</dt><dd>{html.escape(str(value) if value != "" else "Не заповнено")}</dd>"
        )
    title = html.escape(TITLES.get(key, key))
    return f"<section><h2>{title}</h2><dl>{''.join(rows)}</dl></section>"


def render_page(data: dict[str, dict[str, object]], request: dict[str, object]) -> str:
    """Сторінка «паспорта середовища» без зовнішніх ресурсів."""
    sections = [_section(key, values) for key, values in data.items() if values]
    sections.append(_section("request", request))
    hostname = html.escape(str(data["identity"]["hostname"]))
    kind = html.escape(str(data["machine"]["kind"]))
    return (
        "<!doctype html><html lang=\"uk\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>Паспорт середовища</title>"
        f"<style>{STYLE}</style></head><body><main>"
        f"<h1>Паспорт середовища: <span class=\"host\">{hostname}</span></h1>"
        f"<div class=\"kind\">{kind}</div>"
        f"<div class=\"grid\">{''.join(sections)}</div>"
        "<footer>Ті самі відомості у форматі JSON: "
        "<a href=\"/api/env\"><code>/api/env</code></a>; стан застосунку: "
        "<a href=\"/healthz\"><code>/healthz</code></a>. Запустіть застосунок "
        "в іншому середовищі та порівняйте значення.</footer>"
        "</main></body></html>"
    )
