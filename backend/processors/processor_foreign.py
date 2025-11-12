from typing import Dict

try:
    from . import processor_rus
    from .shared import *
except ImportError:
    import processor_rus  # type: ignore
    from shared import *  # type: ignore


def process(schedule_bytes: bytes, report_bytes: bytes, params: Dict) -> bytes:
    """
    Обработка иностранного отчета.
    По умолчанию работает с листом "иностранные произведения" в отчётном файле, но
    позволяет переопределить через params['sheet_name'].
    Использует ту же логику заполнения, что и российский процессор (openpyxl-only).
    """
    # Если пользователь не передал sheet_name – подставляем лист иностранных произведений
    if 'sheet_name' not in params or not params.get('sheet_name'):
        params = dict(params)  # копия чтобы не мутировать исходный
        params['sheet_name'] = 'иностранные произведения'
    return processor_rus.process(schedule_bytes, report_bytes, params)
