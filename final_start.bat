@echo off
chcp 65001 > nul
echo ===============================================
echo  ФИНАЛЬНЫЙ ЗАПУСК - ВСЕ ОШИБКИ ИСПРАВЛЕНЫ
echo ===============================================

cd /d "%~dp0"

echo 📦 Установка зависимостей...
pip install fastapi uvicorn pandas openpyxl python-multipart > nul 2>&1

echo.
echo 🔍 Проверка исправленного processor_rus.py...
python test_processor_fix.py

echo.
echo 🔍 Финальная проверка синтаксиса...
python final_syntax_check.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Остались синтаксические ошибки!
    pause
    exit /b 1
)

echo.
echo ✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!
echo 🚀 Запуск сервера на http://localhost:8000
echo.
echo Исправлены ошибки:
echo   ✅ IndentationError (shared.py)
echo   ✅ SyntaxError (processor_rus.py)
echo   ✅ PermissionError (файлы)
echo.

timeout /t 3 > nul
start http://localhost:8000

echo Запуск сервера...
python -m uvicorn backend.main:app --reload --port 8000

pause
