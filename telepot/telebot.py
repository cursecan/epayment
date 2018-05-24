import sys
import time
import telepot
import pendulum
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


MAIN_Q = ('PULSA', 'TOPUP', 'LISTRIK')


class Epaybot(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(Epaybot, self).__init__(*args, **kwargs)

        global trx_record
        if self.id in trx_record:
            self._level, self._edit_mgs_ident, self._edit_mgs_ident_2 ,self._code, self._keyboard = trx_record[self.id]
            self._editor = telepot.helper.Editor(self.bot, self._edit_mgs_ident) if self._edit_mgs_ident else None
            self._editor_2 = telepot.helper.Editor(self.bot, self._edit_mgs_ident_2) if self._edit_mgs_ident_2 else None
        else:
            self._level = 0
            self._edit_mgs_ident = None
            self._editor = None
            self._code = None
            self._keyboard = []
            self._editor_2 = None
            self._edit_mgs_ident_2 = None

        self._list_pulsa_op = self.all_pulsa_operator()
        self._list_topup_op = self.all_topup_operator()
        self._list_pulsa_prod = self.all_pulsa_prod()
        self._list_topup_prod = self.all_topup_prod()
        self._list_listrik_prod = self.all_listrik_prod()


    # MENU UTAMA 
    def main_menu(self):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='PULSA & DATA', callback_data='PULSA'),
                    InlineKeyboardButton(text='TOPUP', callback_data='TOPUP')
                ],
                [
                    InlineKeyboardButton(text='CEK SALDO', callback_data='saldo'),
                ]
            ]
        )
        sent = self.sender.sendMessage(
            'Selamat datang di menu utama, silahkan pilih produk yang anda cari.',
            reply_markup=keyboard
        )
        self._editor = telepot.helper.Editor(self.bot, sent)
        self._edit_mgs_ident = telepot.message_identifier(sent)
        self._level = 1
        self._code = None
        self._keyboard = [keyboard]


    # CEK SALDO
    def cek_saldo(self, telid):
        url = _URL+'api/manager/user/?t='+str(telid)
        r = requests.get(url)
        rson = r.json()
        if len(rson) == 1:
            saldo = rson[0]['saldo']
            name = rson[0]['first_name']
            sent = self.sender.sendMessage(
                'Pelanggan Yth, {}\nSaldo simpanan anda saat ini Rp {}'.format(name, saldo)
            )
        else :
            sent = self.sender.sendMessage(
                'Maaf anda belum terdaftar'
            )

        self._editor_2 = telepot.helper.Editor(self.bot, sent)
        self._edit_mgs_ident_2 = telepot.message_identifier(sent)


    # BACK BUTTON
    def return_back(self, keyboard):
        sent = self.bot.editMessageReplyMarkup(self._edit_mgs_ident, reply_markup=keyboard)
        self._editor = telepot.helper.Editor(self.bot, sent)
        self._edit_mgs_ident = telepot.message_identifier(sent)


    # LIST PRODUK LISTRIK
    def all_listrik_prod(self):
        url = _URL+'api/pln/produk/'
        r = requests.get(url)
        return [i['kode_produk'] for i in r.json()]


    # LIST PRODUK PULSA
    def all_pulsa_prod(self):
        url = _URL+'api/pulsa/produks/'
        r = requests.get(url)
        return [i['kode_internal'] for i in r.json()]


    # LIST PRODUK TOPUP
    def all_topup_prod(self):
        url = _URL+'api/etrans/produk/'
        r = requests.get(url)
        return [i['kode_internal'] for i in r.json()]
        

    # LIST ALL OPERATOR
    def all_pulsa_operator(self):
        url = _URL+'api/pulsa/operator/'
        r = requests.get(url)
        list_1 = [i['kode'] for i in r.json()]
        return list_1

    
    # LIST TOPUP OPERATOR
    def all_topup_operator(self):
        url = _URL+'api/etrans/operator/'
        r = requests.get(url)
        list_1 = [i['kode'] for i in r.json()]
        return list_1
    

    # DATAS ALL USER
    def get_all_user(self):
        r = requests.get(_URL+'api/manager/user/')
        return r.json()


    # OPERATOR
    def get_operator(self, qs):
        if qs == 'PULSA':
            url = _URL+'api/pulsa/operator/'
        else :
            url = _URL+'api/etrans/operator/'

        r = requests.get(url)

        board = []
        for i in r.json():
            board.append(
                InlineKeyboardButton(text=i.get('operator'), callback_data=i.get('kode'))
            )

        if qs == 'TOPUP':
            board.append(
                InlineKeyboardButton(text='TOKEN LISTRIK', callback_data='listrik')
            )

        board.append(
            InlineKeyboardButton(text='< BACK >', callback_data='backbutton')
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard = group_li(board, 3)
        )
        sent = self.bot.editMessageReplyMarkup(self._edit_mgs_ident, reply_markup=keyboard)
        self._editor = telepot.helper.Editor(self.bot, sent)
        self._edit_mgs_ident = telepot.message_identifier(sent)
        self._keyboard.append(keyboard)

    
    # ALL PRODUK PULSA
    def pulsa_produk(self, val):
        url = _URL+'api/pulsa/produks/?op='+val
        r = requests.get(url)
        board = []

        for i in r.json():
            board.append(
                InlineKeyboardButton(text=i.get('parse_text'), callback_data=i.get('kode_internal'))
            )

        board.append(
            InlineKeyboardButton(text='< BACK >', callback_data='backbutton')
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard = group_li(board,2)
        )
        sent = self.bot.editMessageReplyMarkup(self._edit_mgs_ident, reply_markup=keyboard)
        self._editor = telepot.helper.Editor(self.bot, sent)
        self._edit_mgs_ident = telepot.message_identifier(sent)
        self._keyboard.append(keyboard)


    def listrik_produk(self):
        url = _URL+'api/pln/produk/'
        r = requests.get(url)
        board = []
        for i in r.json():
            board.append(
                InlineKeyboardButton(text=i.get('parse_text'), callback_data=i.get('kode_produk'))
            )
        
        board.append(
            InlineKeyboardButton(text='< BACK >', callback_data='backbutton')
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard = group_li(board,2)
        )
        sent = self.bot.editMessageReplyMarkup(self._edit_mgs_ident, reply_markup=keyboard)
        self._editor = telepot.helper.Editor(self.bot, sent)
        self._edit_mgs_ident = telepot.message_identifier(sent)
        self._keyboard.append(keyboard)

    

    # ALL PRODUK TOPUP
    def topup_produk(self, val):
        url = _URL+'api/etrans/produk/?op='+val
        r = requests.get(url)
        board = []

        for i in r.json():
            board.append(
                InlineKeyboardButton(text=i.get('parse_text'), callback_data=i.get('kode_internal'))
            )


        board.append(
            InlineKeyboardButton(text='< BACK >', callback_data='backbutton')
        )


        keyboard = InlineKeyboardMarkup(
            inline_keyboard = group_li(board,2)
        )
        sent = self.bot.editMessageReplyMarkup(self._edit_mgs_ident, reply_markup=keyboard)
        self._editor = telepot.helper.Editor(self.bot, sent)
        self._edit_mgs_ident = telepot.message_identifier(sent)
        self._keyboard.append(keyboard)


    # BROADCAST MESSAGE
    def broadcast_msg(self, msg):
        users = self.get_all_user()
        for u in users :
            if u['telegram'] != '':
                try:
                    bot.sendMessage(
                        u['telegram'],
                        msg,
                        parse_mode='HTML'
                    )
                except:
                    pass


    # DETAIL PRODUK PULSA
    def pulsa_detail_prod(self, val):
        url = _URL+'api/pulsa/produks/?kd='+val
        r = requests.get(url)
        rson = r.json()
        info_prod = '<b>{} harga Rp {}.</b>\nKetikan No.Handpone tujuan.\n<i>Contoh : 0822187111</i>'.format(rson[0]['keterangan'], rson[0]['price'])
        sent = self.sender.sendMessage(info_prod, parse_mode='HTML')
        self._editor_2 = telepot.helper.Editor(self.bot, sent)
        self._edit_mgs_ident_2 = telepot.message_identifier(sent)
        

    # DETAIL PRODUK TOPUP
    def topup_detail_prod(self, val):
        url = _URL+'api/etrans/produk-detail/?kd='+val
        r = requests.get(url)
        rson = r.json()
        info_prod = '<b>{} harga Rp {}.</b>\nKetikan No.Handpone tujuan.\n<i>Contoh : 0822187111</i>'.format(rson[0]['keterangan'], rson[0]['price'])
        sent = self.sender.sendMessage(info_prod, parse_mode='HTML')
        self._editor_2 = telepot.helper.Editor(self.bot, sent)
        self._edit_mgs_ident_2 = telepot.message_identifier(sent)


    def listrik_detail_prod(self, val):
        url = _URL+'api/pln/produk/?p='+val
        r = requests.get(url)
        rson = r.json()
        info_prod = '<b>{} harga Rp {}.</b>\nKetikan No.PLN dan No.Handphone dipisah dengan tanda #.\n<i>Contoh : 14021894085#081397382353</i>'.format(rson[0]['nama_produk'], rson[0]['price'])
        sent = self.sender.sendMessage(info_prod, parse_mode='HTML')
        self._editor_2 = telepot.helper.Editor(self.bot, sent)
        self._edit_mgs_ident_2 = telepot.message_identifier(sent)


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


    def topup_listrik(self, code, acc, phone, chat_id):
        payload = {
            'telegram': chat_id,
            'produk': code,
            'account': acc,
            'phone': phone
        }

        r = requests.post(_URL+'api/pln/topup/', data=json.dumps(payload), headers={'Content-Type':'application/json'})
        rson = r.json()
        self.fedback_message(rson)

    # MESSAGE FEEDBACK
    def fedback_message(self, rson):
        if rson['code'] == 0:
            try:
                self.sender.sendMessage(
                    'TRANSAKSI {}\n<i>Pembelian {} dengan harga Rp {} pada nomor {} dalam process. Saldo anda saat ini adalah Rp {}.</i>'.format(
                        rson.get('trx'), rson.get('produk'), rson.get('price'),
                        rson.get('phone'), rson.get('saldo')
                    ), parse_mode='HTML'
                )
            except:
                pass
            try :
                self.sender.sendMessage(
                    rson['struk'], parse_mode='HTML'
                )
            except:
                pass

        else :
            try :
                self.sender.sendMessage(
                    'TRANSAKSI {}\n<i>{}</i>'.format(
                        rson.get('trx', 'GAGAL'), rson.get('status')
                    ),  parse_mode='HTML'
                )
            except:
                pass


    # USER SINCRONIZE TELEGRAM
    def integrate_telegram(self, chat_id, val):
        payload = {
            'telegram': chat_id,
            'email_confirmed' : True
        }

        r = requests.put(_URL+'api/manager/profile/update/{}/'.format(val),
            data=json.dumps(payload),
            headers={'Content-Type':'application/json'}
        )   
        rson = r.json()
        result = rson.get('detail', None)
        if result:
            self.sender.sendMessage(
                'Maaf kode yang anda masukan salah, silahkan masukan kode dengan benar.'
            )
        else :
            self.sender.sendMessage(
                '<b>Sinkronisasi berhasil</b>, telegram anda telah terdaftar.',
                parse_mode='HTML'
            )


    # MAIN ON CHAT
    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type != 'text':
            return

        if '/broadcast' in msg['text']:
            code , data = msg['text'].split(' ', 1)
            self.broadcast_msg(data)
            return

        if '/code' in msg['text']:
            code , data = msg['text'].split(' ', 1)
            self.integrate_telegram(chat_id, data)
            return

        if self._code != None:
            data = msg['text']
            if self._code in self._list_pulsa_prod:
                valid = re.match(r'^0\d+$', data)
                if not valid:
                    self.sender.sendMessage('Silahkan masukan nomor handphone anda dengan benar.')
                    return
                self.sender.sendMessage('Mohon tunggu transaksi anda sedang diproses.')
                self.topup_pulsa(self._code, data, chat_id)
                self._code = None
                self._editor_2 = None
                self._edit_mgs_ident_2 = None
                self.close()
                return
            if self._code in self._list_topup_prod:
                valid = re.match(r'^0\d+$', data)
                if not valid:
                    self.sender.sendMessage('Silahkan masukan nomor handphone anda dengan benar.')
                    return
                self.sender.sendMessage('Mohon tunggu transaksi anda sedang diproses.')
                self.topup_etrans(self._code, data, chat_id)
                self._code = None
                self._editor_2 = None
                self._edit_mgs_ident_2 = None
                self.close()
                return
            if self._code in self._list_listrik_prod:
                valid = re.match(r'^(\d+)#(0\d+)$', data)
                if not valid:
                    self.sender.sendMessage('Silahkan masukan nomor handphone anda dengan benar.')
                    return
                self.sender.sendMessage('Mohon tunggu transaksi anda sedang diproses.')
                acc = valid.group(1)
                phone = valid.group(2)
                    
                self.topup_listrik(self._code, acc, phone, chat_id)
                self._code = None
                self._editor_2 = None
                self._edit_mgs_ident_2 = None
                self.close()
                return

        self.main_menu()
    

    # MAIN CALLBACK
    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        self.bot.answerCallbackQuery(
            query_id,
            text='Ok. Wait to process.'
        )

        # Main Menu Filtering
        if self._editor:
            if query_data == 'backbutton':
                self._keyboard.pop()
                self.return_back(self._keyboard[-1])
                self._level -= 1
                self._code = None
                return

            if query_data == 'saldo':
                self._cancel_last()
                self.cek_saldo(from_id)
                return

            if query_data in MAIN_Q:
                self.get_operator(query_data)
                self._level += 1
                self._code = None
                return

            if self._level == 2:
                if query_data == 'listrik':
                    self.listrik_produk()
                    self._level += 1
                    self._code = None
                    return

                if query_data in self._list_pulsa_op:
                    self.pulsa_produk(val=query_data)
                    self._level += 1
                    self._code = None
                    return

                if query_data in self._list_topup_op:
                    self.topup_produk(val=query_data)
                    self._level += 1
                    self._code = None
                    return

            if self._level == 3:
                if query_data in self._list_listrik_prod:
                    self._cancel_last()
                    self.listrik_detail_prod(val=query_data)
                    self._code = query_data
                    return

                if query_data in self._list_pulsa_prod:
                    self._cancel_last()
                    self.pulsa_detail_prod(val=query_data)
                    self._code = query_data
                    return

                if query_data in self._list_topup_prod:
                    self._cancel_last()
                    self.topup_detail_prod(val=query_data)
                    self._code = query_data
                    return

        else:
            self.main_menu()


    def _cancel_last(self):
        if self._editor_2:
            self._editor_2.deleteMessage()
            self._editor_2 = None
            self._edit_mgs_ident_2 = None


    # IDLE 10 S
    def on__idle(self, event):
        self.close()


    # CLOSED
    def on_close(self, ex):
        # Save to database
        global trx_record
        trx_record[self.id] = (self._level, self._edit_mgs_ident, self._edit_mgs_ident_2, self._code, self._keyboard)



