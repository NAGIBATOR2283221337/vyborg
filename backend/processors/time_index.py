from __future__ import annotations
import re
from datetime import datetime, date, time
from typing import Dict, List, Optional, Tuple, Iterable, Any
import pandas as pd
from .normalize_titles import norm_text, split_base_and_episodes, MONTH

RE_DATE_HEADER = re.compile(r'(\d{1,2})\s+([А-Яа-яЁё]+)\s+(\d{4})')  # '1 сентября 2025'


def parse_header_date(cell: str) -> Optional[date]:
    m = RE_DATE_HEADER.search(str(cell))
    if not m:
        return None
    d = int(m.group(1)); mon = MONTH.get(m.group(2).lower()); y = int(m.group(3))
    if not mon:
        return None
    return date(y, mon, d)


def parse_time(val: Any) -> Optional[time]:
    # текст 'HH:MM[:SS]' или excel-фракция суток, или pandas Timestamp
    if isinstance(val, (pd.Timestamp, datetime)):
        return time(val.hour, val.minute, val.second)
    s = str(val).strip()
    m = re.match(r'^(\d{1,2})[:\.](\d{1,2})(?::(\d{1,2}))?$', s)
    if m:
        h = int(m.group(1)); mi = int(m.group(2)); se = int(m.group(3) or 0)
        if 0<=h<24 and 0<=mi<60 and 0<=se<60:
            return time(h, mi, se)
    # excel fraction
    try:
        f = float(val)
        if -1.0 < f < 2.0:
            sec = int(round(f*24*3600))%(24*3600)
            return time(sec//3600,(sec%3600)//60, sec%60)
    except Exception:
        pass
    return None


def build_schedule_index(df: pd.DataFrame) -> Dict[Tuple[str, frozenset], List[datetime]]:
    """Ожидаемый вид листа: A: время, B: название или заголовок даты. Дата может быть в A или B."""
    idx: Dict[Tuple[str, frozenset], List[datetime]] = {}
    cur_day: Optional[date] = None
    for _, row in df.iterrows():
        # Гарантируем хотя бы 2 колонки
        if row.shape[0] < 2:
            # Попробуем всё равно взять первую как потенциальный заголовок даты
            cell0 = row.iloc[0]
            d0 = parse_header_date(cell0)
            if d0:
                cur_day = d0
            continue

        time_cell = row.iloc[0]
        title = row.iloc[1]

        # Заголовок дня может быть в любой из двух колонок
        d_title = parse_header_date(title)
        d_time = parse_header_date(time_cell)
        if d_title or d_time:
            cur_day = d_title or d_time
            continue

        if cur_day is None:
            continue

        # Определяем время (из первой колонки)
        t = parse_time(time_cell)
        if not t or pd.isna(title) or str(title).strip() == "":
            continue

        base, epis = split_base_and_episodes(str(title))
        key = (base, frozenset(epis))
        idx.setdefault(key, []).append(datetime.combine(cur_day, t))
    return idx


def format_dt_list(dts: Iterable[datetime], minutes_only: bool = True) -> str:
    items = sorted(set(dts))
    fmt = "%d.%m.%Y %H:%M" if minutes_only else "%d.%m.%Y %H:%M:%S"
    return "; ".join(dt.strftime(fmt) for dt in items)
