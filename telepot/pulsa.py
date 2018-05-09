import requests
import json
import re

def topup(bot, chat_id, base_url, v):
    url = base_url+'api/manager/user/?t='+str(chat_id)
    r = requests.get(url, headers={'Content-Type':'application/json'})
    rson = r.json()

    # cek user regitered
    if rson['count'] == 1:
        user_id = rson['results'][0]['id']
        phone = rson['results'][0]['phone']
        prefix = phone[:4]
        nominal = v[1]
        if nominal < 1000:
            nominal *= 1000
            
        url = base_url+'api/pulsa/produk/?p={0}&n={1}'.format(prefix, v[1])
        r = requests.get(url, headers={'Content-Type':'application/json'})
        rson = r.json()

        # cek produk exists
        if rson['count'] > 0:
            produk_id = rson['results'][0]['id']
            url = base_url+'api/pulsa/topup/'
            payload = {
                'user' : user_id,
                'produk' : produk_id,
                'phone' : phone,
            }
            r = requests.post(url, data=json.dumps(payload), headers={'Content-Type':'application/json'})
            rson = r.json()
            if rson['valid'] :
                msg_out = '*Transaksi {}*\n'.format(rson['trx'])
                msg_out += '_Pembelian {} dengan harga Rp {} untuk nomor {} berhasil._ '.format(rson['produk'], rson['price'], rson['phone'])
                msg_out += '_Saldo anda saat ini adalah Rp {}._'.format(rson['saldo'])
            
            else :
                msg_out = '_{}_'.format(rson['info'])
        else :
            msg_out = '_Produk tidak ditemukan, silahkan pilih nominal lain._'

    else:
        msg_out = '_User tidak terdaftar atau tersinkronisasi dengan telegram_'

    bot.sendMessage(chat_id, msg_out, parse_mode='Markdown')