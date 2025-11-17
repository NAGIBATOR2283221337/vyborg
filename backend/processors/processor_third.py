# processor_third.py – заглушка третьего типа отчёта
"""Третий обработчик (пока минимальная реализация).

Функция process повторяет входной отчёт без изменений, чтобы можно было
протестировать полный путь загрузки/скачивания. Далее сюда можно будет
добавить специфическую логику.
"""
from io import BytesIO
from typing import Dict


def process(schedule_bytes: bytes, report_bytes: bytes, params: Dict) -> bytes:
    """Возвращает исходный отчёт как есть (пока что заглушка).
    schedule_bytes: bytes сетки (игнорируется)
    report_bytes: bytes отчёта
    params: словарь параметров (игнорируется)
    """
    # Просто возвращаем то что пришло – можно вставить базовую проверку
    if not report_bytes:
        return b""  # пустой результат если отчёт пуст
    # Убеждаемся что это действительно xlsx (простейшая проверка сигнатуры zip)
    if not (len(report_bytes) > 4 and report_bytes[:2] == b"PK"):
        # Оборачиваем произвольные данные в zip-пустышку, чтобы Excel не падал
        mem = BytesIO()
        mem.write(report_bytes)
        return mem.getvalue()
    return report_bytes

