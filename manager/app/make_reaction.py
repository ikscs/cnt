#!/usr/local/bin/python
import os
import json
import hashlib
from datetime import datetime

from db_wrapper import DB
from service_exchange import Service_exchange
from sender import Sender, get_email_cfg
from telegram_bot import TBot

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
        {'point_id': 5, 'point_name': 'Sezon', 'group_name': 'Співробітники', 'reaction_name': 'Nothing', 'face_uuid': '6eff665c0cf24e09a6d180f1e90077fb', 'parent_uuid': '34316fff4388494fb08193502fae939a', 'ts': '2025-12-26T15:12:10.089620', 'name': 'Лариса', 'common_param': {'x': 123}, 'param': {'y': 4561}},
        {'point_id': 5, 'point_name': 'Sezon', 'group_name': 'Співробітники', 'reaction_name': 'Nothing', 'face_uuid': 'c3664862f46b485fbb04e2b4d6e5c8f3', 'parent_uuid': '65d25cd148e6434d8c8d3820168e926a', 'ts': '2025-12-26T15:12:10.089620', 'name': 'Адель', 'common_param': {'x': 123}, 'param': {'y': 4562}},
        {'point_id': 5, 'point_name': 'Sezon', 'group_name': 'Співробітники', 'reaction_name': 'Email1', 'face_uuid': 'aaaaa', 'parent_uuid': 'b', 'ts': '2025-12-26T15:12:10.089620', 'name': 'Адель1', 'common_param': {'x': 123}, 'param': {'y': 4563}},
        {'point_id': 5, 'point_name': 'Sezon', 'group_name': 'Співробітники', 'reaction_name': 'Email1', 'face_uuid': 'cacsac', 'parent_uuid': 'dddb', 'ts': '2025-12-26T15:12:10.089620', 'name': 'Адель2', 'common_param': {'x': 123}, 'param': {'y': 4564}},
        {'point_id': 6, 'point_name': 'Sezon', 'group_name': 'Співробітники', 'reaction_name': 'Nothing', 'face_uuid': '12', 'parent_uuid': '34316fff4388494fb08193502fae939a', 'ts': '2025-12-26T15:12:10.089620', 'name': 'Лариса3', 'common_param': {'x': 123}, 'param': {'y': 4565}},
        {'point_id': 6, 'point_name': 'Sezon', 'group_name': 'Співробітники', 'reaction_name': 'Nothing', 'face_uuid': 'ssssss', 'parent_uuid': '65d25cd148e6434d8c8d3820168e926a', 'ts': '2025-12-26T15:12:10.089620', 'name': 'Адель4', 'common_param': {'x': 123}, 'param': {'y': 4566}},
        {'point_id': 6, 'point_name': 'Sezon', 'group_name': 'Співробітники', 'reaction_name': 'Email1', 'face_uuid': 'aaaaa', 'parent_uuid': 'bdsdds', 'ts': '2025-12-26T15:12:10.089620', 'name': 'Адель5', 'common_param': {'x': 123}, 'param': {'y': 4567}},
        {'point_id': 6, 'point_name': 'Sezon', 'group_name': 'Співробітники', 'reaction_name': 'Email1', 'face_uuid': '11d239efc62142369575a3ece8943031', 'parent_uuid': '65d25cd148e6434d8c8d3820168e926a', 'ts': '2025-12-26T15:12:10.089620', 'name': 'Адель6', 'common_param': {'x': 123}, 'param': {'y': 4568, 'recipient': "t380689005276@gmail.com"}},
        {'point_id': 6, 'point_name': 'Sezon', 'group_name': 'Співробітники', 'reaction_name': 'Email1', 'face_uuid': '14726a4f785a442691d65930c3be3b69', 'parent_uuid': '34316fff4388494fb08193502fae939a', 'ts': '2025-12-26T15:12:20.089620', 'name': 'АдельX', 'common_param': {'x': 123}, 'param': {'y': 4568, 'recipient': "t380689005276@gmail.com"}},
        {'point_id': 6, 'point_name': 'Sezon', 'group_name': 'Співробітники', 'reaction_name': 'Telegram1', 'face_uuid': '11d239efc62142369575a3ece8943031', 'parent_uuid': '65d25cd148e6434d8c8d3820168e926a', 'ts': '2025-12-26T15:12:10.089620', 'name': 'Адель6', 'common_param': {'x': 123}, 'param': {'y': 4569, "token": "qqqqqqqqqqqqqqqqqqq", "chat_id": "-1234"}},
    ]
    make_reaction(cursor, reactions)

