import os
import tempfile
import gc
import time
import shutil
from io import BytesIO
from typing import Dict

import openpyxl
from openpyxl import load_workbook

try:
    from .shared import (
        ensure_real_xlsx,
        build_schedule_index,
        find_headers_any,
        parse_date_from_cell,
        normalize_base,
        tokenize,
        jaccard_over_min,
        seq_ratio,
        limit_and_format
    )
except ImportError:
    from shared import (
        ensure_real_xlsx,
        build_schedule_index,
        find_headers_any,
        parse_date_from_cell,
        normalize_base,
        tokenize,
        jaccard_over_min,
        seq_ratio,
        limit_and_format
    )


def force_close_excel_files():
    """Принудительно освобождает все Excel процессы"""
    gc.collect()
    time.sleep(0.5)
    
    # Попытка завершить Excel процессы (только на Windows)
    if os.name == 'nt':
        try:
            import subprocess
            subprocess.run(['taskkill', '/F', '/IM', 'EXCEL.EXE'], 
                         capture_output=True, check=False)
        except:
            pass


def safe_load_workbook(path: str):
    """Безопасная загрузка workbook с автоматическим закрытием"""
    wb = None
    try:
        wb = load_workbook(path)
        return wb
    except Exception as e:
        if wb:
            try:
                wb.close()
            except:
                pass
        raise e


def safe_close_workbook(wb):
    """Безопасное закрытие workbook"""
    if wb is not None:
        try:
            wb.close()
        except:
            pass
    wb = None
    gc.collect()
    time.sleep(0.1)


def process(schedule_bytes: bytes, report_bytes: bytes, params: Dict) -> bytes:
    """
    Обработка российского отчета с улучшенным управлением ресурсами
    
    Args:
        schedule_bytes: Байты файла сетки
        report_bytes: Байты файла отчета
        params: Параметры обработки
    
    Returns:
        bytes: Готовый xlsx файл
    """
    max_shows = params.get('max_shows', 3)
    fuzzy_cutoff = params.get('fuzzy_cutoff', 0.20)
    min_token_overlap = params.get('min_token_overlap', 0.35)
    delete_unmatched = params.get('delete_unmatched', True)

    # Создаем временную директорию
    temp_dir = None
    wb = None
    
    try:
        temp_dir = tempfile.mkdtemp(prefix="report_processor_")
        
        # Сохраняем входные файлы
        schedule_path = os.path.join(temp_dir, "schedule.xlsx")
        report_path = os.path.join(temp_dir, "report.xlsx")

        with open(schedule_path, 'wb') as f:
            f.write(schedule_bytes)

        with open(report_path, 'wb') as f:
            f.write(report_bytes)

        # Конвертируем в xlsx если нужно
        schedule_path = ensure_real_xlsx(schedule_path)
        report_path = ensure_real_xlsx(report_path)

        # Принудительно освобождаем ресурсы после конверсии
        force_close_excel_files()

        # Индексируем сетку
        schedule_by_date, bases_by_date = build_schedule_index(schedule_path)
        
        # Еще раз освобождаем ресурсы
        force_close_excel_files()

        # Обрабатываем отчет
        wb = safe_load_workbook(report_path)
        ws = wb.active

        # Находим заголовки
        header_row, title_col, date_col = find_headers_any(ws)

        # Список строк для удаления (индексы)
        rows_to_delete = []

        # Обрабатываем строки отчета
        for r in range(header_row + 1, ws.max_row + 1):
            title_cell = ws.cell(r, title_col)
            date_cell = ws.cell(r, date_col)

            title_val = title_cell.value
            cell_val = date_cell.value

            if not title_val:
                continue

            # Парсим дату
            date_r = parse_date_from_cell(cell_val)

            if not date_r:
                if delete_unmatched:
                    rows_to_delete.append(r)
                continue

            # Получаем данные сетки для этой даты
            sub = schedule_by_date.get(date_r)
            if sub is None or sub.empty:
                if delete_unmatched:
                    rows_to_delete.append(r)
                continue

            # Нормализуем название из отчета
            base_r = normalize_base(str(title_val))
            if not base_r:
                if delete_unmatched:
                    rows_to_delete.append(r)
                continue

            # Токенизируем
            tokens_r = tokenize(base_r)

            # Ищем лучшее совпадение
            best_b = None
            best_score = 0.0

            for _, row_data in sub.iterrows():
                base_s = row_data['base']
                tokens_s = tokenize(base_s)

                # Вычисляем метрики
                overlap = jaccard_over_min(tokens_r, tokens_s)
                ratio = seq_ratio(base_r, base_s)

                # Проверяем пороги
                if ratio >= fuzzy_cutoff or overlap >= min_token_overlap:
                    score = max(overlap, ratio)
                    if score > best_score:
                        best_score = score
                        best_b = base_s

                # Дополнительная проверка: если есть хотя бы одно общее слово длиннее 3 символов
                if best_b is None:
                    for token_r in tokens_r:
                        for token_s in tokens_s:
                            if len(token_r) > 3 and len(token_s) > 3 and token_r == token_s:
                                if best_score < 0.5:  # Присваиваем средний балл
                                    best_score = 0.5
                                    best_b = base_s
                                    print(f"      📝 Найдено общее слово: '{token_r}'")

                # Если все еще нет совпадения, пробуем самое похожее по первым словам
                if best_b is None and tokens_r and len(sub) > 0:
                    print(f"    🔄 Поиск по первым словам...")
                    first_word_r = tokens_r[0] if tokens_r else ""

                    for _, row_data in sub.iterrows():
                        base_s = row_data['base']
                        tokens_s = tokenize(base_s)
                        first_word_s = tokens_s[0] if tokens_s else ""

                        if len(first_word_r) > 2 and len(first_word_s) > 2:
                            if first_word_r.startswith(first_word_s[:3]) or first_word_s.startswith(first_word_r[:3]):
                                best_b = base_s
                                best_score = 0.3
                                print(f"      📝 Совпадение по началу слов: '{first_word_r}' ~ '{first_word_s}'")
                                break

            if best_b is not None:
                # Собираем времена для лучшего совпадения
                matching_rows = sub[sub['base'] == best_b]
                times = matching_rows['time'].tolist()

                # Форматируем показы
                formatted_shows = []
                for time_val in times:
                    formatted_shows.append(f"{date_r} в {time_val}")

                # Применяем лимит и форматирование
                result_text = limit_and_format(formatted_shows, max_shows)

                # Записываем результат в ячейку даты
                date_cell.value = result_text
                matched_count += 1
                print(f"    ✅ НАЙДЕНО СОВПАДЕНИЕ: {best_b} -> {result_text}")
            else:
                print(f"    ❌ Совпадений не найдено")
                if delete_unmatched:
                    rows_to_delete.append(r)
                    print(f"    📝 Помечено для удаления")

        # Удаляем строки (с конца, чтобы не сбить индексы)
        for row_idx in sorted(rows_to_delete, reverse=True):
            ws.delete_rows(row_idx)

        # Сохраняем в память
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        result_bytes = output.getvalue()
        output.close()
        
        return result_bytes

    finally:
        # Обязательно закрываем workbook
        safe_close_workbook(wb)
        
        # Принудительно освобождаем все ресурсы
        force_close_excel_files()
        
        # Удаляем временную директорию
        if temp_dir and os.path.exists(temp_dir):
            try:
                # Ждем немного перед удалением
                time.sleep(1)
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                print(f"Предупреждение: не удалось удалить временную папку {temp_dir}: {e}")
