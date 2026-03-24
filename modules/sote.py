import time

def handle(vk, event, data, save_func):
    p = data.get("prefix", ".")
    text = event.text
    
    # Проверка команды: ". су [текст]" (строго с пробелом)
    # Игнорируем, если это "су цитата", так как для неё будет отдельный модуль
    if text.lower().startswith(f"{p} су ") and not text.lower().startswith(f"{p} су цитата"):
        # Извлекаем аргументы после ". су "
        args = text[len(p) + 4:].strip()
        if not args:
            return

        # 1. Запоминаем последний ID в ЛС с Сотеботом
        last_hist = vk.messages.getHistory(peer_id=-205747591, count=1)
        last_msg_id = last_hist['items'][0]['id'] if last_hist.get('items') else 0

        # 2. Удаляем команду из чата и отправляем в ЛС Сотеботу
        vk.messages.delete(message_ids=event.message_id, delete_for_all=1)
        vk.messages.send(peer_id=-205747591, message=args, random_id=0)

        # 3. Быстрый цикл ожидания любого ответа
        start_wait = time.time()
        while time.time() - start_wait < 20:
            new_hist = vk.messages.getHistory(peer_id=-205747591, count=1)
            if new_hist.get('items'):
                msg = new_hist['items'][0]
                
                # Если пришло новое сообщение от Сотебота — пересылаем
                if msg['id'] > last_msg_id and msg['from_id'] == -205747591:
                    vk.messages.send(
                        peer_id=event.peer_id, 
                        forward_messages=msg['id'], 
                        random_id=0
                    )
                    return
            
            time.sleep(1) # Для обычной команды 1 сек достаточно
