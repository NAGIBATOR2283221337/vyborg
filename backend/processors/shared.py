import os
import shutil
import tempfile
import re
import gc
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import datetime
import difflib

import pandas as pd
import openpyxl
from openpyxl import load_workbook


def ensure_real_xlsx(path: str) -> str:
    """
    Многоступенчатая конверсия .xls → .xlsx
    1. Проверяем через openpyxl
    2. Пробуем Excel COM (SaveAs 51)
    3. LibreOffice soffice --headless --convert-to xlsx
    4. pandas fallback
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл не найден: {path}")

    # Если уже xlsx и читается openpyxl - возвращаем как есть
    if path.lower().endswith('.xlsx'):
        wb = None
        try:
            wb = load_workbook(path)
            # Проверяем, что файл читается
            _ = wb.active
            return path
        except Exception:
            pass
        finally:
            if wb is not None:
                try:
                    wb.close()
                except:
                    pass
            # Принудительное освобождение
            wb = None
            gc.collect()
            time.sleep(0.2)

    # Создаем новый путь .xlsx
    base_name = os.path.splitext(path)[0]
    xlsx_path = f"{base_name}.xlsx"

    # Этап 1: Попробуем openpyxl (для .xls не сработает, но попробуем)
    try:
        wb = load_workbook(path)
        wb.save(xlsx_path)
        wb.close()  # Важно: закрываем файл
        gc.collect()  # Освобождаем память
        time.sleep(0.1)  # Небольшая задержка для полного освобождения файла

        # Проверяем, что файл создался и доступен
        if os.path.exists(xlsx_path):
            return xlsx_path
    except Exception:
        pass

    # Этап 2: Excel COM (только на Windows)
    if os.name == 'nt':
        try:
            import win32com.client
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = False
            wb = excel.Workbooks.Open(os.path.abspath(path))
            wb.SaveAs(os.path.abspath(xlsx_path), FileFormat=51)  # xlOpenXMLWorkbook
            wb.Close()
            excel.Quit()
            if os.path.exists(xlsx_path):
                return xlsx_path
        except Exception:
            pass

    # Этап 3: LibreOffice
    try:
        import subprocess
        result = subprocess.run([
            'soffice', '--headless', '--convert-to', 'xlsx',
            '--outdir', os.path.dirname(path), path
        ], capture_output=True, timeout=30)
        if result.returncode == 0 and os.path.exists(xlsx_path):
            return xlsx_path
    except Exception:
        pass

    # Этап 4: pandas fallback
    try:
        if path.lower().endswith('.xls'):
            df = pd.read_excel(path, sheet_name=None)  # Читаем все листы
            with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
                for sheet_name, sheet_df in df.items():
                    sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
            if os.path.exists(xlsx_path):
                return xlsx_path
    except Exception:
        pass

    # Если ничего не помогло, возвращаем исходный путь
    return path


def normalize_base(title: str) -> str:
    """Нормализация названий с вырезанием артикулов, расширений и мусора"""
    if not title:
        return ""

    title = str(title).strip()
    original_title = title  # Сохраняем для отладки

    # Удаляем номера серий и эпизодов в различных форматах
    title = re.sub(r'\s+\d+[,\s]*\d*\s*', ' ', title)  # "61, 62" или "63, 64"
    title = re.sub(r'\s*№\s*\d+', '', title)  # "№ 5"

    # Удаляем артикулы и коды в скобках
    title = re.sub(r'\([^)]*\)', '', title)

    # Удаляем (ред), (редакция)
    title = re.sub(r'\s*\(ред\w*\)', '', title, flags=re.IGNORECASE)

    # Удаляем copy, копия
    title = re.sub(r'\s*cop[yi]e?\s*\d*', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s*копи[яи]\s*\d*', '', title, flags=re.IGNORECASE)

    # Удаляем служебные слова
    title = re.sub(r'\b(серия|серии|выпуск|передача|программа|фильм|эпизод)\b', '', title, flags=re.IGNORECASE)

    # Удаляем диапазоны дат
    title = re.sub(r'\d{1,2}\.\d{1,2}\.\d{2,4}\s*-\s*\d{1,2}\.\d{1,2}\.\d{2,4}', '', title)

    # Удаляем расширения файлов
    title = re.sub(r'\.(mp4|avi|mkv|mov|wmv|mp3|wav)$', '', title, flags=re.IGNORECASE)

    # Очистка лишних пробелов
    title = re.sub(r'\s+', ' ', title).strip()

    # Приводим к нижнему регистру для сопоставления
    result = title.lower()

    print(f"    Нормализация: '{original_title}' -> '{result}'")
    return result


def denoise_tokens(tokens: List[str]) -> List[str]:
    """Удаляем шумовые токены"""
    try:
        # Пытаемся импортировать конфигурацию
        import sys
        import os
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.py')
        if os.path.exists(config_path):
            sys.path.insert(0, os.path.dirname(config_path))
            import config
            noise_words = config.STOP_WORDS
        else:
            # Fallback к встроенному списку
            noise_words = {
                'в', 'на', 'с', 'по', 'из', 'от', 'до', 'для', 'про', 'под', 'над', 'при',
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'
            }
    except:
        noise_words = {
            'в', 'на', 'с', 'по', 'из', 'от', 'до', 'для', 'про', 'под', 'над', 'при',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'
        }

    return [token for token in tokens if token.lower() not in noise_words and len(token) > 1]


def tokenize(text: str) -> List[str]:
    """Токенизация текста"""
    if not text:
        return []

    # Оставляем только буквы, цифры и пробелы
    text = re.sub(r'[^\w\s]', ' ', str(text), flags=re.UNICODE)
    tokens = text.lower().split()
    return denoise_tokens(tokens)


def jaccard_over_min(tokens1: List[str], tokens2: List[str]) -> float:
    """Коэффициент Жаккара с нормализацией на минимальное количество"""
    if not tokens1 or not tokens2:
        return 0.0

    set1, set2 = set(tokens1), set(tokens2)
    intersection = len(set1 & set2)
    min_len = min(len(set1), len(set2))

    return intersection / min_len if min_len > 0 else 0.0


def seq_ratio(text1: str, text2: str) -> float:
    """Коэффициент схожести через difflib.SequenceMatcher"""
    if not text1 or not text2:
        return 0.0
    return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def parse_date_from_cell(value) -> Optional[str]:
    """Парсинг даты из ячейки отчёта → "ДД.ММ.ГГГГ" """
    if not value:
        return None

    # Если это datetime объект
    if isinstance(value, datetime.datetime):
        return value.strftime("%d.%m.%Y")

    if isinstance(value, datetime.date):
        return value.strftime("%d.%m.%Y")

    # Если строка, пробуем парсить
    value_str = str(value).strip()

    # Паттерны дат
    patterns = [
        r'(\d{1,2})\.(\d{1,2})\.(\d{4})',
        r'(\d{1,2})/(\d{1,2})/(\d{4})',
        r'(\d{1,2})-(\d{1,2})-(\d{4})',
        r'(\d{4})-(\d{1,2})-(\d{1,2})',
    ]

    for pattern in patterns:
        match = re.search(pattern, value_str)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                if pattern.startswith(r'(\d{4}'):  # YYYY-MM-DD
                    year, month, day = groups
                else:  # DD.MM.YYYY, DD/MM/YYYY, DD-MM-YYYY
                    day, month, year = groups

                try:
                    dt = datetime.date(int(year), int(month), int(day))
                    return dt.strftime("%d.%m.%Y")
                except ValueError:
                    continue

    return None


def parse_time_from_str(value) -> Optional[str]:
    """Парсинг времени из сетки → "H:MM" """
    if not value:
        return None

    value_str = str(value).strip()

    # Паттерны времени
    patterns = [
        r'(\d{1,2}):(\d{2})',
        r'(\d{1,2})\.(\d{2})',
        r'(\d{1,2})\s*ч\s*(\d{2})',
    ]

    for pattern in patterns:
        match = re.search(pattern, value_str)
        if match:
            hour, minute = match.groups()
            try:
                h, m = int(hour), int(minute)
                if 0 <= h <= 23 and 0 <= m <= 59:
                    return f"{h}:{minute.zfill(2)}"
            except ValueError:
                continue

    return None


def parse_dt_key(date_str: str) -> str:
    """Преобразуем дату в ключ для индекса"""
    return date_str


def limit_and_format(full_dt_list: List[str], limit: int) -> str:
    """
    Ограничение и форматирование показов
    Сортировка по дате/времени, дедупликация, формат "ДД.MM.ГГГГ в H:MM"
    """
    if not full_dt_list:
        return ""

    # Дедупликация
    unique_items = list(dict.fromkeys(full_dt_list))

    # Сортировка (предполагаем, что элементы уже в формате "ДД.MM.ГГГГ в H:MM")
    def sort_key(item):
        try:
            # Извлекаем дату и время для сортировки
            parts = item.split(' в ')
            if len(parts) == 2:
                date_part, time_part = parts
                day, month, year = date_part.split('.')
                hour, minute = time_part.split(':')
                return datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))
        except:
            pass
        return datetime.datetime.min

    unique_items.sort(key=sort_key)

    # Ограничиваем количество
    limited = unique_items[:limit]

    return "; ".join(limited)


def is_title_header(cell_value: str) -> bool:
    """Проверяем, является ли ячейка заголовком названия"""
    if not cell_value:
        return False

    value = str(cell_value).lower().strip()

    title_keywords = [
        'название передачи',
        'наименование аудиовизуального произведения',
        'название',
        'наименование',
        'передача',
        'произведение'
    ]

    for keyword in title_keywords:
        if keyword in value:
            return True

    return False


def is_datetime_header(cell_value: str) -> bool:
    """Проверяем, является ли ячейка заголовком даты/времени"""
    if not cell_value:
        return False

    value = str(cell_value).lower().strip()

    datetime_keywords = [
        'дата',
        'время',
        'дата и время',
        'дата/время',
        'показ',
        'эфир',
        'трансляция'
    ]

    for keyword in datetime_keywords:
        if keyword in value:
            return True

    return False


def find_headers_any(ws) -> Tuple[int, int, int]:
    """
    Универсальный поиск заголовков на листе отчёта
    Возвращает: (header_row, title_col, date_col)
    """
    max_row = min(ws.max_row, 30)  # Увеличиваем до 30 строк для поиска заголовков глубже
    max_col = min(ws.max_column, 12)  # Ограничиваем поиск по колонкам

    print(f"🔍 Поиск заголовков в области {max_row}x{max_col}")

    for row in range(1, max_row + 1):
        title_col = None
        date_col = None

        for col in range(1, max_col + 1):
            cell_value = ws.cell(row, col).value
            if cell_value:
                if is_title_header(str(cell_value)):
                    title_col = col
                elif is_datetime_header(str(cell_value)):
                    date_col = col

        if title_col and date_col:
            return row, title_col, date_col

    # Если не нашли оба заголовка, возвращаем значения по умолчанию
    return 1, 1, 2


def build_schedule_index(schedule_xlsx: str) -> Tuple[Dict[str, pd.DataFrame], Dict[str, Set[str]]]:
    """
    Индексация сетки по дате
    Возвращает: schedule_by_date: {date: DataFrame(base,time)}, bases_by_date: {date: set(bases)}
    """
    wb = None
    schedule_by_date = {}
    bases_by_date = {}

    try:
        wb = load_workbook(schedule_xlsx)
        print(f"📚 Обрабатываем сетку, листов: {len(wb.sheetnames)}")

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            current_date = None
            print(f"📄 Лист '{sheet_name}': {ws.max_row} строк, {ws.max_column} колонок")

            for row in range(1, ws.max_row + 1):
                cell_a = ws.cell(row, 1).value
                cell_b = ws.cell(row, 2).value

                if cell_a:
                    cell_a_str = str(cell_a).strip()
                    print(f"  Строка {row}: A='{cell_a_str}', B='{cell_b}'")

                    # Ищем строки с датой - расширенные паттерны
                    date_patterns = [
                        r'(\w+),\s*(\d{1,2})\s+(\w+)\s+(\d{4})',  # "Понедельник, 1 сентября 2025"
                        r'(\d{1,2})\s+(\w+)\s+(\d{4})',          # "1 сентября 2025"
                        r'(\d{1,2})\.(\d{1,2})\.(\d{4})',        # "01.09.2025"
                    ]

                    date_found = False
                    for pattern in date_patterns:
                        match = re.search(pattern, cell_a_str)
                        if match:

                            groups = match.groups()
                            print(f"    📅 Найдена дата, группы: {groups}")

                            if len(groups) == 4:  # "Понедельник, 1 сентября 2025"
                                _, day, month_name, year = groups
                            elif len(groups) == 3 and not groups[0].isdigit():  # "1 сентября 2025"
                                day, month_name, year = groups
                            elif len(groups) == 3 and groups[0].isdigit():  # "01.09.2025"
                                day, month, year = groups
                                # Преобразуем в нужный формат
                                current_date = f"{day.zfill(2)}.{month.zfill(2)}.{year}"
                                print(f"    ✅ Дата установлена: {current_date}")
                                if current_date not in schedule_by_date:
                                    schedule_by_date[current_date] = pd.DataFrame(columns=['base', 'time'])
                                    bases_by_date[current_date] = set()
                                date_found = True
                                break

                            if not date_found:
                                # Преобразуем название месяца в номер
                                months = {
                                    'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
                                    'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
                                    'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'
                                }

                                month_num = months.get(month_name.lower())
                                if month_num:
                                    current_date = f"{day.zfill(2)}.{month_num}.{year}"
                                    print(f"    ✅ Дата установлена: {current_date}")

                                    if current_date not in schedule_by_date:
                                        schedule_by_date[current_date] = pd.DataFrame(columns=['base', 'time'])
                                        bases_by_date[current_date] = set()
                                    date_found = True
                            break

                    # Если есть текущая дата, пробуем извлечь время из колонки A
                    if current_date and not date_found:
                        time_parsed = parse_time_from_str(cell_a)
                        if time_parsed and cell_b:
                            base_normalized = normalize_base(str(cell_b))
                            if base_normalized:
                                # Добавляем запись
                                new_row = pd.DataFrame([{
                                    'base': base_normalized,
                                    'time': time_parsed
                                }])
                                schedule_by_date[current_date] = pd.concat([
                                    schedule_by_date[current_date], new_row
                                ], ignore_index=True)

                                bases_by_date[current_date].add(base_normalized)

    finally:
        if wb is not None:
            try:
                wb.close()
            except:
                pass
        wb = None
        gc.collect()  # Принудительное освобождение памяти
        time.sleep(0.5)  # Увеличенная задержка для полного освобождения файла

    return schedule_by_date, bases_by_date
