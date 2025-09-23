#encoding: utf-8
import telebot
import os
from dotenv import dotenv_values

class TBot():
    def __init__(self, credentials={}):
        if not credentials:
            credentials['TELEGRAMM_TOKEN'] = os.environ.get('TELEGRAMM_TOKEN')
            credentials['TELEGRAMM_CHAT_ID'] = os.environ.get('TELEGRAMM_CHAT_ID')
            if not credentials['TELEGRAMM_TOKEN']:
                credentials = dotenv_values('.env_telegramm')

        self.token = credentials['TELEGRAMM_TOKEN']
        self.chat_id = credentials['TELEGRAMM_CHAT_ID']
        self.bot = telebot.TeleBot(self.token)

    def send_message(self, text):
        self.bot.send_message(self.chat_id, text=text, parse_mode='html', disable_web_page_preview=True)

if __name__ == '__main__':
    credentials = dotenv_values('.env_telegramm')

    bot = TBot(credentials)

    message = {'db': 1.0242958068847656, 'tmp': 6.4849853515625e-05}

    text = f'<b>Hello</b>\n'
    for k, v in message.items():
        text += f'{k}: {v}\n'

    #bot.send_message(CHAT_ID, text=text, parse_mode='html', disable_web_page_preview=True)
    #bot.send_message(CHAT_ID, "🔴 ALERT: System status is RED", parse_mode="HTML")

    #bot.edit_message_text("🟢 OK: System running normally", CHAT_ID, MESSAGE_ID)
