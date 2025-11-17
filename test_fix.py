"""Быстрый тест исправления ошибки форматирования."""
from backend.processors.shared import parse_time_from_str
from datetime import datetime
import pandas as pd
import numpy as np

print("="*60)
print("ТЕСТ ИСПРАВЛЕНИЯ: float и NaN атрибуты")
print("="*60)

# Создаём объект с float атрибутами (имитация проблемы)
class MockTime:
    def __init__(self, h, m):
        self.hour = h
        self.minute = m

# Тесты
test_cases = [
    (datetime(2025, 1, 1, 6, 30), "datetime(6, 30)"),
    (pd.Timestamp("2025-01-01 06:30:00"), "pd.Timestamp(6:30)"),
    (MockTime(6.0, 30.0), "MockTime(hour=6.0, minute=30.0) - float"),
    (MockTime(np.nan, 30), "MockTime(hour=NaN, minute=30) - NaN hour"),
    (MockTime(6, np.nan), "MockTime(hour=6, minute=NaN) - NaN minute"),
    (MockTime(np.nan, np.nan), "MockTime(hour=NaN, minute=NaN) - оба NaN"),
    ("6:30", "Строка '6:30'"),
    (0.25, "Excel 0.25 (6:00)"),
    (np.nan, "np.nan"),
]

print("\nПроверяем разные типы времени:\n")

for val, desc in test_cases:
    try:
        result = parse_time_from_str(val)
        if result:
            print(f"✅ {desc:45} → {result}")
        else:
            print(f"⚠️  {desc:45} → None (ожидаемо)")
    except Exception as e:
        print(f"❌ {desc:45} → ОШИБКА: {e}")

print("\n" + "="*60)
print("ТЕСТ ЗАВЕРШЁН")
print("="*60)
print("\nЕсли нет ❌ - все ошибки исправлены!")
print("⚠️ (None) - это нормально для невалидных данных")

