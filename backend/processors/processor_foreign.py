from typing import Dict

try:
    from . import processor_rus
    from .shared import *
except ImportError:
    import processor_rus
    from shared import *


def process(schedule_bytes: bytes, report_bytes: bytes, params: Dict) -> bytes:
    """
    Обработка иностранного отчета
    Использует ту же улучшенную логику, что и российский процессор
    с надежным управлением файлами и ресурсами
    """
    return processor_rus.process(schedule_bytes, report_bytes, params)
