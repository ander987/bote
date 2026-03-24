from deep_translator import GoogleTranslator

def handle(vk, event, data, save_func):
    p = data.get("prefix", ".")
    msg_low = event.text.lower()

    # Проверяем новые варианты команды
    if msg_low.startswith(f"{p}перевод") or msg_low.startswith(f"{p}переведи"):
        # Определяем, какую именно команду использовали, чтобы правильно отрезать текст
        if msg_low.startswith(f"{p}перевод"):
            cmd_len = len(p) + 7
        else:
            cmd_len = len(p) + 8

        # Получаем данные о сообщении (для работы с реплаями)
        msg_full = vk.messages.getById(message_ids=event.message_id)['items'][0]
        
        target_text = ""
        
        # 1. Если это ответ на сообщение
        if msg_full.get('reply_message'):
            target_text = msg_full['reply_message']['text']
        # 2. Если есть пересланные сообщения
        elif msg_full.get('fwd_messages'):
            target_text = msg_full['fwd_messages'][0]['text']
        # 3. Если текст написан сразу после команды
        else:
            target_text = event.text[cmd_len:].strip()

        if not target_text:
            vk.messages.edit(
                peer_id=event.peer_id, 
                message=f"⚠️ Напишите текст после команды (например: {p}перевод hello) или ответьте на сообщение.", 
                message_id=event.message_id
            )
            return

        try:
            # Редактируем сообщение, чтобы показать процесс
            vk.messages.edit(peer_id=event.peer_id, message="🔄 Перевожу...", message_id=event.message_id)
            
            # Перевод на русский
            translated = GoogleTranslator(source='auto', target='ru').translate(target_text)
            
            res = f"🌐 Результат перевода:\n——\n{translated}"
            vk.messages.edit(peer_id=event.peer_id, message=res, message_id=event.message_id)
            
        except Exception as e:
            vk.messages.edit(peer_id=event.peer_id, message=f"❌ Ошибка: {e}", message_id=event.message_id)