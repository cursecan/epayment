import sys
import time
import telepot
from telepot.loop import MessageLoop
from pprint import pprint
import requests
import json
import re

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type == 'text' and chat_type == 'private':
        message = msg['text']
        
        if message == '/start':
            respond_msg = '*Pake Dulu Baru Bayar*\nNikmati pengisian pulsa all operator s/d Rp 50.000 tanpa pengisian saldo terlebih dahulu.'
            bot.sendMessage(chat_id, respond_msg, parse_mode='Markdown')
            return 0

        ms_group  = re.match(r'^([/#]\w+) (\d+)', message)
        try :
            command = ms_group.group(1)
            var = ms_group.group(2)

            if command in ['/pulsa', '#pulsa']:
                ivar = int(var)
                if ivar < 1000:
                    ivar *= 1000
                data = {
                    'teleuser': chat_id,
                    'amount': ivar
                }

                r = requests.post('http://127.0.0.1/api/pulsa/topup/', data=json.dumps(data), headers={'Content-Type':'application/json'})
                
                result = r.json()
                if 'invalid' in result:
                    respond_msg = 'Permintaan Gagal.'
                else :
                    respond_msg = '*Transaksi {}*\n'.format(result['trx_code'])
                    respond_msg += '_Pembelian {} dengan harga Rp {} pada no. {} sedang diproses. _'.format(result['info'], result['price'],result['phone'])
                    if result['saldo'] > 0 :
                        respond_msg += '_Sisa saldo anda adalah Rp {}._'.format(result['saldo'])
                    else :
                        respond_msg += '_Piutang anda adalah Rp {}._'.format(result['saldo'])
            
            elif command in ['/code', '#code']:
                data = {
                    'telegram': chat_id,
                    'email_confirmed': True
                }
                url = 'http://127.0.0.1/api/manager/profile/update/{}/'.format(var)
                r = requests.put(url, data=json.dumps(data), headers={'Content-Type':'application/json'})
                result = r.json()

                if result.get('detail') == 'Not found.':
                    respond_msg = "Telegram anda telah diregistrasi."
                else :
                    respond_msg = 'Selamat, telegram anda berhasil diregistrasi untuk nomor {}.'.format(result['phone'])

            else :
                respond_msg = "Maaf keyword anda salah."
        except :
            respond_msg = "Maaf keyword yang anda masukan salah."
        bot.sendMessage(chat_id, respond_msg, parse_mode='Markdown')

    # if content_type == 'text':
    #     bot.sendMessage(chat_id, msg['text'])

TOKEN = '433464639:AAFInCWL9F91LVPeABrkgW9OSL_f7GNKysA'  # get token from command-line

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)