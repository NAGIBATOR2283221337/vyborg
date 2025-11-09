import ast

files = [
    'backend/processors/processor_rus.py',
    'backend/processors/shared.py',
    'backend/main.py'
]

print("Проверка синтаксиса:")
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            ast.parse(file.read())
        print(f"✅ {f}")
    except Exception as e:
        print(f"❌ {f}: {e}")

print("Готово!")
