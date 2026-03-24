import time

# ЭТО ДОЛЖНО БЫТЬ ВНЕ ФУНКЦИИ (в самом начале файла)
start_bot_time = time.time()

def handle(vk, event, data, save_func):
    p = data.get("prefix", ".")
    
    if event.text.lower() in [f"{p}пинг", f"{p}ping", f"{p}статус"]:
        # 1. Считаем чистые секунды разницы
        total_seconds = int(time.time() - start_bot_time)
        
        # 2. Раскладываем на компоненты
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        # 3. Ваше оформление
        uptime_str = f"{hours}ч {minutes}м {seconds}с"

        # Дальше ваш код отправки...
        start_time = time.time()
        vk.messages.edit(peer_id=event.peer_id, message="⏳ Замеряю...", message_id=event.message_id)
        ping_ms = round((time.time() - start_time) * 1000)
        
        res = (f"🌕 Понг!\n"
               f"🚀 Задержка: {ping_ms} мс\n"
               f"⏱ Аптайм: {uptime_str}")
        
        vk.messages.edit(peer_id=event.peer_id, message=res, message_id=event.message_id)
