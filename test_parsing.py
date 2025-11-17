"""Быстрый тест парсинга времени и дат."""
from backend.processors.shared import parse_time_from_str, parse_date_label_ru

print("="*60)
print("ТЕСТ ПАРСИНГА ВРЕМЕНИ")
print("="*60)

test_times = [
    ("6:00", "Строка HH:MM"),
    ("06:00:00", "Строка HH:MM:SS"),
    (0.25, "Excel число 0.25 (6:00)"),
    (0.5, "Excel число 0.5 (12:00)"),
    (6.0, "Число 6 (6 часов)"),
    (6, "Целое 6"),
    ("6", "Строка '6'"),
    ("12:30", "12:30"),
    (None, "None"),
    ("invalid", "Невалидная строка"),
]

for val, desc in test_times:
    result = parse_time_from_str(val)
    status = "✅" if result else "❌"
    print(f"{status} {desc:30} → {result}")

print("\n" + "="*60)
print("ТЕСТ ПАРСИНГА ДАТ")
print("="*60)

test_dates = [
    ("1 сентября 2025", "Текстовая дата"),
    ("Понедельник, 1 сентября 2025", "С днём недели"),
    ("01.09.2025", "Числовая DD.MM.YYYY"),
    ("1.9.2025", "Без ведущих нулей"),
    ("01.09.25", "Короткий год"),
    ("invalid", "Невалидная строка"),
]

for val, desc in test_dates:
    result = parse_date_label_ru(val)
    status = "✅" if result else "❌"
    print(f"{status} {desc:30} → {result}")

print("\n" + "="*60)
print("ТЕСТ ЗАВЕРШЁН")
print("="*60)

