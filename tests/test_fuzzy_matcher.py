from backend.processors.matcher import best_candidates, pick_showtimes_for_report_title
from backend.processors.normalize_titles import split_base_episodes
from datetime import datetime

index = {
    ("гора самоцветов", frozenset({63,64})): [datetime(2025,9,1,8,0), datetime(2025,9,1,9,0)],
    ("новости", frozenset()): [datetime(2025,9,1,6,0)]
}

def test_best_candidates():
    cands, eps = best_candidates("Гора самоцветов. 63 серия", index.keys())
    assert cands, "Должны быть кандидаты"
    assert any(b=="гора самоцветов" for b,_ in cands)


def test_partial_episode_match():
    dts = pick_showtimes_for_report_title("Гора самоцветов. 63 серия", index)
    assert dts, "Должен найтись хотя бы один показ"
    assert dts[0].hour == 8


def test_no_episode_title():
    dts = pick_showtimes_for_report_title("Новости", index)
    assert dts and dts[0].hour == 6


def test_no_match():
    dts = pick_showtimes_for_report_title("Несуществующая", index)
    assert dts == []

