#!/usr/bin/env python3
"""
Простой тест исправленного processor_rus.py
"""
import sys
import os

# Добавляем пути
sys.path.insert(0, '.')
sys.path.insert(0, 'backend')

def test_processor_rus():
    try:
        print("Тестируем импорт processor_rus...")
        import backend.processors.processor_rus as processor_rus
        print("✅ Импорт успешен")

        print("Проверяем функцию process...")
        if hasattr(processor_rus, 'process'):
            print("✅ Функция process найдена")
        else:
            print("❌ Функция process не найдена")
            return False

        print("✅ processor_rus.py работает корректно!")
        return True

    except SyntaxError as e:
        print(f"❌ SyntaxError: {e}")
        return False
    except IndentationError as e:
        print(f"❌ IndentationError: {e}")
        return False
    except Exception as e:
        print(f"❌ Другая ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Тест исправленного processor_rus.py")
    print("=" * 40)

    if test_processor_rus():
        print("🎉 ТЕСТ ПРОЙДЕН!")
        print("IndentationError и кодировка исправлены!")
    else:
        print("❌ Тест не пройден")

    print("=" * 40)
