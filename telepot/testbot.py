import sys
import time
import telepot
from telepot.loop import MessageLoop
from pprint import pprint
import requests, schedule
import json
import re


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)


def job():
    bot.sendMessage(126681118, 'This Message')


TOKEN = '528057329:AAFBShP7yaoh2ZgOl0Fg4Fzipw1kYitx9Iw'  # get token from command-line

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
print ('Listening ...')

schedule.every().minute.do(job)

# Keep the program running.
while 1:
    schedule.run_pending()
    time.sleep(10)