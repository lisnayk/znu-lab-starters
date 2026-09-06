@echo off
rem Запуск застосунку в Windows без WSL. Файл зберігати в UTF-8.
chcp 65001 >nul
setlocal
cd /d "%~dp0"
if "%HOST%"=="" set "HOST=127.0.0.1"
if "%PORT%"=="" set "PORT=8000"

set "PY=py -3"
where py >nul 2>&1 || set "PY=python"
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"
if errorlevel 1 (
  echo Потрiбен Python 3.10 або новiший. Встановiть його з python.org
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  %PY% -m venv .venv || (echo Не вдалося створити .venv & exit /b 1)
)
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt || exit /b 1

echo Паспорт середовища: http://%HOST%:%PORT% ; зупинка — Ctrl+C.
".venv\Scripts\python.exe" -m uvicorn main:app --host %HOST% --port %PORT%
