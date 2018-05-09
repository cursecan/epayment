import requests
import json
import re

def saldo(bot, chat_id, base_url):
    url = base_url+'api/manager/user/?t='+str(chat_id)
    r = requests.get(url, headers={'Content-Type':'application/json'})
    rson = r.json()

    msg_out = '_User tidak terdaftar atau tersinkronisasi dengan telegram_'
    if rson['count'] == 1:
        saldo = rson['results'][0]['saldo']
        msg_out = '_Yth. Pelanggan, saldo/tagihan anda adalah Rp {}_.'.format(saldo)

    bot.sendMessage(chat_id, msg_out, parse_mode='Markdown')


def reguser(bot, chat_id, base_url, v):
    data = {
        'telegram': chat_id,
        'email_confirmed': True
    }
    url = base_url+'api/manager/profile/update/{}/'.format(v[1])
    r = requests.put(url, data=json.dumps(data), headers={'Content-Type':'application/json'})
    result = r.json()

    if result.get('detail') == 'Not found.':
        respond_msg = "Maaf token yang anda masukan salah."
    else :
        respond_msg = 'Selamat, telegram anda berhasil diregistrasi untuk nomor {}.'.format(result['phone'])

    bot.sendMessage(chat_id, respond_msg, parse_mode='Markdown')