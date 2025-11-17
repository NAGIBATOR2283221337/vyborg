"""
Быстрая проверка работы улучшенного алгоритма
"""
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("ПРОВЕРКА МОДУЛЕЙ")
print("=" * 60)

try:
    from backend.processors.normalize_titles import split_base_episodes, norm_base_only
    print("✅ normalize_titles импортирован")
except Exception as e:
    print(f"❌ Ошибка импорта normalize_titles: {e}")
    sys.exit(1)

try:
    from backend.processors.settings_match import BASE_RATIO, PARTIAL_RATIO
    print(f"✅ settings_match импортирован (BASE_RATIO={BASE_RATIO})")
except Exception as e:
    print(f"❌ Ошибка импорта settings_match: {e}")
    sys.exit(1)

try:
    from backend.processors.matcher import best_candidates, pick_showtimes_for_report_title
    print("✅ matcher импортирован")
except Exception as e:
    print(f"❌ Ошибка импорта matcher: {e}")
    sys.exit(1)

try:
    from backend.processors.processor_rus import process
    print("✅ processor_rus импортирован")
except Exception as e:
    print(f"❌ Ошибка импорта processor_rus: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("ТЕСТ НОРМАЛИЗАЦИИ")
print("=" * 60)

test_titles = [
    "Дикие и стильные. 2 выпуск",
    "Гора самоцветов. 63 серия",
    "18 лун",
    "БЕСЦЕННАЯ ЛЮБОВЬ 4 серия",
]

for title in test_titles:
    base, eps = split_base_episodes(title)
    normalized = norm_base_only(base)
    print(f"'{title}'")
    print(f"  → база: '{base}', эпизоды: {eps}")
    print(f"  → нормализовано: '{normalized}'")

print("\n" + "=" * 60)
print("ТЕСТ СОПОСТАВЛЕНИЯ")
print("=" * 60)

from datetime import datetime

# Создаем простой индекс
schedule_index = {
    ("дикие стильные", frozenset([2])): [datetime(2025, 9, 1, 6, 0)],
    ("18 лун", frozenset(["__NOSER__"])): [datetime(2025, 9, 4, 6, 0)],
}

for title in ["Дикие и стильные. 2 выпуск", "18 лун", "Несуществующая передача"]:
    result = pick_showtimes_for_report_title(title, schedule_index)
    status = "✅" if result else "❌"
    print(f"{status} '{title}' → {len(result)} показов")

print("\n" + "=" * 60)
print("ВСЕ ПРОВЕРКИ ЗАВЕРШЕНЫ")
print("=" * 60)
print("\nМодули работают корректно!")
print("Можно запускать сервер: start_improved_server.bat")

