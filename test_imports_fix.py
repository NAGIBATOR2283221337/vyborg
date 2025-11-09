#!/usr/bin/env python3
"""
Быстрый тест импортов для отладки
"""
import sys
import os
from pathlib import Path

# Добавляем пути
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "backend"))

print("Текущая директория:", current_dir)
print("Python пути:", sys.path[:3])

try:
    print("1. Тестируем импорт FastAPI...")
    from fastapi import FastAPI
    print("✅ FastAPI OK")

    print("2. Тестируем импорт shared...")
    from backend.processors.shared import normalize_base
    print("✅ shared OK")

    print("3. Тестируем импорт processor_rus...")
    from backend.processors.processor_rus import process
    print("✅ processor_rus OK")

    print("4. Тестируем импорт main...")
    from backend.main import app
    print("✅ main OK")

    print("\n🎉 Все импорты работают!")

except Exception as e:
    print(f"❌ Ошибка импорта: {e}")
    import traceback
    traceback.print_exc()
