#!/usr/bin/env python3
"""
Диагностика проблемы сопоставления - почему отчет не заполняется
"""
import sys
sys.path.append('.')
sys.path.append('backend')

def test_matching():
    print("🔍 ДИАГНОСТИКА СОПОСТАВЛЕНИЯ")
    print("=" * 50)

    try:
        from backend.processors.shared import normalize_base, tokenize, jaccard_over_min, seq_ratio

        # Тестовые данные из ваших скриншотов
        schedule_items = [
            "Заставка СМИ",
            "Заставка Доброе утро!",
            "Гора самоцветов 61, 62",
            "Заставка Реклама",
            "Реклама",
            "Повтор",
            "Гора самоцветов 63, 64"
        ]

        report_items = [
            "Заставка СМИ",
            "Гора самоцветов",
            "Реклама программа"
        ]

        print("📊 ТЕСТ СОПОСТАВЛЕНИЯ:")
        print()

        for report_item in report_items:
            print(f"🎯 Ищем совпадения для: '{report_item}'")

            # Нормализуем элемент из отчета
            report_norm = normalize_base(report_item)
            report_tokens = tokenize(report_norm)

            print(f"   Нормализовано: '{report_norm}'")
            print(f"   Токены: {report_tokens}")

            best_match = None
            best_score = 0

            for schedule_item in schedule_items:
                schedule_norm = normalize_base(schedule_item)
                schedule_tokens = tokenize(schedule_norm)

                # Вычисляем метрики
                overlap = jaccard_over_min(report_tokens, schedule_tokens)
                ratio = seq_ratio(report_norm, schedule_norm)

                score = max(overlap, ratio)

                print(f"     vs '{schedule_item}' -> '{schedule_norm}'")
                print(f"        Токены: {schedule_tokens}")
                print(f"        Overlap: {overlap:.3f}, Ratio: {ratio:.3f}, Score: {score:.3f}")

                if score > best_score:
                    best_score = score
                    best_match = schedule_item

                # Проверяем пороги
                if ratio >= 0.05 or overlap >= 0.10:
                    print(f"        ✅ ПРОХОДИТ ПОРОГИ (0.05/0.10)")
                else:
                    print(f"        ❌ НЕ ПРОХОДИТ ПОРОГИ")

            print(f"   🏆 Лучшее совпадение: '{best_match}' (score: {best_score:.3f})")
            print()

        print("✅ Диагностика завершена")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_matching()
