@echo off
cd /d "%~dp0"

echo Запуск сервера...
python -m uvicorn backend.main:app --port 8000

pause
