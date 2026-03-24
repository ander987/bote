import time

def check_friends(vk, data, save_func):
    # Если в базе auto_friends стоит False — выходим
    if not data.get("auto_friends", True):
        return

    try:
        # Проверяем входящие заявки
        reqs = vk.friends.getRequests(need_viewed=1, out=0)
        if reqs.get('items'):
            for uid in reqs['items']:
                vk.friends.add(user_id=uid)
                print(f"👤 [AutoFriends] Принял в друзья: {uid}")
                time.sleep(1.5) # Пауза от капчи
    except:
        pass

def handle(vk, event, data, save_func):
    """Команды управления (вызываются при сообщении)"""
    p = data.get("prefix", ".")
    msg = event.text.lower()

    if msg == f"{p}+адр":
        data["auto_friends"] = True
        save_func(data)
        vk.messages.edit(peer_id=event.peer_id, message="✅ Автодобавление друзей включено", message_id=event.message_id)

    elif msg == f"{p}-адр":
        data["auto_friends"] = False
        save_func(data)
        vk.messages.edit(peer_id=event.peer_id, message="❌ Автодобавление друзей выключено", message_id=event.message_id)