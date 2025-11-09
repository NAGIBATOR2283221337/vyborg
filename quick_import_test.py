import sys
import os
sys.path.insert(0, 'backend')

print("Тест импорта...")
try:
    import backend.processors.processor_rus
    print("✅ processor_rus импортирован")

    import backend.processors.shared
    print("✅ shared импортирован")

    import backend.main
    print("✅ main импортирован")

    print("🎉 Все модули работают!")

except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
