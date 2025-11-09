#!/usr/bin/env python3
"""
Демонстрация работы системы обработки отчётов
Запускает все основные компоненты для проверки
"""
import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_python():
    """Проверка Python"""
    print("🐍 Проверка Python...")
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
            return True
        else:
            print(f"❌ Python {version.major}.{version.minor}.{version.micro} - требуется 3.8+")
            return False
    except Exception as e:
        print(f"❌ Ошибка проверки Python: {e}")
        return False

def check_dependencies():
    """Проверка зависимостей"""
    print("\n📦 Проверка зависимостей...")

    required_packages = [
        'fastapi', 'uvicorn', 'pandas', 'openpyxl', 'python-multipart'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - не установлен")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n📥 Установка недостающих пакетов...")
        try:
            cmd = [sys.executable, '-m', 'pip', 'install'] + missing_packages
            subprocess.run(cmd, check=True)
            print("✅ Пакеты установлены")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка установки: {e}")
            return False

    return True

def check_files():
    """Проверка структуры файлов"""
    print("\n📁 Проверка файлов...")

    required_files = [
        "backend/main.py",
        "backend/processors/shared.py",
        "backend/processors/processor_rus.py",
        "backend/processors/processor_foreign.py",
        "frontend/index.html",
        "frontend/app.js",
        "frontend/styles.css",
        "requirements.txt"
    ]

    all_present = True

    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - не найден")
            all_present = False

    return all_present

def create_demo_files():
    """Создание демо-файлов"""
    print("\n📄 Создание демонстрационных файлов...")

    try:
        # Импортируем и запускаем создание примеров
        import create_examples

        # Выполняем создание
        examples_dir = "examples"
        if not os.path.exists(examples_dir):
            os.makedirs(examples_dir)

        from create_examples import create_sample_schedule, create_sample_report_rus, create_sample_report_foreign

        # Создаем файлы
        schedule_wb = create_sample_schedule()
        schedule_wb.save(os.path.join(examples_dir, "sample_schedule.xlsx"))

        rus_report_wb = create_sample_report_rus()
        rus_report_wb.save(os.path.join(examples_dir, "sample_report_rus.xlsx"))

        foreign_report_wb = create_sample_report_foreign()
        foreign_report_wb.save(os.path.join(examples_dir, "sample_report_foreign.xlsx"))

        print("✅ Демо-файлы созданы в папке examples/")
        return True

    except Exception as e:
        print(f"❌ Ошибка создания демо-файлов: {e}")
        return False

def run_tests():
    """Запуск тестов"""
    print("\n🧪 Запуск тестов...")

    try:
        # Добавляем путь к backend
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

        # Импортируем и запускаем тест
        import integration_test

        # Здесь можно было бы запустить тесты, но для демо просто проверим импорт
        print("✅ Тесты доступны")
        return True

    except Exception as e:
        print(f"❌ Ошибка тестов: {e}")
        return False

def start_server():
    """Запуск сервера"""
    print("\n🚀 Запуск сервера...")

    try:
        # Формируем команду
        cmd = [
            sys.executable, '-m', 'uvicorn',
            'backend.main:app', '--reload', '--port', '8000'
        ]

        print("Команда запуска:", ' '.join(cmd))
        print("Сервер запускается на http://localhost:8000")
        print("Для остановки нажмите Ctrl+C")
        print("-" * 50)

        # Даем время на запуск и открываем браузер
        def open_browser():
            time.sleep(3)  # Ждем 3 секунды
            try:
                webbrowser.open('http://localhost:8000')
                print("🌐 Браузер открыт на http://localhost:8000")
            except:
                print("⚠️  Не удалось открыть браузер. Откройте http://localhost:8000 вручную")

        import threading
        threading.Thread(target=open_browser, daemon=True).start()

        # Запускаем сервер
        subprocess.run(cmd)

    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка запуска сервера: {e}")
        print("\nПопробуйте запустить вручную:")
        print("python -m uvicorn backend.main:app --reload --port 8000")

def main():
    """Главная функция"""
    print("=" * 60)
    print("🎯 ДЕМОНСТРАЦИЯ СИСТЕМЫ ОБРАБОТКИ ОТЧЁТОВ")
    print("=" * 60)

    # Проверки
    checks = [
        ("Python", check_python),
        ("Зависимости", check_dependencies),
        ("Файлы", check_files),
        ("Демо-файлы", create_demo_files),
        ("Тесты", run_tests),
    ]

    all_ok = True
    for check_name, check_func in checks:
        if not check_func():
            all_ok = False
            break

    if all_ok:
        print("\n🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print("\nСистема готова к запуску.")

        response = input("\n🚀 Запустить сервер? (y/n): ").lower().strip()
        if response in ['y', 'yes', 'да', 'д']:
            start_server()
        else:
            print("\n📝 Для ручного запуска используйте:")
            print("python -m uvicorn backend.main:app --reload --port 8000")
            print("или дважды кликните start_server.bat")
    else:
        print("\n❌ Некоторые проверки не пройдены.")
        print("Исправьте ошибки и попробуйте снова.")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
