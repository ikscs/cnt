#!/usr/local/bin/python
import os
import json
import hashlib
from datetime import datetime

from db_wrapper import DB
from service_exchange import Service_exchange
from sender import Sender, get_email_cfg
from telegram_bot import TBot

import base64

class AutoDict(dict):
    def __missing__(self, k):
        self[k] = AutoDict()
        return self[k]

def dict_hash(dictionary):
    encoded_dict = json.dumps(dictionary, sort_keys=True).encode('utf-8')
    dhash = hashlib.md5(encoded_dict)
    return dhash.hexdigest()

def main(cursor):
    reactions = [
        {'origin_id': 5, 'origin_name': 'Sezon', 'group_name': 'Співробітники', 'reaction_name': 'Email', 'obj_uuid': 'aaaaa', 'context': 'b', 'ts': '2025-12-26T15:12:10.089620', 'name': 'Адель1', 'common_param': {'x': 123}, 'param': {'y': 4563}},
        {'origin_id': 5, 'origin_name': 'Sezon', 'group_name': 'Співробітники', 'reaction_name': 'Email', 'obj_uuid': 'cacsac', 'context': 'dddb', 'ts': '2025-12-26T15:12:10.089620', 'name': 'Адель2', 'common_param': {'x': 123}, 'param': {'y': 4564}},
        {'origin_id': 6, 'origin_name': 'Sezon', 'group_name': 'Співробітники', 'reaction_name': 'Email', 'obj_uuid': 'aaaaa', 'context': 'bdsdds', 'ts': '2025-12-26T15:12:10.089620', 'name': 'Адель5', 'common_param': {'x': 123}, 'param': {'y': 4567}},
        {'origin_id': 6, 'origin_name': 'Sezon', 'group_name': 'Співробітники', 'reaction_name': 'Email', 'obj_uuid': '11d239efc62142369575a3ece8943031', 'context': '65d25cd148e6434d8c8d3820168e926a', 'ts': '2025-12-26T15:12:10.089620', 'name': 'Адель6', 'common_param': {'x': 123}, 'param': {'subject': "Face alert1", 'y': 4568, 'recipient': "user_123@mailinator.com"}},
        {'origin_id': 6, 'origin_name': 'Sezon', 'group_name': 'Співробітники', 'reaction_name': 'Email', 'obj_uuid': '14726a4f785a442691d65930c3be3b69', 'context': '34316fff4388494fb08193502fae939a', 'ts': '2025-12-26T15:12:20.089620', 'name': 'АдельX', 'common_param': {'x': 123}, 'param': {'subject': "Face alert2", 'y': 4568, 'recipient': "user_123@mailinator.com"}},
        {'origin_id': 6, 'origin_name': 'Sezon', 'group_name': 'Співробітники', 'reaction_name': 'Telegram', 'obj_uuid': '11d239efc62142369575a3ece8943031', 'context': '65d25cd148e6434d8c8d3820168e926a', 'ts': '2025-12-26T15:12:10.089620', 'name': 'Адель6', 'common_param': {'x': 123}, 'param': {'y': 4569, "token": "qqqqqqqqqqqqqqqqqqq", "chat_id": "-1234"}},
    ]
    app_id = 'mutant'

    reactions = [
        {'origin_id': 181, 'origin_name': '1Demo камера', 'group_name': None, 'reaction_name': 'Email', 'obj_uuid': 'a71fc0b78ad44aad9f9395f9facf48bb', 'context': 'BB1234BB', 'ts': '2026-02-16 15:23:46+02', 'name': 'Mr. X. Ferrari', 'common_param': {'x': 123}, 'param': {'subject': "Vehicle alert", 'recipient': "user_123@mailinator.com"}},
        {'origin_id': 188, 'origin_name': '2Нова камера', 'group_name': None, 'reaction_name': 'Email', 'obj_uuid': 'Lg4AAwAA4A8AAAUA', 'context': 'KA9655BH', 'ts': '2026-02-02 15:23:46+02', 'name': 'Нова пошта. Бус', 'common_param': {'x': 123}, 'param': {'y': 4563, 'recipient': "user_123@mailinator.com"}},
        {'origin_id': 188, 'origin_name': '3Нова камера', 'group_name': None, 'reaction_name': 'Email', 'obj_uuid': 'Lg4AAwAA4A8AAAUA', 'context': 'KA9655BH', 'ts': '2026-02-02 15:24:46+02', 'name': 'Нова пошта. Бус', 'common_param': {'x': 123}, 'param': {'y': 4563, 'recipient': "user_123@mailinator.com"}},
        {'origin_id': 189, 'origin_name': '4Нова камера', 'group_name': None, 'reaction_name': 'Email', 'obj_uuid': 'Lg4AAwAA4A8AAAUA2', 'context': 'KA9655BH', 'ts': '2026-02-02 15:25:46+02', 'name': 'Нова пошта. Бус', 'common_param': {'x': 123}, 'param': {'y': 4563, 'recipient': "user_123@mailinator.com"}},
        {'origin_id': 188, 'origin_name': '5Нова камера', 'group_name': None, 'reaction_name': 'Email', 'obj_uuid': 'Lg4AAwAA4A8AAAUA3', 'context': 'KA9655BH', 'ts': '2026-02-02 15:23:46+02', 'name': 'Нова пошта. Бус', 'common_param': {'x': 123}, 'param': {'y': 4563, 'recipient': "user_123@mailinator.com"}},
        {'origin_id': 181, 'origin_name': '6Нова камера', 'group_name': None, 'reaction_name': 'Telegram', 'obj_uuid': 'a71fc0b78ad44aad9f9395f9facf48bb', 'context': 'BB1234BB', 'ts': '2026-02-02 15:24:46+02', 'name': 'Mr. Y. Ferrari', 'common_param': {'x': 123, "token": "qwerty"}, 'param': {'y': 4563, "chat_id": "-123456"}},
        {'origin_id': 189, 'origin_name': '7Нова камера', 'group_name': None, 'reaction_name': 'Telegram', 'obj_uuid': 'Lg4AAwAA4A8AAAUA5', 'context': 'KA9655BH', 'ts': '2026-02-02 15:25:46+02', 'name': 'Нова пошта. Бус', 'common_param': {'x': 123, "token": "qwerty"}, 'param': {'y': 4563, "chat_id": "-123456"}},
    ]
    app_id = 'lpr'

    make_reaction(cursor, app_id, reactions)

