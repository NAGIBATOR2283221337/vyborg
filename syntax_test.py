#!/usr/bin/env python3
"""
Простейший тест синтаксиса
"""
try:
    import sys
    sys.path.append('.')
    sys.path.append('backend')

    print("Тестируем импорт shared...")
    import backend.processors.shared
    print("✅ shared.py - OK")

    print("Тестируем импорт processor_rus...")
    import backend.processors.processor_rus
    print("✅ processor_rus.py - OK")

    print("Тестируем импорт main...")
    import backend.main
    print("✅ main.py - OK")

    print("\n🎉 ВСЕ ФАЙЛЫ СИНТАКСИЧЕСКИ КОРРЕКТНЫ!")
    print("IndentationError исправлена!")

except SyntaxError as e:
    print(f"❌ Синтаксическая ошибка: {e}")
except IndentationError as e:
    print(f"❌ Ошибка отступов: {e}")
except Exception as e:
    print(f"❌ Другая ошибка: {e}")
    import traceback
    traceback.print_exc()

