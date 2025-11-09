#!/usr/bin/env python3
"""
Простой тест для определения причины проблемы
"""
import sys
import os
sys.path.insert(0, '.')
sys.path.insert(0, 'backend')

def simple_test():
    print("🔍 Простой тест импортов и функций")

    try:
        # Проверяем shared.py
        print("1. Импорт shared...")
        from backend.processors.shared import normalize_base, find_headers_any
        print("✅ shared импортирован")

        # Тестируем нормализацию
        test_title = "Гора самоцветов 61, 62"
        normalized = normalize_base(test_title)
        print(f"2. Нормализация: '{test_title}' -> '{normalized}'")

        # Проверяем processor_rus
        print("3. Импорт processor_rus...")
        from backend.processors.processor_rus import process
        print("✅ processor_rus импортирован")

        print("\n🎉 Базовые функции работают!")
        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    simple_test()
