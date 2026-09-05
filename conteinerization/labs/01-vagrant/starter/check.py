"""Перевірка відповідей реального HTTP-сервера; URL передається аргументом."""
import json
import sys
import urllib.error
import urllib.request

args = [arg for arg in sys.argv[1:] if arg != "--student"]
base = (args[0] if args else "http://127.0.0.1:8000").rstrip("/")
SECTIONS = ("identity", "machine", "os", "cpu", "memory", "network", "runtime")


def fetch(route, method="GET"):
    request = urllib.request.Request(base + route, method=method)
    try:
        return urllib.request.urlopen(request, timeout=5)
    except urllib.error.HTTPError as error:
        return error


with fetch("/") as response:
    body = response.read().decode("utf-8")
    assert response.status == 200, response.status
    assert response.headers.get_content_type() == "text/html", response.headers
    assert "Паспорт середовища" in body, body[:200]
    print("PASS 200 /")

with fetch("/api/env") as response:
    payload = json.load(response)
    assert response.status == 200, response.status
    missing = [name for name in SECTIONS if name not in payload["environment"]]
    assert not missing, missing
    assert payload["environment"]["machine"]["kind"], payload["environment"]["machine"]
    assert payload["request"]["listen"], payload["request"]
    student = payload["environment"]["student"]
    assert set(student) == {"full_name", "group", "year", "programme"}, student
    if "--student" in sys.argv:
        import html
        assert all(isinstance(v, str) and v.strip() for v in student.values()), "Заповніть усі чотири поля .env"
        assert all(html.escape(v) in body for v in student.values()), "Дані HTML та JSON різняться"
    print("PASS 200 /api/env")

with fetch("/healthz") as response:
    assert response.status == 200, response.status
    assert json.load(response) == {"status": "ok"}
    print("PASS 200 /healthz")

with fetch("/missing") as response:
    assert response.status == 404, response.status
    print("PASS 404 /missing")

with fetch("/healthz", method="POST") as response:
    assert response.status == 405, response.status
    print("PASS 405 POST /healthz")