def exec_reaction_pcnt(cursor, se, reaction, param, values):
    result, bot = load_bot(cursor, reaction, param)
    if not result:
        return

    photo = dict()
    for row in values:
        if row['obj_uuid'] not in photo:
            photo[row['obj_uuid']] = get_photo_by_face_uuid(se, row['obj_uuid'])
        if row['context'] not in photo:
            photo[row['context']] = get_photo_by_parent_uuid(cursor, row['context'])

    data = []
    for e in values:
        try:
            t = datetime.fromisoformat(e['ts']).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as err:
            t = e['ts'] if e['ts'] else ''
        data.append({'ts': t, 'origin_name': e['origin_name'], 'group_name': e['group_name'], 'name': e['name'], 'obj_uuid': photo[e['obj_uuid']], 'context': photo[e['context']], })

    if reaction == 'Email':
        email_reaction_pcnt(bot, param, data)
    elif reaction == 'Telegram':
        telegram_reaction_pcnt(bot, param, data)

def exec_reaction_lpr(cursor, se, reaction, param, values):
    result, bot = load_bot(cursor, reaction, param)
    if not result:
        return

    photo = dict()
    for row in values:
        if row['obj_uuid'] not in photo:
            photo[row['obj_uuid']] = get_lpr_photo_by_uuid(cursor, row['origin_id'], row['obj_uuid'])

    data = []
    for e in values:
        try:
            t = datetime.fromisoformat(e['ts']).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as err:
            t = e['ts'] if e['ts'] else ''
        data.append({'ts': t, 'origin_name': e['origin_name'], 'group_name': e['group_name'], 'name': e['name'], 'obj_uuid': photo[e['obj_uuid']], 'context': e['context'], })

    if reaction == 'Email':
        email_reaction_lpr(bot, param, data)
    elif reaction == 'Telegram':
        telegram_reaction_lpr(bot, param, data)

def get_lpr_photo_by_uuid(cursor, origin_id, uuid):
    sql = 'SELECT * FROM lpr.get_event_images(%s, %s);'
    cursor.execute(sql, [origin_id, uuid])
    result = cursor.fetchone()

    if not result:
        return None
    if not result[0].get('result'):
        return None

    b64 = result[0].get('background')
    if not b64:
        return None

    try:
        bytes = base64.b64decode(b64)
    except Exception as err:
        return None

    return bytes

def load_bot(cursor, reaction, param):
    #Load config
    if reaction == 'Email':
        result, bot = get_sender(cursor)
        if not result or not bot:
            return False, None
        bot.recipient = param.get('recipient', bot.recipient)
        if not bot.recipient or '@' not in bot.recipient:
            return False, None
    elif reaction == 'Telegram':
        bot = get_telegram(param)
        if not bot:
            return False, None
    return True, bot

def exec_reaction(cursor, se, app_id, reaction, param, values):
    if reaction not in ('Email', 'Telegram'):
        print(f'Unknown reaction: {reaction}')
        return

    if app_id not in ('mutant', 'lpr'):
        print(f'Unknown app_id: {app_id}')
        return

    #Chose app_id
    if app_id == 'mutant':
        exec_reaction_pcnt(cursor, se, reaction, param, values)
    elif app_id == 'lpr':
        exec_reaction_lpr(cursor, se, reaction, param, values)

def get_photo_by_face_uuid(se, uuid):
    result = se.get_img(uuid)
    return result

