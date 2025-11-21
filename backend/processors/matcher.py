from typing import Dict, Tuple, List, Iterable, Set
from datetime import datetime
from rapidfuzz import fuzz
import logging

from .normalize_titles import split_base_episodes, norm_base_only
from .settings_match import BASE_RATIO, PARTIAL_RATIO, TOKEN_SET, JACCARD_MIN, ALLOW_EPISODE_PARTIAL, MAX_CANDIDATES, ALLOW_CONTAINS, ALLOW_PARTIAL_WORDS

logger = logging.getLogger(__name__)


def _tokens(s: str) -> Set[str]:
    """Разбивает строку на множество токенов."""
    return set(s.split())


def _jaccard(a: str, b: str) -> float:
    """Вычисляет коэффициент Жаккара для двух строк."""
    A, B = _tokens(a), _tokens(b)
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)


def _word_overlap_ratio(a: str, b: str) -> float:
    """Проверяет, какая часть слов из более короткой строки есть в более длинной."""
    A, B = _tokens(a), _tokens(b)
    if not A or not B:
        return 0.0
    shorter, longer = (A, B) if len(A) <= len(B) else (B, A)
    return len(shorter & longer) / len(shorter)


def _partial_word_match(a: str, b: str) -> float:
    """Проверяет частичное совпадение слов (подстроки)."""
    if not ALLOW_PARTIAL_WORDS:
        return 0.0

    words_a = _tokens(a)
    words_b = _tokens(b)

    matches = 0
    total = len(words_a) + len(words_b)

    for wa in words_a:
        for wb in words_b:
            # Если одно слово содержится в другом
            if len(wa) >= 4 and len(wb) >= 4:  # Только для слов длиной >= 4
                if wa in wb or wb in wa:
                    matches += 2
                    break

    return matches / max(1, total) if total > 0 else 0.0


def best_candidates(report_title: str, schedule_keys: Iterable[Tuple[str, frozenset]]) -> Tuple[List[Tuple[str,frozenset]], List[int]]:
    """Находит лучшие кандидаты для сопоставления с использованием множества метрик."""
    base_r, eps_r = split_base_episodes(report_title)
    base_r0 = norm_base_only(base_r)

    if not base_r0:
        logger.warning(f"Пустая база после нормализации: '{report_title}'")
        return [], list(eps_r)

    scored = []

    for base_s, eps_s in schedule_keys:
        base_s0 = norm_base_only(base_s)

        if not base_s0:
            continue

        # Множество метрик для сопоставления
        r1 = fuzz.ratio(base_r0, base_s0)              # Общее сходство
        r2 = fuzz.partial_ratio(base_r0, base_s0)       # Частичное совпадение
        r3 = fuzz.token_set_ratio(base_r0, base_s0)     # Совпадение множества токенов
        r4 = fuzz.token_sort_ratio(base_r0, base_s0)    # Совпадение с сортировкой токенов

        jac = _jaccard(base_r0, base_s0)                # Коэффициент Жаккара
        overlap = _word_overlap_ratio(base_r0, base_s0) # Перекрытие слов
        partial = _partial_word_match(base_r0, base_s0) # Частичное совпадение слов

        # Проверяем различные критерии
        ok = False
        boost = 0

        # Критерий 1: Высокие показатели по основным метрикам
        if r1 >= BASE_RATIO or r2 >= PARTIAL_RATIO or r3 >= TOKEN_SET or r4 >= TOKEN_SET:
            ok = True

        # Критерий 2: Коэффициент Жаккара
        if jac >= JACCARD_MIN:
            ok = True
            boost += 5

        # Критерий 3: Хорошее перекрытие слов
        if overlap >= 0.6:
            ok = True
            boost += 10

        # Критерий 4: Частичное совпадение слов
        if partial >= 0.3:
            ok = True
            boost += 5

        # Критерий 5: Подстрока (очень сильный критерий)
        if ALLOW_CONTAINS:
            if base_r0 in base_s0 or base_s0 in base_r0:
                ok = True
                r2 = max(r2, 95)
                boost += 20

        if ok:
            # Комплексная оценка с учетом всех метрик
            score = (
                max(r1, r2, r3, r4) * 1.0 +  # Максимальная из базовых метрик
                jac * 30 +                    # Жаккар (0-30)
                overlap * 20 +                # Перекрытие слов (0-20)
                partial * 15 +                # Частичное совпадение (0-15)
                boost                         # Бонусы
            )

            scored.append((score, base_s, eps_s, {
                'ratio': r1,
                'partial': r2,
                'token_set': r3,
                'jaccard': jac,
                'overlap': overlap,
                'partial_word': partial
            }))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Логируем топ-3 кандидата для отладки
    if scored and logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"\n🔍 Топ кандидатов для '{report_title}':")
        for i, (score, base, eps, metrics) in enumerate(scored[:3], 1):
            logger.debug(f"  {i}. [{score:.1f}] '{base}' eps={eps}")
            logger.debug(f"     Метрики: ratio={metrics['ratio']:.0f}, partial={metrics['partial']:.0f}, "
                        f"jac={metrics['jaccard']:.2f}, overlap={metrics['overlap']:.2f}")

    return [(b, e) for score, b, e, _ in scored[:MAX_CANDIDATES]], list(eps_r)


