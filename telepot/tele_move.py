import sys
import time
import telepot
from telepot.loop import MessageLoop
from pprint import pprint
import requests
import json
import re

def get_all_user():
    r = requests.get('http://127.0.0.1/'+'api/manager/user/')
    return [i['telegram'] for i in r.json()['results']]

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    pprint(msg)

TOKEN = '528057329:AAFBShP7yaoh2ZgOl0Fg4Fzipw1kYitx9Iw'  # get token from command-line

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)