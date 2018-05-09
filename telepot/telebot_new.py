import sys
import time
import telepot
from telepot.loop import MessageLoop
from pprint import pprint
import re

import pulsa, saldo, admin

base_url = 'http://127.0.0.1:8000/'

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type == 'text' and chat_type == 'private':
        message = msg['text']
        
        if message == '/start':
            respond_msg = '*Pake Dulu Baru Bayar*\nNikmati pengisian pulsa all operator s/d Rp 50.000 tanpa pengisian saldo terlebih dahulu.'
            bot.sendMessage(chat_id, respond_msg, parse_mode='Markdown')
            return 0
        if message == '/saldo':
            saldo.saldo(bot, chat_id, base_url)
            return 0
        if '/news' in message:
            n, content = message.split(' ',1)
            admin.news(bot, base_url, content)
            return 0

        ms_raw = re.match(r'^[/#](\w+) (\d+)', message)
        if ms_raw:
            v = ms_raw.groups()
            if v[0] == 'pulsa':
                pulsa.topup(bot,chat_id, base_url, v)
                return 0

            if v[0] == 'code':
                saldo.reguser(bot, chat_id, base_url, v)
                return 0

TOKEN = '433464639:AAFInCWL9F91LVPeABrkgW9OSL_f7GNKysA'  # get token from command-line

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)