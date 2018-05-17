import sys
import time
import telepot
import telepot.helper
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, create_open, pave_event_space, include_callback_query_chat_id
)

import requests, re, json

trx_record = telepot.helper.SafeDict()
_URL = 'http://127.0.0.1:8000/'

def group_li(li, n):
    return [li[i:i+n] for i in range(0, len(li), n)]


def all_pulsa_op():
    url = _URL+'api/pulsa/operator/'
    r = requests.get(url)
    rson = r.json()
    return [i['kode'] for i in rson['results']]

def all_pulsa_prod():
    url = _URL+'api/pulsa/produks/'
    r = requests.get(url)
    rson = r.json()
    print('proses request produk')
    return [i['kode_internal'] for i in rson['results']]


def all_etrans_op():
    url = _URL+'api/etrans/operator/'
    r = requests.get(url)
    rson = r.json()
    return [i['kode'] for i in rson['results']]

def all_etrans_prod():
    url = _URL+'api/etrans/produk/'
    r = requests.get(url)
    rson = r.json()
    print('proses request produk')
    return [i['kode_internal'] for i in rson['results']]


PULSA_OP = all_pulsa_op()
PULSA_PROD = all_pulsa_prod()
ETRANS_OP = all_etrans_op()
ETRANS_PROD = all_etrans_prod()


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


    def main_menu(self):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='PULSA', callback_data='pulsa'),
                    InlineKeyboardButton(text='E-PAYMENT', callback_data='etrans')
                ]
            ]
        )
        sent = self.sender.sendMessage('Selamat datang di menu utama, silahkan pilih produk yang anda cari.', reply_markup=keyboard)
        self._editor = telepot.helper.Editor(self.bot, sent)
        self._edit_mgs_ident = telepot.message_identifier(sent)

    def get_all_user(self):
        r = requests.get(_URL+'api/manager/user/')
        return [i['telegram'] for i in r.json()['results']]

    def pulsa_operator(self):
        url = _URL+'api/pulsa/operator/'
        r = requests.get(url)
        rson = r.json()
        board = []
        for i in rson['results']:
            board.append(
                InlineKeyboardButton(text=i.get('operator'), callback_data=i.get('kode'))
            )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard = group_li(board, 3)
        )
        sent = self.bot.editMessageReplyMarkup(self._edit_mgs_ident, reply_markup=keyboard)
        self._editor = telepot.helper.Editor(self.bot, sent)
        self._edit_mgs_ident = telepot.message_identifier(sent)

    def etrans_operator(self):
        url = _URL+'api/etrans/operator/'
        r = requests.get(url)
        rson = r.json()
        board = []
        for i in rson['results']:
            board.append(
                InlineKeyboardButton(text=i.get('operator'), callback_data=i.get('kode'))
            )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard = group_li(board, 3)
        )
        sent = self.bot.editMessageReplyMarkup(self._edit_mgs_ident, reply_markup=keyboard)
        self._editor = telepot.helper.Editor(self.bot, sent)
        self._edit_mgs_ident = telepot.message_identifier(sent)


    def pulsa_produk(self, val):
        url = _URL+'api/pulsa/produks/?op='+val
        r = requests.get(url)
        rson = r.json()
        board = []

        for i in rson['results']:
            board.append(
                InlineKeyboardButton(text=i.get('keterangan'), callback_data=i.get('kode_internal'))
            )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard = group_li(board,2)
        )
        sent = self.bot.editMessageReplyMarkup(self._edit_mgs_ident, reply_markup=keyboard)
        self._editor = telepot.helper.Editor(self.bot, sent)
        self._edit_mgs_ident = telepot.message_identifier(sent)

    def etrans_produk(self, val):
        url = _URL+'api/etrans/produk/?op='+val
        r = requests.get(url)
        rson = r.json()
        board = []

        for i in rson['results']:
            board.append(
                InlineKeyboardButton(text=i.get('keterangan'), callback_data=i.get('kode_internal'))
            )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard = group_li(board,2)
        )
        sent = self.bot.editMessageReplyMarkup(self._edit_mgs_ident, reply_markup=keyboard)
        self._editor = telepot.helper.Editor(self.bot, sent)
        self._edit_mgs_ident = telepot.message_identifier(sent)


    def broadcast_msg(self, msg):
        users = self.get_all_user()
        for u in users :
            try:
                bot.sendMessage(int(u),'*~ News & Information ~*\n{}'.format(msg), parse_mode='Markdown')
            except:
                pass


    def pulsa_harga(self, val):
        url = _URL+'api/pulsa/produks/?kd='+val
        r = requests.get(url)
        rson = r.json()
        self.sender.sendMessage('*Ketik:*\n/{}#no.handphone'.format(rson['results'][0]['kode_internal']), parse_mode='Markdown')

    def etrans_harga(self, val):
        url = _URL+'api/etrans/produk-detail/?kd='+val
        r = requests.get(url)
        rson = r.json()
        self.sender.sendMessage('*Ketik:*\n/{}#no.handphone'.format(rson['results'][0]['kode_internal']), parse_mode='Markdown')



    def _cancel_last(self):
        if self._editor:
            self._editor.editMessageReplyMarkup(reply_markup=None)
            self._editor = None
            self._edit_mgs_ident = None


    def topup_pulsa(self, code, val, chat_id):
        payload = {
            'telegram': chat_id,
            'produk': code,
            'phone': val
        }
        r = requests.post(_URL+'api/pulsa/topup/', data=json.dumps(payload), headers={'Content-Type':'application/json'})
        rson = r.json()
        self.fedback_message(rson)

    def topup_etrans(self, code, val, chat_id):
        payload = {
            'telegram': chat_id,
            'produk': code,
            'phone': val
        }
        r = requests.post(_URL+'api/etrans/topup/', data=json.dumps(payload), headers={'Content-Type':'application/json'})
        rson = r.json()
        self.fedback_message(rson)

    def fedback_message(self, rson):
        if rson['code'] == 0:
            self.sender.sendMessage(
                '*Transaksi {}*\n_Pembelian {} dengan harga Rp {} untuk nomor {} dalam process. Saldo anda saat ini adalah Rp {}, terimakasih~_'.format(
                    rson.get('trx'), rson.get('produk'), rson.get('price'),
                    rson.get('phone'), rson.get('saldo')
                ), parse_mode='Markdown'
            )
        else :
            self.sender.sendMessage(
                '*Transaksi {}*\n_{}_'.format(
                    rson.get('trx', 'Gagal'), rson.get('status')
                ),  parse_mode='Markdown'
            )


    def integrate_telegram(self, chat_id, val):
        payload = {
            'telegram': chat_id,
            'email_confirmed' : True
        }
        r = requests.put(_URL+'api/manager/profile/update/{}/'.format(val), data=json.dumps(payload), headers={'Content-Type':'application/json'})
        rson = r.json()
        result = rson.get('detail', None)
        if result:
            self.sender.sendMessage('Maaf kode yang anda masukan salah, silahkan masukan kode dengan benar.')
        else :
            self.sender.sendMessage('*Sinkronisasi berhasil*, telegram anda telah terdaftar.', parse_mode='Markdown')



    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type != 'text':
            return

        if '/broadcast' in msg['text']:
            code , msg = msg['text'].split(' ', 1)
            self.broadcast_msg(msg)
            return

        com = re.match(r'^/(\w+) (\d+)', msg['text'])
        if com :
            arg1 = com.group(1)
            arg2 = com.group(2)
            if arg1 == 'code':
                    self.integrate_telegram(chat_id, arg2)
                    return

        txt = msg['text'].upper()
        com = re.match(r'^/(\w+)#(\d+)', txt)

        if com :
            arg1 = com.group(1)
            arg2 = com.group(2)

            if arg1 in PULSA_PROD:
                self.topup_pulsa(arg1, arg2, chat_id)
                return

            if arg1 in ETRANS_PROD:
                self.topup_etrans(arg1, arg2, chat_id)
                return
        

        

        self.main_menu()
    

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        print(query_id, from_id, query_data)
        self.bot.answerCallbackQuery(query_id, text='Ok. Wait to precess.')
        if query_data == 'pulsa':
            self.pulsa_operator()
            return

        if query_data == 'etrans':
            self.etrans_operator()
            return

        if query_data in PULSA_OP:
            self.pulsa_produk(val=query_data)
            return

        if query_data in ETRANS_OP:
            self.etrans_produk(val=query_data)
            return

        if query_data in PULSA_PROD:
            self.pulsa_harga(val=query_data)
            return

        if query_data in ETRANS_PROD:
            self.etrans_harga(val=query_data)
            return

    def on__idle(self, event):
        self.close()


    def on_close(self, ex):
        # Save to database
        global trx_record
        trx_record[self.id] = (self._count, self._edit_mgs_ident)



TOKEN = '433464639:AAFInCWL9F91LVPeABrkgW9OSL_f7GNKysA'  # get token from command-line

bot = telepot.DelegatorBot(TOKEN, [
    include_callback_query_chat_id(
        pave_event_space())(
            per_chat_id(types=['private']), create_open, Epaybot, timeout=10),
])

MessageLoop(bot).run_as_thread()
print('Listening ...')

while 1:
    time.sleep(10)

