#!/usr/bin/env python3
"""
Простой тест для проверки работы модулей
"""

# Тестируем импорты
try:
    import sys
    print(f"Python версия: {sys.version}")

    # Тестируем стандартные модули
    import os
    import tempfile
    import re
    import datetime
    import difflib
    print("✓ Стандартные модули импортированы успешно")

    # Тестируем pandas
    try:
        import pandas as pd
        print("✓ pandas импортирован успешно")
    except ImportError as e:
        print(f"✗ Ошибка импорта pandas: {e}")

    # Тестируем openpyxl
    try:
        import openpyxl
        print("✓ openpyxl импортирован успешно")
    except ImportError as e:
        print(f"✗ Ошибка импорта openpyxl: {e}")

    # Тестируем fastapi
    try:
        import fastapi
        print("✓ fastapi импортирован успешно")
    except ImportError as e:
        print(f"✗ Ошибка импорта fastapi: {e}")

    # Тестируем uvicorn
    try:
        import uvicorn
        print("✓ uvicorn импортирован успешно")
    except ImportError as e:
        print(f"✗ Ошибка импорта uvicorn: {e}")

    print("\nТест импортов завершен!")

except Exception as e:
    print(f"Общая ошибка: {e}")
    import traceback
    traceback.print_exc()
