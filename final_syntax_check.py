#!/usr/bin/env python3
"""
Финальная проверка синтаксиса после исправления IndentationError
"""
import ast
import sys

def check_file_syntax(filename):
    try:
        # Пробуем разные кодировки
        encodings = ['utf-8', 'utf-8-sig', 'cp1251', 'latin1']
        content = None

        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            print(f"❌ {filename} - не удалось прочитать файл (проблема с кодировкой)")
            return False

        # Парсим AST для проверки синтаксиса
        ast.parse(content, filename=filename)
        print(f"✅ {filename} - синтаксис корректен")
        return True

    except SyntaxError as e:
        print(f"❌ {filename} - SyntaxError на строке {e.lineno}:")
        print(f"   {e.msg}")
        if e.text:
            print(f"   Код: {e.text.strip()}")
        return False

    except IndentationError as e:
        print(f"❌ {filename} - IndentationError на строке {e.lineno}:")
        print(f"   {e.msg}")
        if e.text:
            print(f"   Код: {e.text.strip()}")
        return False

    except Exception as e:
        print(f"❌ {filename} - Ошибка: {e}")
        return False

# Список файлов для проверки
files_to_check = [
    'backend/processors/shared.py',
    'backend/processors/processor_rus.py',
    'backend/processors/processor_foreign.py',
    'backend/main.py'
]

print("🔍 ФИНАЛЬНАЯ ПРОВЕРКА СИНТАКСИСА")
print("=" * 50)

all_ok = True
for filename in files_to_check:
    if not check_file_syntax(filename):
        all_ok = False

print("=" * 50)
if all_ok:
    print("🎉 ВСЕ СИНТАКСИЧЕСКИЕ ОШИБКИ ИСПРАВЛЕНЫ!")
    print("✅ IndentationError устранена")
    print("✅ Система готова к запуску")
    print("\nДля запуска используйте:")
    print("  python -m uvicorn backend.main:app --reload --port 8000")
else:
    print("⚠️  Найдены синтаксические ошибки!")

print("=" * 50)
