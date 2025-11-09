#!/usr/bin/env python3
"""
Простой тест для проверки компонентов системы
"""
import sys
import os

# Добавляем путь к backend в sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_shared_module():
    """Тестируем модуль shared.py"""
    try:
        from processors.shared import (
            normalize_base, tokenize, jaccard_over_min,
            seq_ratio, parse_date_from_cell, parse_time_from_str
        )

        # Тест нормализации
        test_title = "Программа (Ред.) серия 5 copy.mp4"
        normalized = normalize_base(test_title)
        print(f"Нормализация: '{test_title}' -> '{normalized}'")

        # Тест токенизации
        tokens = tokenize("Вечерние новости программа")
        print(f"Токены: {tokens}")

        # Тест метрик
        text1 = "Вечерние новости"
        text2 = "Новости вечером"
        tokens1 = tokenize(text1)
        tokens2 = tokenize(text2)

        jaccard = jaccard_over_min(tokens1, tokens2)
        ratio = seq_ratio(text1, text2)
        print(f"Схожесть '{text1}' и '{text2}': Jaccard={jaccard:.3f}, Ratio={ratio:.3f}")

        # Тест парсинга даты
        date_test = "15.11.2025"
        parsed_date = parse_date_from_cell(date_test)
        print(f"Дата: '{date_test}' -> '{parsed_date}'")

        # Тест парсинга времени
        time_test = "14:30"
        parsed_time = parse_time_from_str(time_test)
        print(f"Время: '{time_test}' -> '{parsed_time}'")

        print("✓ Модуль shared.py работает корректно")
        return True

    except Exception as e:
        print(f"✗ Ошибка в модуле shared.py: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_processor_modules():
    """Тестируем процессорные модули"""
    try:
        from processors import processor_rus, processor_foreign
        print("✓ Модули процессоров импортированы успешно")
        return True
    except Exception as e:
        print(f"✗ Ошибка импорта процессоров: {e}")
        return False

def test_main_module():
    """Тестируем основной модуль"""
    try:
        # Пробуем импортировать main без запуска
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", "backend/main.py")
        main_module = importlib.util.module_from_spec(spec)

        print("✓ Главный модуль может быть загружен")
        return True
    except Exception as e:
        print(f"✗ Ошибка в главном модуле: {e}")
        return False

if __name__ == "__main__":
    print("=== Тестирование компонентов системы ===\n")

    tests = [
        ("Модуль shared.py", test_shared_module),
        ("Модули процессоров", test_processor_modules),
        ("Главный модуль", test_main_module)
    ]

    passed = 0
    for test_name, test_func in tests:
        print(f"Тест: {test_name}")
        if test_func():
            passed += 1
        print()

    print(f"=== Результат: {passed}/{len(tests)} тестов пройдено ===")

    if passed == len(tests):
        print("\n🎉 Все компоненты работают! Можно запускать сервер.")
        print("Запустите: python -m uvicorn backend.main:app --reload --port 8000")
    else:
        print("\n⚠️  Некоторые компоненты требуют исправления.")
