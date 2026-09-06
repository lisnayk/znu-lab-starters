#!/usr/bin/env bash
# EC2 User data для Ubuntu Server 22.04/24.04 LTS.
# Заповніть чотири значення: вони мають збігатися з вашим локальним .env.
# Вставте весь скрипт в Advanced details → User data перед створенням інстанса.
# cloud-init виконує його від root під час першого запуску.
set -Eeuo pipefail

export STUDENT_FULL_NAME=""
export STUDENT_GROUP=""
export STUDENT_YEAR=""
export STUDENT_PROGRAMME=""

for name in STUDENT_FULL_NAME STUDENT_GROUP STUDENT_YEAR STUDENT_PROGRAMME; do
  if [[ -z "${!name//[[:space:]]/}" ]]; then
    printf 'Заповніть %s на початку user-data.sh.\n' "$name" >&2
    exit 1
  fi
done

REPO="https://github.com/lisnayk/znu-lab-starters.git"
DIR="/opt/znu-lab-starters"
APP="$DIR/conteinerization/labs/01-vagrant/starter"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y git python3 python3-venv curl
# Повторний ручний запуск не видаляє наявні файли.
if [[ ! -d "$DIR/.git" ]]; then
  git clone --depth 1 "$REPO" "$DIR"
fi

python3 -m venv "$APP/.venv"
"$APP/.venv/bin/python" -m pip install --disable-pip-version-check -q -r "$APP/requirements.txt"

# Значення записуються як дані, без виконання .env оболонкою.
# Лапки, зворотні слеші та кирилиця зберігаються коректно.
umask 077
python3 - "$APP/.env" <<'PYENV'
import json
import os
from pathlib import Path
import sys

names = ("STUDENT_FULL_NAME", "STUDENT_GROUP", "STUDENT_YEAR", "STUDENT_PROGRAMME")
content = "\n".join(f"{name}={json.dumps(os.environ[name], ensure_ascii=False)}" for name in names)
Path(sys.argv[1]).write_text(content + "\n", encoding="utf-8")
PYENV
umask 022

id -u passport >/dev/null 2>&1 || useradd --system --home-dir "$APP" --shell /usr/sbin/nologin passport
chown passport:passport "$APP/.env"
chmod 600 "$APP/.env"

cat > /etc/systemd/system/passport.service <<UNIT
[Unit]
Description=Passport of environment
After=network-online.target
Wants=network-online.target

[Service]
User=passport
WorkingDirectory=$APP
ExecStart=$APP/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable passport.service
systemctl restart passport.service

# Перевіряємо тільки GET /; студент відкриває цю сторінку з браузера.
for attempt in {1..30}; do
  if curl --fail --silent --output /dev/null http://127.0.0.1:8000/; then
    printf 'GET /: сторінка доступна на порту 8000.\n'
    exit 0
  fi
  sleep 2
done
printf 'Сторінка не відповідає. Перевірте journalctl -u passport та /var/log/cloud-init-output.log.\n' >&2
exit 1
