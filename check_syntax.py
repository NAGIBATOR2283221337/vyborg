import ast
import sys

def check_syntax(filename):
    """Проверка синтаксиса Python файла"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()

        # Компилируем AST для проверки синтаксиса
        ast.parse(source, filename=filename)
        print(f"✅ {filename} - синтаксис OK")
        return True

    except SyntaxError as e:
        print(f"❌ {filename} - SyntaxError: {e}")
        print(f"   Строка {e.lineno}: {e.text}")
        return False
    except IndentationError as e:
        print(f"❌ {filename} - IndentationError: {e}")
        print(f"   Строка {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ {filename} - Ошибка: {e}")
        return False

# Проверяем все Python файлы
files_to_check = [
    'backend/processors/shared.py',
    'backend/processors/processor_rus.py',
    'backend/processors/processor_foreign.py',
    'backend/main.py'
]

print("🔍 Проверка синтаксиса Python файлов:")
print("=" * 50)

all_ok = True
for filename in files_to_check:
    if not check_syntax(filename):
        all_ok = False

print("=" * 50)
if all_ok:
    print("🎉 Все файлы синтаксически корректны!")
    print("IndentationError исправлена!")
else:
    print("⚠️  Найдены синтаксические ошибки!")
