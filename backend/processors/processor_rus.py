# processor_rus.py – new architecture (openpyxl only)
import os
import tempfile
import shutil
from typing import Dict

from .write_report_openpyxl import fill_report_column_and_prune


def process(schedule_bytes: bytes, report_bytes: bytes, params: Dict) -> bytes:
    sheet_name = params.get('sheet_name', 'росийские произведения')
    title_substr = params.get('title_substr', 'Наименование аудиовизуального произведения')
    target_substr = params.get('target_substr', 'Дата и время выхода в эфир (число, часы, мин.)')

    temp_dir = tempfile.mkdtemp(prefix='rus_report_')
    report_path = os.path.join(temp_dir, 'report.xlsx')
    try:
        with open(report_path, 'wb') as f:
            f.write(report_bytes)

        fill_report_column_and_prune(schedule_bytes, report_path, sheet_name=sheet_name,
                           title_substr=title_substr, target_substr=target_substr)

        with open(report_path, 'rb') as f:
            return f.read()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