def exec_reaction(cursor, se, point_id, reaction, param, values):
    if reaction not in ('Nothing', 'Email', 'Telegram'):
        print(f'Unknown reaction: {reaction}')
        return
    if reaction == 'Nothing':
        return

    photo = dict()
    for row in values:
        if row['face_uuid'] not in photo:
            photo[row['face_uuid']] = get_photo_by_face_uuid(se, row['face_uuid'])
        if row['parent_uuid'] not in photo:
            photo[row['parent_uuid']] = get_photo_by_parent_uuid(cursor, row['parent_uuid'])

    data = []
    for e in values:
        try:
            t = datetime.fromisoformat(e['ts']).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as err:
            t = e['ts'] if e['ts'] else ''
        data.append({'ts': t, 'point_name': e['point_name'], 'group_name': e['group_name'], 'name': e['name'], 'face': photo[e['face_uuid']], 'parent': photo[e['parent_uuid']], })

    if reaction == 'Email':
        result, sender = get_sender(cursor)
        if not result or not sender:
            return

        sender.recipient = param.get('recipient', sender.recipient)

        if not sender.recipient or '@' not in sender.recipient:
            return

        email_reaction(sender, param, data)
        return
    elif reaction == 'Telegram':
        bot = get_telegram(param)

        telegram_reaction(bot, param, data)
        return

def get_photo_by_face_uuid(se, uuid):
    result = se.get_img(uuid)

    return result

def get_photo_by_parent_uuid(cursor, uuid):
    sql = 'SELECT photo FROM face_referer_data WHERE face_uuid=%s;'

    cursor.execute(sql, [uuid, ])
    result = cursor.fetchone()

    return result[0] if result else None

def email_reaction(sender, param, data):
    print('Email')
    attachment_data = []
    attachment_name = []

    subject = param.get('subject', "Face match event default")

    html = f'<div style="max-width: 300px;"><table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">\n'

    for n, e in enumerate(data, 1):
        attachment_name.append(e['name'] + f'_event_{n}.jpg')
        attachment_name.append(e['name'] + '.jpg')
        attachment_data.append(e['face'])
        attachment_data.append(e['parent'])

        html += '<tr><td align="center" style="padding: 0 20px;">'
        html += f'<h1>{e["point_name"]}: {e["ts"]}</h1></td>'
        html += '<td align="center" style="padding: 0 20px;">'
        html += f'<td><h1>{e["group_name"]}: <i>{e["name"]}</i></h1></td></tr>'

        html += '<tr><td align="center" style="padding: 0 20px;">'
        html += f'<img src="cid:att{2*n-1}" width="150" style="display: block; width: 100%; max-width: 150px; height: auto;"></td>'
        html += '<td align="center" style="padding: 0 20px;">'
        html += f'<img src="cid:att{2*n}" width="150" style="display: block; width: 100%; max-width: 150px; height: auto;"></td></tr>\n'
    html += '</table></div>'

    sender.send_email(subject, body=None, html=html, attachment_data=attachment_data, attachment_name=attachment_name)


def telegram_reaction(bot, param, data):
    print('Telegram')

    for e in data:
        bot.send_photo(photo=e['face'], caption=f'{e["point_name"]}: {e["ts"]}')
        bot.send_photo(photo=e['parent'], caption=f'Match: {e["group_name"]} - {e["name"]}')

def make_reaction(cursor, reactions):
    se = Service_exchange()

    react = AutoDict()
    hash_list = dict()
    for r in reactions:
        param = r['common_param'] | r['param']
        param_hash = dict_hash(param)
        if param_hash not in react[r['point_id']][r['reaction_name']]:
            hash_list[param_hash] = param
            react[r['point_id']][r['reaction_name']][param_hash] = []
        react[r['point_id']][r['reaction_name']][param_hash].append({'face_uuid': r['face_uuid'], 'parent_uuid': r['parent_uuid'], 'ts': r['ts'], 'name': r['name'], 'point_name': r['point_name'], 'group_name': r['group_name'], })

    for point_id, v1 in react.items():
        for reaction, v2 in v1.items():
            for param_hash, values in v2.items():
                param = hash_list[param_hash]
                exec_reaction(cursor, se, point_id, reaction, param, values)

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
