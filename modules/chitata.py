import time

def handle(vk, event, data, save_func):
    p = data.get("prefix", ".")
    text_lower = event.text.lower()
    
    # 1. Проверяем команду
    if not text_lower.startswith(f"{p} су цитата"):
        return

    # --- ПОИСК ID СООБЩЕНИЯ (РЕПЛАЯ) ---
    fwd_id = None
    
    # Способ 1: Прямой атрибут (зависит от версии vk_api)
    if hasattr(event, 'reply_message') and event.reply_message:
        fwd_id = event.reply_message['id']
    
    # Способ 2: Через сырые данные события (наиболее надежный)
    elif 'reply_message' in event.raw[6]: # В UserLongPoll индекс 6 содержит attachments/extra
        import json
        try:
            # Парсим вложения, если они пришли строкой
            extra = event.raw[6]
            if 'reply_message' in extra:
                reply_data = json.loads(extra['reply_message'])
                fwd_id = reply_data.get('id')
        except:
            pass

    # Если совсем ничего не нашли, попробуем взять через getById (медленно, но верно)
    if not fwd_id:
        try:
            msg_full = vk.messages.getById(message_ids=event.message_id)['items'][0]
            if 'reply_message' in msg_full:
                fwd_id = msg_full['reply_message']['id']
            elif msg_full.get('fwd_messages'):
                fwd_id = msg_full['fwd_messages'][0]['id']
        except:
            return # Если и тут пусто, цитату делать не из чего

    # --- ОТПРАВКА СОТЕБОТУ ---
    # Перед отправкой запомним последний ID в ЛС
    try:
        last_hist = vk.messages.getHistory(peer_id=-205747591, count=1)
        last_msg_id = last_hist['items'][0]['id'] if last_hist.get('items') else 0
    except:
        last_msg_id = 0

    try:
        # Шлем !цитата + прикрепляем то сообщение, на которое ты ответил
        vk.messages.send(
            peer_id=-205747591, 
            message="!цитата", 
            forward_messages=fwd_id, # Передаем числом или строкой
            random_id=0
        )
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return

    # --- ОЖИДАНИЕ ОТВЕТА ---
    start_wait = time.time()
    while time.time() - start_wait < 40:
        try:
            # Получаем последнее сообщение в ЛС с Сотеботом
            res = vk.messages.getHistory(peer_id=-205747591, count=1)
            if res.get('items'):
                msg = res['items'][0]
                
                # Если ID новый и сообщение от бота
                if msg['id'] > last_msg_id and msg['from_id'] == -205747591:
                    # Ищем картинку
                    if any(att['type'] == 'photo' for att in msg.get('attachments', [])):
                        vk.messages.send(
                            peer_id=event.peer_id, 
                            forward_messages=msg['id'], 
                            random_id=0
                        )
                        return
        except:
            pass
        time.sleep(1)
