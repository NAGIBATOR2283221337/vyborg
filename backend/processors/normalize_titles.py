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
    s = s.replace(' серия', '').replace(' выпуск', '').replace(' эпизод', '').replace(' часть', '')

    base, eps = s, set()

    # Ищем числа в конце строки (возможно разделенные запятыми, дефисами, пробелами)
    m = re.search(r'(\d[\d\s,\-]*)$', s)
    if m:
        base = s[:m.start()].strip().strip('.')
        tail = m.group(1)

        # Обрабатываем диапазоны (63-64)
        for tok in SEP.split(tail):
            if not tok:
                continue
            m2 = RANGE.fullmatch(tok)
            if m2:
                a, b = int(m2.group(1)), int(m2.group(2))
                for k in range(min(a, b), max(a, b) + 1):
                    eps.add(k)
            elif tok.isdigit():
                eps.add(int(tok))

    # Если ничего не нашли, возвращаем исходную базу и пустое множество
    return base.strip(), eps if eps else set()
