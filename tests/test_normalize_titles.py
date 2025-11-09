import pytest
from backend.processors.normalize_titles import split_base_episodes, norm

def test_split_single_episode():
    base, eps = split_base_episodes('Гора самоцветов. 63 серия')
    assert base == 'гора самоцветов'
    assert eps == {63}

def test_split_range():
    base, eps = split_base_episodes('Гора самоцветов 63-64')
    assert base == 'гора самоцветов'
    assert eps == {63,64}

def test_split_list():
    base, eps = split_base_episodes('Гора самоцветов 63,64')
    assert eps == {63,64}

def test_split_none():
    base, eps = split_base_episodes('Новости')
    assert base == 'новости'
    assert eps == set()

