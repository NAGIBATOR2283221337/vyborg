@echo off
chcp 65001 >nul
echo ======================================
echo Запуск сервера с улучшенным алгоритмом
echo ======================================
echo.

cd /d "%~dp0"

echo Проверка импорта модулей...
python -c "from backend.processors import processor_rus, matcher; print('✅ Модули загружены успешно')"
if errorlevel 1 (
    echo ❌ Ошибка импорта модулей
    pause
    exit /b 1
)

echo.
echo Запуск сервера на http://localhost:8000
echo Для остановки нажмите Ctrl+C
echo.

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

pause

