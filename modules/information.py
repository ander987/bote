def handle(vk, event, data, save_func):
    p = data.get("prefix", ".")
    text_lower = event.text.lower()

    # --- КОМАНДА .ИНФО ---
    if text_lower == f"{p}инфо":
        active_status = "Включен ✅" if data.get("active") else "Выключен ❌"
        friends_status = "Вкл ✅" if data.get("auto_friends") else "Выкл ❌"
        
        info_message = (
            "📋 **Информация о юзерботе**\n"
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"🔸 Префикс: [ {p} ]\n"
            f"🔸 Состояние: {active_status}\n"
            f"🔸 Голосовых в базе: {len(data.get('gs', []))}\n"
            f"🔸 Доверенных лиц: {len(data.get('trusted', {}))}\n"
            f"🔸 Авто-прием в друзья: {friends_status}\n"
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"💡 Чтобы изменить префикс, {p}префикс [символ]"
        )
        
        vk.messages.edit(peer_id=event.peer_id, message_id=event.message_id, message=info_message)
