import sys
import time
import telepot
import telepot.helper
from pprint import pprint
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, create_open, pave_event_space, include_callback_query_chat_id
)

import requests, re, json

trx_record = telepot.helper.SafeDict()

class Epaybot(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(Epaybot, self).__init__(*args, **kwargs)

        global trx_record
        if self.id in trx_record:
            self._count, self._edit_mgs_ident = trx_record[self.id]
            self._editor = telepot.helper.Editor(self.bot, self._edit_mgs_ident) if self._edit_mgs_ident else None
        else:
            self._count = 0
            self._edit_mgs_ident = None
            self._editor = None

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type == 'text':
            data = msg['text']
            img, capt = data.split(' ', 1)
            bot.sendPhoto(chat_id, img, caption=capt)

        

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        print(query_id, from_id, query_data)
        self.bot.answerCallbackQuery(query_id, text='Ok. Wait to precess.')

    def on__idle(self, event):
        self.close()


    def on_close(self, ex):
        # Save to database
        global trx_record
        trx_record[self.id] = (self._count, self._edit_mgs_ident)



TOKEN = '528057329:AAFBShP7yaoh2ZgOl0Fg4Fzipw1kYitx9Iw'  # get token from command-line

bot = telepot.DelegatorBot(TOKEN, [
    include_callback_query_chat_id(
        pave_event_space())(
            per_chat_id(types=['private']), create_open, Epaybot, timeout=10),
])

MessageLoop(bot).run_as_thread()
print('Listening ...')

while 1:
    time.sleep(10)

