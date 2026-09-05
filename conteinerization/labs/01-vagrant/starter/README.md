# Паспорт середовища — стартер лабораторної 1

Послідовність: локальний запуск → Vagrant / VirtualBox → AWS EC2.
Після кожного відкрийте GET / у браузері, перевірте свої дані та зробіть
скриншот з адресним рядком для звіту. Повний хід роботи — у Moodle.

## Отримання коду

У Linux/WSL, у робочому каталозі без наявного lab1:

```bash
git clone --depth 1 https://github.com/lisnayk/znu-lab-starters.git
cp -R znu-lab-starters/conteinerization/labs/01-vagrant/starter lab1
cd lab1
```

## Дані студента

Скопіюйте .env.example у .env, заповніть чотири значення в лапках:
STUDENT_FULL_NAME — ПІБ, STUDENT_GROUP — номер групи, STUDENT_YEAR — курс навчання,
STUDENT_PROGRAMME — освітня програма. Кодування UTF-8.
Зміни файла діють після перезапуску сервера. Заповнений .env не публікується.

## 1. Локально в Linux або WSL

У каталозі стартера, з Python 3.10+ і venv:

```bash
bash run.sh
```

Відкрийте http://127.0.0.1:8000/ та зробіть перший скриншот.
Зупиніть сервер через Ctrl+C.

## 2. Vagrant / VirtualBox

На сумісному хості x86_64, у тому самому каталозі:

```bash
vagrant up
vagrant ssh
```

У гості:

```bash
cd ~/lab1
HOST=0.0.0.0 bash run.sh
```

Відкрийте на хості http://127.0.0.1:8080/ та зробіть другий скриншот.
Після виходу з гостя видаліть власну VM командою vagrant destroy.

## 3. AWS EC2

У Learner Lab створіть погоджений інстанс Ubuntu. У Security Group дозвольте
вхідні TCP 22 і TCP 8000 для всіх IPv4-адрес: джерело 0.0.0.0/0 (Anywhere-IPv4).
Через SCP передайте main.py,
envinfo.py, requirements.txt, run.sh та .env до ~/lab1.
У гості встановіть python3-venv та виконайте:

```bash
cd ~/lab1
HOST=0.0.0.0 bash run.sh
```

Відкрийте http://PUBLIC_IP:8000/, де PUBLIC_IP — публічна адреса інстанса.
Зробіть третій скриншот, завершіть сервер і видаліть власні ресурси EC2.

check.py та expected.txt залишаються допоміжними засобами розробника;
для звіту потрібна тільки сторінка GET / у кожному середовищі.
