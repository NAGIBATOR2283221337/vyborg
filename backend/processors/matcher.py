from typing import Dict, Tuple, List, Iterable
from datetime import datetime
from rapidfuzz import fuzz

from .normalize_titles import split_base_episodes, norm, norm_base_only
from .settings_match import BASE_RATIO, PARTIAL_RATIO, TOKEN_SET, JACCARD_MIN, ALLOW_EPISODE_PARTIAL, MAX_CANDIDATES, ALLOW_CONTAINS


def _tokens(s: str):
    return set(s.split())


def _jaccard(a: str, b: str) -> float:
    A, B = _tokens(a), _tokens(b)
    if not A or not B:
        return 0.0
    return len(A & B) / max(1, len(A | B))


def best_candidates(report_title: str, schedule_keys: Iterable[Tuple[str, frozenset]]) -> Tuple[List[Tuple[str,frozenset]], List[int]]:
    base_r, eps_r = split_base_episodes(report_title)
    base_r0 = norm_base_only(base_r)
    scored = []
    for base_s, eps_s in schedule_keys:
        base_s0 = norm_base_only(base_s)
        r1 = fuzz.ratio(base_r0, base_s0)
        r2 = fuzz.partial_ratio(base_r0, base_s0)
        r3 = fuzz.token_set_ratio(base_r0, base_s0)
        jac = _jaccard(base_r0, base_s0)
        ok = (r1>=BASE_RATIO or r2>=PARTIAL_RATIO or r3>=TOKEN_SET or jac>=JACCARD_MIN)
        if ALLOW_CONTAINS and (base_r0 in base_s0 or base_s0 in base_r0):
            ok = True
            r2 = max(r2, 100)
        if ok:
            score = max(r1, r2, r3) + int(jac*10)
            scored.append((score, base_s, eps_s))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [(b,e) for _,b,e in scored[:MAX_CANDIDATES]], list(eps_r)


def pick_showtimes_for_report_title(title: str, index: Dict[Tuple[str, frozenset], List[datetime]]) -> List[datetime]:
    cands, eps_r = best_candidates(title, index.keys())
    if not cands:
        return []
    eps_r_set = set(eps_r)
    # 1) полное совпадение эпизодов
    for b,e in cands:
        if eps_r_set and e == frozenset(eps_r_set):
            return index[(b,e)]
    # 2) любое пересечение
    if ALLOW_EPISODE_PARTIAL and eps_r_set:
        out = []
        for b,e in cands:
            if set(e) & eps_r_set:
                out += index[(b,e)]
        if out:
            return sorted(set(out))
    # 3) без эпизодов
    for b,e in cands:
        if not eps_r_set and not e:
            return index[(b,e)]
    # 4) fallback: топ-1 независимо от серий
    b,e = cands[0]
    return index[(b,e)]
