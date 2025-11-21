"""Тест извлечения серий из названий."""
import sys
from pathlib import Path

# Добавляем backend в путь
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from processors.normalize_titles import split_base_episodes, norm_base_only

# Тестовые случаи
test_cases = [
    ("Гора самоцветов. 63 серия", "гора самоцветов", {63}),
    ("Гора самоцветов. 64 серия", "гора самоцветов", {64}),
    ("Гора самоцветов 63,64", "гора самоцветов", {63, 64}),
    ("Гора самоцветов 63-64", "гора самоцветов", {63, 64}),
    ("Гора самоцветов. 2 выпуск", "гора самоцветов", {2}),
    ("Новости", "новости", set()),
    ("Дикие и стильные. 2 выпуск", "дикие и стильные", {2}),
    ("Дикие и стильные. 3 выпуск", "дикие и стильные", {3}),
    ("Мультфильм 1", "мультфильм", {1}),
]

print("=" * 80)
print("ТЕСТ ИЗВЛЕЧЕНИЯ СЕРИЙ")
print("=" * 80)

all_passed = True

for raw, expected_base, expected_eps in test_cases:
    base, eps = split_base_episodes(raw)
    base_norm = norm_base_only(base)

    passed = base == expected_base and eps == expected_eps

    status = "✅" if passed else "❌"
    print(f"\n{status} '{raw}'")
    print(f"   База:    '{base}' (ожидалось '{expected_base}')")
    print(f"   Норм:    '{base_norm}'")
    print(f"   Серии:   {eps} (ожидалось {expected_eps})")

    if not passed:
        all_passed = False

print("\n" + "=" * 80)
if all_passed:
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
else:
    print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
print("=" * 80)

