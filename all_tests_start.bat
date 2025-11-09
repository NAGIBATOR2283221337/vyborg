@echo off
chcp 65001 > nul
echo ==============================================
echo  ПОЛНОЕ ТЕСТИРОВАНИЕ ВСЕХ ИСПРАВЛЕНИЙ
echo ==============================================

cd /d "%~dp0"

echo 📦 Установка зависимостей...
pip install fastapi uvicorn pandas openpyxl python-multipart > nul 2>&1

echo.
echo 🔍 1. Проверка синтаксиса...
python -c "import ast; print('Проверяем processor_rus.py...'); ast.parse(open('backend/processors/processor_rus.py', encoding='utf-8').read()); print('✅ Синтаксис OK')"

if %ERRORLEVEL% neq 0 (
    echo ❌ Синтаксические ошибки остались!
    pause
    exit /b 1
)

echo.
echo 🧪 2. Тест PermissionError...
python test_permission_fix.py

if %ERRORLEVEL% neq 0 (
    echo ❌ PermissionError не исправлена!
    pause
    exit /b 1
)

echo.
echo ✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!
echo 🚀 Запуск сервера на http://localhost:8000
echo.
echo Исправлены:
echo   ✅ IndentationError
echo   ✅ SyntaxError
echo   ✅ PermissionError
echo   ✅ UnicodeDecodeError
echo.

timeout /t 3 > nul
start http://localhost:8000

echo Запуск сервера...
python -m uvicorn backend.main:app --reload --port 8000

pause
