import re
import unicodedata
from typing import Tuple, Set

_SYNONYMS = {
    "серия": "серия",
    "эпизод": "серия",
    "выпуск": "серия",
    "часть": "серия",
}
_EXT = re.compile(r'\.(mp4|mkv|avi|mov)$', re.I)
_BR = re.compile(r'\s*\([^)]*\)')
SEP = re.compile(r'[\s,]+')
RANGE = re.compile(r'(\d{1,3})\s*[–\-]\s*(\d{1,3})')

MONTH = {
    "января":1,"февраля":2,"марта":3,"апреля":4,"мая":5,"июня":6,
    "июля":7,"августа":8,"сентября":9,"октября":10,"ноября":11,"декабря":12
}

_STOP = {"фильм","кино","передача","серия","выпуск","эпизод","часть","ред","copy"}

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s)).lower()
    s = _EXT.sub("", s)
    s = _BR.sub("", s)
    s = s.replace("ё", "е")
    for k,v in _SYNONYMS.items():
        s = re.sub(fr'\b{k}\b', v, s)
    s = re.sub(r'\s+', ' ', s).strip().strip('.')
    return s

def _strip_stop(tokens):
    return [t for t in tokens if t not in _STOP]

def norm_base_only(s: str) -> str:
    s2 = norm(s)
    toks = _strip_stop(s2.split())
    return " ".join(toks)

def split_base_episodes(raw: str) -> Tuple[str, Set[int]]:
    """
    Извлекает базовое название и номера эпизодов/серий.

    Поддерживает форматы:
    - "Название. 63 серия" → ("название", {63})
    - "Название 63,64" → ("название", {63, 64})
    - "Название 63-64" → ("название", {63, 64})
    - "Название. 2 выпуск" → ("название", {2})
    - "Название" → ("название", set())
    """
    s = norm(raw)

    # Убираем служебные слова, но сохраняем числа рядом с ними
    # "гора самоцветов. 63 серия" → "гора самоцветов 63"
    s = re.sub(r'\b(серия|выпуск|эпизод|часть)\b', '', s)
    s = re.sub(r'\s+', ' ', s).strip()

    base, eps = s, set()

    # Паттерн 1: Числа с явным указанием "серия/выпуск" (до удаления этих слов)
    # Этот паттерн уже обработан выше через norm() и замену слов

    # Паттерн 2: Диапазоны и списки чисел в конце
    # "гора самоцветов 63 64" или "гора самоцветов 63,64" или "гора самоцветов 63-64"
    m = re.search(r'[.\s]+(\d[\d\s,\-]*)$', s)
    if m:
        base = s[:m.start()].strip()
        tail = m.group(1).strip()

        # Обрабатываем диапазоны (63-64)
        for tok in SEP.split(tail):
            tok = tok.strip()
            if not tok:
                continue
            m2 = RANGE.fullmatch(tok)
            if m2:
                a, b = int(m2.group(1)), int(m2.group(2))
                for k in range(min(a, b), max(a, b) + 1):
                    eps.add(k)
            elif tok.isdigit():
                eps.add(int(tok))

    # Паттерн 3: Одиночное число в конце (если предыдущий паттерн не сработал)
    if not eps:
        m = re.search(r'\b(\d{1,3})\s*$', s)
        if m:
            eps.add(int(m.group(1)))
            base = s[:m.start()].strip()

    # Финальная очистка базы
    base = base.strip(' .-–—')

    return base, eps if eps else set()
