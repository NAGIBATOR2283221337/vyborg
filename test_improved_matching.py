"""
Тест улучшенного алгоритма сопоставления
"""
import logging
from backend.processors.normalize_titles import split_base_episodes, norm_base_only
from backend.processors.matcher import best_candidates, pick_showtimes_for_report_title
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def test_normalization():
    """Тестируем нормализацию названий"""
    print("\n" + "="*60)
    print("ТЕСТ 1: Нормализация названий")
    print("="*60)

    test_cases = [
        ("Дикие и стильные. 2 выпуск", ("дикие стильные", {2})),
        ("Гора самоцветов. 63 серия", ("гора самоцветов", {63})),
        ("Гора самоцветов 63,64", ("гора самоцветов", {63, 64})),
        ("18 лун", ("18 лун", set())),
        ("Авангаристы", ("авангаристы", set())),
        ("Бабоньки", ("бабоньки", set())),
        ("БЕСЦЕННАЯ ЛЮБОВЬ 4 серия", ("бесценная любовь", {4})),
    ]

    for raw, expected in test_cases:
        base, eps = split_base_episodes(raw)
        normalized = norm_base_only(base)
        status = "✅" if (base, eps) == expected else "❌"
        print(f"{status} '{raw}'")
        print(f"   → база: '{base}', эпизоды: {eps}")
        if base != expected[0]:
            print(f"   ⚠️  Ожидалось: '{expected[0]}'")
        if eps != expected[1]:
            print(f"   ⚠️  Ожидалось: {expected[1]}")


def test_matching():
    """Тестируем алгоритм сопоставления"""
    print("\n" + "="*60)
    print("ТЕСТ 2: Алгоритм сопоставления")
    print("="*60)

    # Создаем тестовый индекс сетки
    schedule_index = {
        ("дикие стильные", frozenset([2])): [datetime(2025, 9, 1, 6, 0)],
        ("дикие стильные", frozenset([3])): [datetime(2025, 9, 1, 7, 0)],
        ("гора самоцветов", frozenset([63])): [datetime(2025, 9, 1, 8, 0)],
        ("гора самоцветов", frozenset([64])): [datetime(2025, 9, 1, 9, 0)],
        ("18 лун", frozenset(["__NOSER__"])): [
            datetime(2025, 9, 4, 6, 0),
            datetime(2025, 9, 5, 6, 0),
        ],
        ("авангаристы", frozenset(["__NOSER__"])): [
            datetime(2025, 9, 7, 10, 30),
        ],
        ("бабоньки", frozenset(["__NOSER__"])): [datetime(2025, 9, 5, 12, 0)],
        ("бесценная любовь", frozenset([4])): [datetime(2025, 9, 1, 22, 17)],
    }

    test_cases = [
        ("Дикие и стильные. 2 выпуск", True),
        ("Гора самоцветов. 63 серия", True),
        ("18 лун", True),
        ("Авангаристы", True),
        ("Бабоньки", True),
        ("БЕСЦЕННАЯ ЛЮБОВЬ 4 серия", True),
        ("Несуществующая передача 999", False),  # Не должна найтись
    ]

    for title, should_match in test_cases:
        result = pick_showtimes_for_report_title(title, schedule_index)
        matched = len(result) > 0

        if matched == should_match:
            status = "✅"
        else:
            status = "❌"

        print(f"{status} '{title}'")
        if result:
            print(f"   → Найдено показов: {len(result)}")
            for dt in result:
                print(f"      • {dt.strftime('%d.%m.%Y в %H:%M')}")
        else:
            print(f"   → Не найдено")


def test_fuzzy_matching():
    """Тестируем нечёткое сопоставление"""
    print("\n" + "="*60)
    print("ТЕСТ 3: Нечёткое сопоставление")
    print("="*60)

    schedule_index = {
        ("гора самоцветов", frozenset([63])): [datetime(2025, 9, 1, 8, 0)],
        ("новости", frozenset(["__NOSER__"])): [
            datetime(2025, 9, 1, 6, 0),
            datetime(2025, 9, 1, 7, 0),
        ],
    }

    # Тестируем разные варианты написания
    test_cases = [
        "Гора самоцветов (ред.) 63 серия",  # С пометкой (ред.)
        "гора самоцветов - 63 серия",  # С дефисом
        "Гора самоцветов. 63 выпуск",  # "выпуск" вместо "серия"
        "НОВОСТИ",  # Заглавные буквы
        "Новости (copy 1)",  # С пометкой
    ]

    for title in test_cases:
        result = pick_showtimes_for_report_title(title, schedule_index)
        status = "✅" if result else "❌"
        print(f"{status} '{title}' → {len(result)} показов")


if __name__ == "__main__":
    test_normalization()
    test_matching()
    test_fuzzy_matching()

    print("\n" + "="*60)
    print("Тесты завершены!")
    print("="*60)

