@echo off
chcp 65001 > nul
echo ========================================
echo    Быстрый запуск сервера (без venv)
echo ========================================

cd /d "%~dp0"

echo Установка зависимостей...
pip install fastapi uvicorn pandas openpyxl python-multipart

echo.
echo Тестирование импортов...
python test_imports_fix.py

if %ERRORLEVEL% neq 0 (
    echo ❌ Проблемы с импортами
    pause
    exit /b 1
)

echo.
echo ✅ Запуск сервера на http://localhost:8000
echo.

timeout /t 2 /nobreak > nul
start http://localhost:8000

python -m uvicorn backend.main:app --reload --port 8000

pause