def get_photo_by_parent_uuid(cursor, uuid):
    sql = 'SELECT photo FROM face_referer_data WHERE face_uuid=%s;'

    cursor.execute(sql, [uuid, ])
    result = cursor.fetchone()

    return result[0] if result else None

def email_reaction_pcnt(sender, param, data):
    print('Email')
    attachment_data = []
    attachment_name = []

    subject = param.get('subject', "Face match event alert")

    html = f'<div style="max-width: 320px;"><table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">\n'

    for n, e in enumerate(data, 1):
        attachment_name.append(e['name'] + f'_event_{n}.jpg')
        attachment_name.append(e['name'] + '.jpg')
        attachment_data.append(e['obj_uuid'])
        attachment_data.append(e['context'])

        html += '<tr><td align="center" style="padding: 0 10px;">'
        html += f'<h1>{e["origin_name"]}: {e["ts"]}</h1></td>'
        html += '<td align="center" style="padding: 0 10px;">'
        html += f'<h1>{e["group_name"]}: <i>{e["name"]}</i></h1></td></tr>\n'

        html += '<tr>\n'
        html += '<td align="center" style="padding: 0 10px;">'
        html += f'<img src="cid:att{2*n-1}" height="150" style="display: block; width: 100%; max-width: 150px; width: auto;"></td>\n'
        html += '<td align="center" style="padding: 0 10px;">'
        html += f'<img src="cid:att{2*n}" height="150" style="display: block; width: 100%; max-width: 150px; width: auto;"></td>\n'
        html += f'</tr>\n'

        html += '<tr><td colspan="2"><hr></td></tr>\n'

    html += '</table></div>'

    sender.send_email(subject, body=None, html=html, attachment_data=attachment_data, attachment_name=attachment_name)

def email_reaction_lpr(sender, param, data):
    print('Email')
    attachment_data = []
    attachment_name = []

    subject = param.get('subject', "Vehicle event alert")

    html = f'<div style="max-width: 320px;"><table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">\n'

    for n, e in enumerate(data, 1):
        attachment_name.append(e['name'] + f'_event_{n}.jpg')
        attachment_data.append(e['obj_uuid'])

        html += '<tr><td align="center" style="padding: 0 10px;">'
        html += f'<h1>{e["origin_name"]}<br>{e["context"]}<br>{e["name"]}<br>{e["ts"]}</h1></td>'
        html += f'</tr>\n'

        html += '<tr>\n'
        html += '<td align="center" style="padding: 0 10px;">'
        html += f'<img src="cid:att{n}" height="150" style="display: block; width: 100%; max-width: 150px; width: auto;"></td>\n'
        html += f'</tr>\n'

        html += '<tr><td><hr></td></tr>\n'

    html += '</table></div>'

    sender.send_email(subject, body=None, html=html, attachment_data=attachment_data, attachment_name=attachment_name)

def telegram_reaction_pcnt(bot, param, data):
    print('Telegram')

    for e in data:
        bot.send_photo(photo=e['obj_uuid'], caption=f'{e["origin_name"]}: {e["ts"]}')
        bot.send_photo(photo=e['context'], caption=f'Match: {e["group_name"]} - {e["name"]}')

def telegram_reaction_lpr(bot, param, data):
    print('Telegram')

    for e in data:
        bot.send_photo(photo=e['obj_uuid'], caption=f'{e["origin_name"]}\n{e["context"]}\n{e["name"]}\n{e["ts"]}')

def make_reaction(cursor, app_id, reactions):
    se = Service_exchange()

    react = AutoDict()
    hash_list = dict()
    for r in reactions:
        param = r['common_param'] | r['param']
        param_hash = dict_hash(param)
        if param_hash not in react[r['origin_id']][r['reaction_name']]:
            hash_list[param_hash] = param
            react[r['origin_id']][r['reaction_name']][param_hash] = []
        react[r['origin_id']][r['reaction_name']][param_hash].append({'origin_id': r['origin_id'], 'obj_uuid': r['obj_uuid'], 'context': r['context'], 'ts': r['ts'], 'name': r['name'], 'origin_name': r['origin_name'], 'group_name': r['group_name'], })

    for origin_id, v1 in react.items():
        for reaction, v2 in v1.items():
            for param_hash, values in v2.items():
                param = hash_list[param_hash]
                exec_reaction(cursor, se, app_id, reaction, param, values)

    return 'Ok'

def get_sender(cursor):
    email_cfg = get_email_cfg(cursor)
    if not email_cfg:
        return False, "Configuration error"

    sender = Sender(email_cfg)
    return True, sender

def get_telegram(param):
    credentials = {'TELEGRAM_TOKEN': param.get('token'), 'TELEGRAM_CHAT_ID': param.get('chat_id')}
    bot = TBot(credentials)
    return bot

if __name__ == "__main__":
    from dotenv import load_dotenv, dotenv_values
    load_dotenv()
    load_dotenv('.env_telegram')

    db = DB()
    db.open()

    main(db.cursor)

    db.close()
