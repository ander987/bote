import random

# Функция для тебя (с удалением команды)
def handle(vk, event, data, save_func):
    p = data.get("prefix", ".")
    trigger = f"{p}а повтори"
    
    # Проверяем, что сообщение начинается с команды и в нем есть перенос строки
    if event.text.lower().startswith(trigger) and "\n" in event.text:
        # [1] берет всё, что ИДЕТ ПОСЛЕ первого переноса строки
        txt = event.text.split("\n", 1)[1].strip()
        
        if txt:
            # Отправляем повтор
            vk.messages.send(peer_id=event.peer_id, message=txt, random_id=0)
            # Удаляем твою команду для всех
            vk.messages.delete(message_ids=event.message_id, delete_for_all=1)

# Функция для доверенных из списка "довы"
def handle_user(vk, event, data):
    p = data.get("prefix", ".")
    trigger = f"{p}а повтори"
    
    # Проверка для друзей (также с префиксом и переносом строки)
    if event.text.lower().startswith(trigger) and "\n" in event.text:
        # [1] берет текст после команды
        txt = event.text.split("\n", 1)[1].strip()
        
        if txt:
            # Просто повторяем (чужие сообщения бот удалить не может)
            vk.messages.send(
                peer_id=event.peer_id, 
                message=txt, 
                random_id=random.getrandbits(64)
            )
