import requests
from bs4 import BeautifulSoup
import re

def get_reg_date(user_id):
    try:
        response = requests.get(f'https://vk.com/foaf.php?id={user_id}', timeout=5)
        soup = BeautifulSoup(response.text, 'lxml')
        created = soup.find('ya:created').get('dc:date')
        return f'🗓 Дата регистрации: {created[8:10]}.{created[5:7]}.{created[0:4]}'
    except:
        return "❗️ Ошибка получения даты регистрации"

def handle(vk, event, data, save_func):
    p = data.get("prefix", ".")
    msg_low = event.text.lower()
    
    if msg_low.startswith((f"{p}инфа", f"{p}ктоты")):
        user_id = None
        # Поиск ID
        msg_full = vk.messages.getById(message_ids=event.message_id)['items'][0]
        if msg_full.get('reply_message'):
            user_id = msg_full['reply_message']['from_id']
        elif msg_full.get('fwd_messages'):
            user_id = msg_full['fwd_messages'][0]['from_id']
        
        if not user_id or user_id < 0:
            vk.messages.edit(peer_id=event.peer_id, message="❗️ Необходимо пересланное сообщение или упоминание", message_id=event.message_id)
            return

        try:
            rDate = get_reg_date(user_id)
            info = vk.users.get(user_ids=user_id, fields="sex,is_closed,blacklisted,blacklisted_by_me,status,photo_max_orig,counters,friend_status,city,first_name_abl,last_name_abl,last_seen,online,screen_name,bdate")[0]
            
            # Логика замен из твоего кода
            friend_status = str(info['friend_status']).replace('0', '🚫').replace('1', 'Заявка на рассмотрении.').replace('2', '🔖 Имеется входящая заявка.').replace('3', '✅')
            sexi = str(info['sex']).replace('1', 'Она').replace('2', 'Он').replace('3', 'Не указан')
            sex = str(info['sex']).replace('1', '👩').replace('2', '👨').replace('3', 'Не указан')
            is_closed = "✅" if info['is_closed'] else "🚫"
            blacklisted = "✅" if info['blacklisted'] else "🚫"
            blacklisted_by_me = "✅" if info['blacklisted_by_me'] else "🚫"
            
            if 'last_seen' in info:
                platforms = {1: 'Мобильная версия 📱', 2: 'iPhone 📱', 3: 'iPad 📱', 4: 'Android 📱', 5: 'Windows Phone 📱', 6: 'Windows 10 📱', 7: 'Полная версия сайта 🖥'}
                last_seen = platforms.get(info['last_seen']['platform'], "Неизвестно")
            else:
                last_seen = 'Онлайн скрыт 🔒.'

            count_friends = info.get('counters', {}).get('friends', 'Скрыто 🔒.')
            count_followers = info.get('counters', {}).get('followers', 'Скрыто 🔒.')
            
            # Проверка на доверку в нашей базе
            is_trusted_user = 'Да' if str(user_id) in data.get("trusted", {}) else 'Нет'
            
            # Короткая ссылка на фото
            try:
                photo = vk.utils.getShortLink(url=info['photo_max_orig'])['short_url']
            except:
                photo = info['photo_max_orig']

            res = f"""
Информация о {info['first_name_abl']} {info['last_name_abl']}

🆔: {info['id']}
⚜️ Короткая ссылка: {info.get('screen_name', 'id'+str(user_id))}
⚙️ Имя: {info['first_name']}
⚙️ Фамилия: {info['last_name']}
📱 Онлайн: {'Online' if info['online']==1 else 'Offline'}, {last_seen}
👥 Кол-во друзей: {count_friends}
🔐 Является доверенным пользователем: {is_trusted_user}
{rDate}
🎉 Дата рождения: {info.get('bdate', 'Скрыто 🔒.')}
🌆 Город: {info['city']['title'] if 'city' in info else 'Не указан.'}
👨‍💼 Друзья: {friend_status}
✍🏻 Подписчики: {count_followers}
👨 Пол: {sex}
🔒 Закрытый профиль: {is_closed}
💬 Статус: {info.get('status', 'Пусто')}
🚫 Я в ЧС: {blacklisted}
🚫 {sexi} в ЧС: {blacklisted_by_me}
📷 Фото: {photo}
"""
            vk.messages.edit(peer_id=event.peer_id, message=res, message_id=event.message_id)

        except Exception as e:
            vk.messages.edit(peer_id=event.peer_id, message=f"❗️ Произошла ошибка: {e}", message_id=event.message_id)