TOKEN = '528057329:AAFBShP7yaoh2ZgOl0Fg4Fzipw1kYitx9Iw'  # get token from command-line

bot = telepot.DelegatorBot(TOKEN, [
    include_callback_query_chat_id(
        pave_event_space())(
            per_chat_id(types=['private']), create_open, Epaybot, timeout=10),
])

MessageLoop(bot).run_as_thread()

while 1:
    try :
        url = _URL + 'api/manager/unconfirm/'
        q = requests.get(url)
        qson = q.json()
        # print(qson)
        for i in qson:
            debit = i['debit']
            kredit = i['kredit']
            teleid = i['telegram']
            ids = i['id']
            saldo = i['balance']
            kat = i['status_type']
            tm = pendulum.parse(i['timestamp']).to_datetime_string()
            trx = i['trx']
            pop_message = "Terimakasih Anda sudah melakukan pengisisan deposit sebesar Rp {} Nomor Resi {} pada tanggal {}. Saldo anda saat ini menjadi Rp {}".format(debit, ids, tm, saldo)
            if kat == 2:
                pop_message = "Transaksi {} gagal diproses.\nDana sudah kami refund sebesar Rp {}, saldo Anda saat ini menjadi Rp {}. Mohon maaf atas ketidaknyamananya.".format(trx, -kredit, saldo)
            
            try :
                url = _URL + 'api/manager/unconfirm/{}/update/'.format(ids)
                r = requests.put(url, data=json.dumps({'confrmed':True}), headers={'Content-Type':'application/json'})
                bot.sendMessage(teleid, pop_message, parse_mode='HTML')
            except:
                pass

    except :
        pass

    time.sleep(5)

