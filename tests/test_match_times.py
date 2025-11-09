import io
from datetime import datetime
from backend.processors.write_report_openpyxl import match_times_for_title

# Простая фиксация индекса
# ключ: (base, frozenset(episodes))
base_index = {
    ('гора самоцветов', frozenset({63,64})): [datetime(2025,9,1,8,0), datetime(2025,9,1,9,0)],
    ('новости', frozenset()): [datetime(2025,9,1,6,0), datetime(2025,9,1,7,0)]
}

def test_exact_match():
    dts = match_times_for_title('Гора самоцветов 63,64', base_index)
    assert len(dts) == 2


def test_partial_overlap():
    dts = match_times_for_title('Гора самоцветов. 63 серия', base_index)
    # Берём пересечение по эпизодам → должны получить обе даты
    assert len(dts) == 2


def test_no_episodes():
    dts = match_times_for_title('Новости', base_index)
    assert len(dts) == 2


def test_no_match():
    dts = match_times_for_title('Несуществующая', base_index)
    assert dts == []

