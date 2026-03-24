import random

def handle(vk, event, data, save_func):
    p = data.get("prefix", ".")
    msg = event.text
    msg_l = msg.lower()

    # Добавить ГС
    if msg_l.startswith(f"{p}+гс"):
        msg_full = vk.messages.getById(message_ids=event.message_id)['items'][0]
        reply = msg_full.get('reply_message') or (msg_full['fwd_messages'][0] if msg_full.get('fwd_messages') else None)
        
        if not reply or 'audio_message' not in str(reply.get('attachments')):
            vk.messages.edit(peer_id=event.peer_id, message="⚠️ Ответь на ГС!", message_id=event.message_id)
            return

        att = ""
        for a in reply['attachments']:
            if a['type'] == 'audio_message':
                am = a['audio_message']
                att = f"audio_message{am['owner_id']}_{am['id']}"
                if 'access_key' in am:
                    att += f"_{am['access_key']}"
                break

        parts = msg[len(p)+3:].split('|')
        name = parts[0].strip().lower()
        cat = parts[1].strip().lower() if len(parts) > 1 else "общие"

        if name:
            data["gs"][name] = {"attach": att, "cat": cat}
            save_func(data)
            vk.messages.edit(peer_id=event.peer_id, message=f"✅ ГС '{name}' сохранено в '{cat}'", message_id=event.message_id)

    # Список ГС 
    elif msg_l.startswith(f"{p}гсы"):
        cat_f = msg_l[len(p)+3:].strip().lower()
        if not data["gs"]:
            vk.messages.edit(peer_id=event.peer_id, message="📋 Пусто", message_id=event.message_id)
            return
        
        cats = {}
        for n, d in data["gs"].items():
            c = d.get('cat', 'общие').lower()
            cats.setdefault(c, []).append(n)
        
        if not cat_f or cat_f not in cats:
            res = "🎤 Список ГС (папки):"
            for c in cats:
                res += f"\n📂 {c.upper()} ({len(cats[c])} шт.)"
            res += f"\n\n🔎 Чтобы открыть: {p}гсы [папка]"
        else:
            res = f"📂 {cat_f.upper()}:\n— " + "\n— ".join(cats[cat_f])
        
        vk.messages.edit(peer_id=event.peer_id, message=res, message_id=event.message_id)

    # Удалить ГС
    elif msg_l.startswith(f"{p}-гс"):
        name = msg_l[len(p)+3:].strip().lower()
        if name in data["gs"]:
            del data["gs"][name]
            save_func(data)
            vk.messages.edit(peer_id=event.peer_id, message=f"❌ ГС '{name}' удалено.", message_id=event.message_id)

    # Отправка ГС по названию: {префикс}гс название
    elif msg_l.startswith(f"{p}гс "):
        name = msg_l[len(p)+3:].strip().lower()
        gs_item = data.get("gs", {}).get(name)
        
        if gs_item:
            try:
                # ВАЖНО: меняем audio_message на doc, иначе VK вернет Internal Error
                final_attach = gs_item["attach"].replace("audio_message", "doc")
                
                vk.messages.send(
                    peer_id=event.peer_id, 
                    attachment=final_attach, 
                    random_id=random.getrandbits(31)
                )
                
                try:
                    vk.messages.delete(message_ids=event.message_id, delete_for_all=1)
                except:
                    pass
            except Exception as e:
                print(f"Ошибка отправки ГС: {e}")
