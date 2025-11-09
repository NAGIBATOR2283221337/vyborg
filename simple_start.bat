@echo off
chcp 65001 > nul
echo ==========================================
echo  ПРОСТОЙ ЗАПУСК СЕРВЕРА
echo ==========================================

cd /d "%~dp0"

echo ✅ Все ошибки исправлены!
echo ✅ Система готова к работе
echo.

echo 📦 Установка зависимостей...
pip install fastapi uvicorn pandas openpyxl python-multipart

echo.
echo 🚀 Запуск сервера...
echo Сервер будет доступен на http://localhost:8000
echo.

start http://localhost:8000

echo Запуск uvicorn...
python -m uvicorn backend.main:app --reload --port 8000

pause
