#encoding: utf-8
import telebot
import os
import json

from dotenv import dotenv_values, load_dotenv
from db_wrapper import DB

class TBot():
    def __init__(self, credentials={}):
        if not credentials:
            credentials = self.load_credentials_from_db()

        if not credentials['TELEGRAM_TOKEN']:
            self.bot = None
            return

        self.token = credentials['TELEGRAM_TOKEN']
        self.chat_id = credentials['TELEGRAM_CHAT_ID']
        self.bot = telebot.TeleBot(self.token)

    def load_credentials_from_db(self):
        load_dotenv()
        db = DB()
        db.open()

        telegram_cfg = get_telegram_cfg(db.cursor)

        db.close()
        return telegram_cfg

    def send_message(self, text):
        if self.bot:
            self.bot.send_message(self.chat_id, text=text, parse_mode='html', disable_web_page_preview=True)

    def send_photo(self, photo, caption):
        if self.bot:
            self.bot.send_photo(self.chat_id, photo=photo, caption=caption)

def get_telegram_cfg(cursor):
    sql = "SELECT value FROM pcnt.param WHERE name='telegram_default' AND enabled"
    cursor.execute(sql)
    row = cursor.fetchone()
    if not row:
        return None
    try:
         result = json.loads(row[0]['value'])
    except Exception as err:
        print(err)
        return None

    telegram_cfg = dict()
    try:
        telegram_cfg['TELEGRAM_TOKEN'] = result['token']
        telegram_cfg['TELEGRAM_CHAT_ID'] = result['chat_id']
    except Exception as err:
        print(err)
        return None

    return telegram_cfg

if __name__ == '__main__':
#    credentials = dotenv_values('.env_telegram')

#    bot = TBot(credentials)
    bot = TBot()
    #print(bot.token)

    message = {'db': 1.0242958068847656, 'tmp': 6.4849853515625e-05}

    text = f'<b>Hello</b>\n'
    for k, v in message.items():
        text += f'{k}: {v}\n'

    #bot.send_message(CHAT_ID, text=text, parse_mode='html', disable_web_page_preview=True)
    #bot.send_message(CHAT_ID, "🔴 ALERT: System status is RED", parse_mode="HTML")

    #bot.edit_message_text("🟢 OK: System running normally", CHAT_ID, MESSAGE_ID)
