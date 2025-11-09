@echo off
chcp 65001 > nul
echo =======================================
echo  ОТЛАДКА НА ОСНОВЕ ВАШИХ СКРИНШОТОВ
echo =======================================

cd /d "%~dp0"

echo 📦 Проверка зависимостей...
pip install fastapi uvicorn pandas openpyxl python-multipart > nul 2>&1

echo.
echo 🔍 Запуск теста с вашими данными...
python test_user_data.py

echo.
pause
