@echo off
echo Запуск тестового сервера...
cd /d "%~dp0"

pip install fastapi uvicorn python-multipart > nul 2>&1

echo Тестовый сервер запускается на http://localhost:8000
echo.
timeout /t 2 > nul
start http://localhost:8000

python test_server.py

pause
