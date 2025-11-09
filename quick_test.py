print("🔍 Простой тест системы")

try:
    # Тест нормализации
    import sys
    sys.path.append('backend')
    from backend.processors.shared import normalize_base

    print("✅ Функция нормализации импортирована")

    # Тестируем на ваших данных
    test_data = [
        "Гора самоцветов 61, 62",
        "Заставка СМИ",
        "Реклама"
    ]

    for title in test_data:
        result = normalize_base(title)
        print(f"'{title}' -> '{result}'")

    print("✅ Нормализация работает")

except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