def pick_showtimes_for_report_title(title: str, index: Dict[Tuple[str, frozenset], List[datetime]]) -> List[datetime]:
    """
    Подбирает время показа для названия передачи с использованием каскадных стратегий:
    1. Точное совпадение по базе и конкретному эпизоду
    2. Частичное пересечение эпизодов (если включено ALLOW_EPISODE_PARTIAL)
    3. Совпадение по базе без эпизодов (-1)
    4. Топ-кандидат независимо от эпизодов (fallback)

    ВАЖНО: -1 в frozenset означает программу без серий (новости, заставки и т.п.)
    """
    cands, eps_r = best_candidates(title, index.keys())

    if not cands:
        logger.debug(f"❌ Нет кандидатов для '{title}'")
        return []

    eps_r_set = set(eps_r) if eps_r else set()
    has_episodes = bool(eps_r_set and eps_r_set != {-1})

    logger.debug(f"🔍 Ищу показы для '{title}': episodes={eps_r_set}, кандидатов={len(cands)}")

    # Стратегия 1: Точное совпадение базы и КОНКРЕТНОГО эпизода
    if has_episodes:
        for ep in eps_r_set:
            # Ищем ключ с одним конкретным эпизодом
            target_key_single = frozenset([ep])

            for b, e in cands:
                if e == target_key_single:
                    logger.debug(f"✅ Точное совпадение эпизода {ep}: '{title}' → '{b}' eps={e}")
                    return index[(b, e)]

            logger.debug(f"   Не найдено точное совпадение для эпизода {ep}")

    # Стратегия 2: Частичное пересечение эпизодов
    # Ищем среди топовых кандидатов те, у которых есть нужные эпизоды
    if ALLOW_EPISODE_PARTIAL and has_episodes:
        out = []
        matched_keys = []

        for b, e in cands:
            # Пропускаем программы без серий
            if -1 in e:
                continue

            # Проверяем пересечение эпизодов
            intersection = set(e) & eps_r_set
            if intersection:
                out.extend(index[(b, e)])
                matched_keys.append((b, e))
                logger.debug(f"   Совпадение эпизодов: база='{b}', эпизоды в сетке={e}, искомые={eps_r_set}, пересечение={intersection}")

        if out:
            logger.debug(f"✅ Найдено по эпизодам: '{title}' → {matched_keys}")
            return sorted(set(out))

    # Стратегия 3: Совпадение по базе без учета эпизодов (для передач без серий)
    if not has_episodes or eps_r_set == {-1}:
        for b, e in cands:
            if e == frozenset([-1]):
                logger.debug(f"✅ Совпадение без эпизодов: '{title}' → '{b}'")
                return index[(b, e)]

    # Стратегия 4: НЕ используем fallback для многосерийных программ!
    # Это предотвращает неправильное сопоставление разных серий
    if has_episodes:
        logger.debug(f"❌ Не найдено точных совпадений для '{title}' с эпизодами {eps_r_set}")
        return []

    # Fallback только для программ без серий
    if cands:
        b, e = cands[0]
        logger.debug(f"⚠️ Fallback (без серий): '{title}' → '{b}' eps={e}")
        return index[(b, e)]

    logger.debug(f"❌ Не найдено совпадений для '{title}'")
    return []


