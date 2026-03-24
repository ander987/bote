import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import database
import importlib
import os
import threading
import sys
import time

def get_modules():
    mods = []
    if not os.path.exists("modules"): 
        os.makedirs("modules")
    for file in os.listdir("modules"):
        if file.endswith(".py") and file != "__init__.py":
            module_name = f"modules.{file[:-3]}"
            try:
                module = importlib.import_module(module_name)
                importlib.reload(module)
                mods.append(module)
            except: pass
    return mods

def extract_token(input_string):
    if 'access_token=' in input_string:
        start = input_string.find('access_token=') + 13
        end = input_string.find('&', start)
        return input_string[start:end] if end != -1 else input_string[start:]
    return input_string.strip()

data = database.load_data()

def login():
    token = data.get("token")
    while True:
        if not token:
            token = extract_token(input("🔑 Введите токен: "))
        try:
            session = vk_api.VkApi(token=token)
            api = session.get_api()
            user = api.users.get()[0]
            data["token"] = token
            database.save_data(data)
            print(f"✅ Успешный вход: {user['first_name']} {user['last_name']}")
            return session, api
        except:
            print("❌ Ошибка входа."); token = None

vk_session, vk = login()

def friends_loop():
    while True:
        try:
            import modules.auto_friends as af
            af.check_friends(vk, database.load_data(), database.save_data)
        except: pass
        time.sleep(30)

threading.Thread(target=friends_loop, daemon=True).start()

print(f"🚀 Бот готов! Управление через сообщения ВК.")

while True:
    try:
        longpoll = VkLongPoll(vk_session)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.text:
                is_me = event.from_me
                sender_id = str(event.user_id if event.user_id else event.peer_id)
                is_trusted = sender_id in data.get("trusted", {})
                
                if not is_me and not is_trusted:
                    continue

                pref = data.get("prefix", ".")

                if is_me and event.text.startswith(pref):
                    raw_text = event.text[len(pref):].strip()
                    parts = raw_text.split(maxsplit=1)
                    cmd = parts[0].lower()
                    args = parts[1] if len(parts) > 1 else ""

                    if cmd == "перезагрузка":
                        vk.messages.edit(peer_id=event.peer_id, message="🔄 Перезапуск...", message_id=event.message_id)
                        os.execv(sys.executable, [sys.executable] + sys.argv)
                    elif cmd == "префикс":
                        if args:
                            new_pref = args[0]
                            data["prefix"] = new_pref
                            database.save_data(data)
                            vk.messages.edit(peer_id=event.peer_id, message=f"✅ Префикс изменен на: {new_pref}", message_id=event.message_id)
                        else:
                            vk.messages.edit(peer_id=event.peer_id, message="⚠️ Укажите символ префикса!", message_id=event.message_id)
                    elif cmd == "выкл":
                        data["active"] = False
                        database.save_data(data)
                        vk.messages.edit(peer_id=event.peer_id, message="🔴 Бот выключен.", message_id=event.message_id)
                        continue
                    elif cmd == "вкл":
                        data["active"] = True
                        database.save_data(data)
                        vk.messages.edit(peer_id=event.peer_id, message="🟢 Бот включен!", message_id=event.message_id)
                        continue

                if not data.get("active", True):
                    continue

                for module in get_modules():
                    try:
                        if is_me and event.text.startswith(pref) and hasattr(module, 'handle'):
                            module.handle(vk, event, data, database.save_data)
                        elif is_trusted and not is_me and hasattr(module, 'handle_user'):
                            module.handle_user(vk, event, data)
                    except Exception as e:
                        pass
    except Exception as e:
        print(f"🔌 Ошибка сети: {e}. Рестарт через 5 сек...")
        time.sleep(5)
