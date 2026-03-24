import vk_api

def handle(vk, event, data, save_func):
    p = data.get("prefix", ".")
    msg_text = event.text.lower()

    # --- ДОБАВЛЕНИЕ (+дов | Имя) ---
    if msg_text.startswith(f"{p}+дов"):
        try:
            msg_info = vk.messages.getById(message_ids=event.message_id)['items'][0]
            target_id = None
            name = "Без имени"

            if 'reply_message' in msg_info:
                target_id = str(msg_info['reply_message']['from_id'])
                if "|" in event.text:
                    name = event.text.split("|", 1)[1].strip()
            elif "|" in event.text:
                content = event.text[len(f"{p}+дов"):].strip()
                target_id, name = [i.strip() for i in content.split("|", 1)]

            if target_id:
                if "trusted" not in data: data["trusted"] = {}
                data["trusted"][target_id] = name
                save_func(data)
                vk.messages.edit(peer_id=event.peer_id, message=f"✅ {name} добавлен(а) в доверенные!", message_id=event.message_id)
        except: pass

    # --- УДАЛЕНИЕ (-дов) ---
    elif msg_text.startswith(f"{p}-дов"):
        try:
            msg_info = vk.messages.getById(message_ids=event.message_id)['items'][0]
            target_id = None

            # 1. Если есть ответ на сообщение
            if 'reply_message' in msg_info:
                target_id = str(msg_info['reply_message']['from_id'])
            # 2. Если просто написали ID после команды (например: .-дов 12345)
            else:
                target_id = event.text[len(f"{p}-дов"):].strip()

            if target_id and target_id in data.get("trusted", {}):
                name = data["trusted"].pop(target_id)
                save_func(data)
                vk.messages.edit(peer_id=event.peer_id, message=f"🗑 {name} удален(а) из доверенных.", message_id=event.message_id)
            else:
                vk.messages.edit(peer_id=event.peer_id, message="⚠️ Пользователь не найден в списке.", message_id=event.message_id)
        except Exception as e:
            print(f"Ошибка удаления: {e}")

    # --- СПИСОК (довы) ---
    elif msg_text == f"{p}довы":
        trusted = data.get("trusted", {})
        if not trusted:
            vk.messages.edit(peer_id=event.peer_id, message="📜 Список доверенных пуст.", message_id=event.message_id)
        else:
            lines = ["👥 Доверенные пользователи:"]
            for uid, name in trusted.items():
                lines.append(f"• [id{uid}|{name}]")
            vk.messages.edit(peer_id=event.peer_id, message="\n".join(lines), message_id=event.message_id)
