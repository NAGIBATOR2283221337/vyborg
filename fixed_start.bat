@echo off
chcp 65001 > nul
echo ========================================
echo  ИСПРАВЛЕННЫЙ ЗАПУСК СЕРВЕРА
echo ========================================

cd /d "%~dp0"

echo 📦 Установка зависимостей...
pip install fastapi uvicorn pandas openpyxl python-multipart

echo.
echo 🧪 Проверка синтаксиса и отступов...
python syntax_test.py

if %ERRORLEVEL% neq 0 (
    echo ❌ Проверка не пройдена
    pause
    exit /b 1
)

echo.
echo ✅ Все исправления применены!
echo 🚀 Запуск сервера на http://localhost:8000
echo.
echo ВАЖНО: Ошибка WinError 32 должна быть исправлена!
echo.

timeout /t 3 > nul
start http://localhost:8000

python -m uvicorn backend.main:app --reload --port 8000

pause
