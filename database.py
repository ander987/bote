import json
import os

DB_FILE = "database.json"

def load_data():
    # Стандартная структура базы со всеми твоими переменными
    default_data = {
        "token": None,
        "prefix": ".",
        "active": True,
        "trusted": {},
        "gs": {},
        "voices": [],
        "auto_friends": True
    }

    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                # Проверяем каждый ключ из стандарта. Если в файле его нет — добавляем.
                for key, value in default_data.items():
                    if key not in data:
                        data[key] = value
                return data
            except:
                return default_data
    return default_data

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)