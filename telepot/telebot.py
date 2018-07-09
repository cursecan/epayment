import sys
import time
import telepot
import pendulum, schedule
import telepot.helper
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, create_open, pave_event_space, include_callback_query_chat_id
)

import requests, re, json

trx_record = telepot.helper.SafeDict()
_URL = 'http://127.0.0.1:8000/'
TOKEN = '528057329:AAFBShP7yaoh2ZgOl0Fg4Fzipw1kYitx9Iw'  # get token from command-line

def group_li(li, n):
    return [li[i:i+n] for i in range(0, len(li), n)]


MAIN_Q = ('PULSA', 'TOPUP', 'LISTRIK', 'GAME')


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
        self._list_game_op = self.all_game_operator()
        self._list_pulsa_prod = self.all_pulsa_prod()
        self._list_topup_prod = self.all_topup_prod()
        self._list_listrik_prod = self.all_listrik_prod()
        self._list_game_prod = self.all_game_prod()


    # MENU UTAMA 
    def main_menu(self):
        try :
            self.bot.editMessageReplyMarkup(self._edit_mgs_ident)
        except:
            pass
            
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='PULSA & DATA', callback_data='PULSA'),
                ],
                [
                    InlineKeyboardButton(text='GAME ONLINE', callback_data='GAME'),
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
                'Pelanggan Yth, {}\nSaldo simpanan anda saat ini Rp {:0,.0f}'.format(name, float(saldo)).replace('Rp -','-Rp ')
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


    # LIST KODE PRODUK LISTRIK
    def all_listrik_prod(self):
        url = _URL+'api/pln/produk/'
        r = requests.get(url)
        return [i['kode_produk'] for i in r.json()]


    # LIST KODE PRODUK PULSA
    def all_pulsa_prod(self):
        url = _URL+'api/pulsa/produks/'
        r = requests.get(url)
        return [i['kode_internal'] for i in r.json()]


    # LIST KODE PRODUK TOPUP
    def all_topup_prod(self):
        url = _URL+'api/etrans/produk/'
        r = requests.get(url)
        return [i['kode_internal'] for i in r.json()]

    
    # LIST KODE PRODUK GAME
    def all_game_prod(self):
        url = _URL+'api/game/produk-game/'
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

    # LIST GAME OPERATOR
    def all_game_operator(self):
        url = _URL+'api/game/game/'
        r = requests.get(url)
        list_1 = [i['code'] for i in r.json()]
        return list_1
    

    # DATAS ALL USER
    def get_all_user(self):
        r = requests.get(_URL+'api/manager/user/')
        return r.json()


    # OPERATOR
    def get_operator(self, qs):
        if qs == 'PULSA':
            url = _URL+'api/pulsa/operator/'
        elif qs == 'GAME' :
            url = _URL+'api/game/game/'
        else :
            url = _URL+'api/etrans/operator/'

        r = requests.get(url)

        board = []

        # OPERATOR KHUSUS GAME
        if qs == 'GAME':
            for i in r.json():
                board.append(
                    InlineKeyboardButton(text=i.get('nama_game'), callback_data=i.get('code'))
                )

        # DEFAULT OPERATOR
        else :
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


    # PRODUK LISTRIK
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


    # ALL PRODUK GAME
    def game_produk(self, val):
        url = _URL+'api/game/produk-game/?op='+val
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


    # BROADCAST IMAGE
    def broadcast_img(self, image, caption=None):
        users = self.get_all_user()
        for u in users:
            if u['telegram'] != '':
                try :
                    bot.sendPhoto(
                        u['telegram'], image, caption
                    )
                except :
                    pass


    # DETAIL PRODUK PULSA
    def pulsa_detail_prod(self, val):
        url = _URL+'api/pulsa/produks/?kd='+val
        r = requests.get(url)
        rson = r.json()
        info_prod = '<b>{} harga Rp {}.</b>\nKetikkan No.Handphone tujuan! (diawali angka 0).\n<i>Contoh : 081234567890</i>\nnb: klik tombol <b> "BACK" </b> di atas untuk batal transaksi.'.format(rson[0]['keterangan'], rson[0]['price'])
        sent = self.sender.sendMessage(info_prod, parse_mode='HTML')
        self._editor_2 = telepot.helper.Editor(self.bot, sent)
        self._edit_mgs_ident_2 = telepot.message_identifier(sent)
        

    # DETAIL PRODUK TOPUP
    def topup_detail_prod(self, val):
        url = _URL+'api/etrans/produk-detail/?kd='+val
        r = requests.get(url)
        rson = r.json()
        info_prod = '<b>{} harga Rp {}.</b>\nKetikkan No.Handphone tujuan! (diawali angka 0).\n<i>Contoh : 081234567890</i>\nnb: klik tombol <b> "BACK" </b> di atas untuk batal transaksi.'.format(rson[0]['keterangan'], rson[0]['price'])
        sent = self.sender.sendMessage(info_prod, parse_mode='HTML')
        self._editor_2 = telepot.helper.Editor(self.bot, sent)
        self._edit_mgs_ident_2 = telepot.message_identifier(sent)

    # LIHAT pln produk
    def listrik_detail_prod(self, val):
        url = _URL+'api/pln/produk/?p='+val
        r = requests.get(url)
        rson = r.json()
        info_prod = '<b>{} harga Rp {}.</b>\nKetikkan <b>No.Meter/ID Pelanggan</b> tujuan!\n<i>Contoh: 12345698765</i>\nnb: klik tombol <b> "BACK" </b> di atas untuk batal transaksi.'.format(rson[0]['nama_produk'], rson[0]['price'])
        sent = self.sender.sendMessage(info_prod, parse_mode='HTML')
        self._editor_2 = telepot.helper.Editor(self.bot, sent)
        self._edit_mgs_ident_2 = telepot.message_identifier(sent)


    # DETAIL PRODUK GAME
    def game_detail_prod(self, val):
        url = _URL+'api/game/produk-game/?code='+val
        r = requests.get(url)
        rson = r.json()
        info_prod = '<b>{} harga Rp {}.</b>\n{}\nnb: klik tombol <b> "BACK" </b> di atas untuk batal transaksi.'.format(rson[0]['keterangan'], rson[0]['price'], rson[0]['panduan'])
        sent = self.sender.sendMessage(info_prod, parse_mode='HTML')
        self._editor_2 = telepot.helper.Editor(self.bot, sent)
        self._edit_mgs_ident_2 = telepot.message_identifier(sent)

    # PROCESS POST TOPUP PULSA
    def topup_pulsa(self, code, val, chat_id):
        payload = {
            'telegram': chat_id,
            'produk': code,
            'phone': val
        }
        try :
            # PILIH BILLER
            r = requests.get(_URL+'api/pulsa/produks/?kd='+code, headers={'Content-Type':'application/json'})
            rson = r.json()
            # SIAPBAYAR
            if rson[0]['bill'] == 'SB':
                r = requests.post(_URL+'api/pulsa/topup/', data=json.dumps(payload), headers={'Content-Type':'application/json'})
            # RAJABILLER
            elif rson[0]['bill']=='RB' :
                r = requests.post(_URL+'api/pulsa/topup_rb/', data=json.dumps(payload), headers={'Content-Type':'application/json'})
            
            rson = r.json()
        except :
            rson = {}
            
        self.fedback_message(rson)


    # PROCESS POST TOPUP ETRANS
    def topup_etrans(self, code, val, chat_id):
        payload = {
            'telegram': chat_id,
            'produk': code,
            'phone': val
        }

        # url = _URL+'api/etrans/topup/'
        url = _URL+'api/etrans/topup_trans_rb/'

        r = requests.post(url=url, data=json.dumps(payload), headers={'Content-Type':'application/json'})
        rson = r.json()
        self.fedback_message(rson)

    
    # PROCESS POST TOPUP GAME
    def topup_game(self, code, val, chat_id):
        payload = {
            'telegram': chat_id,
            'produk': code,
            'phone': val
        }

        url = _URL+'api/game/topup-game/'

        r = requests.post(url=url, data=json.dumps(payload), headers={'Content-Type':'application/json'})
        rson = r.json()
        self.fedback_message(rson)


    # PROCESS POST TOPUP LISTRIK
    def topup_listrik(self, code, acc, chat_id, phone=None):
        payload = {
            'telegram': chat_id,
            'produk': code,
            'account': acc,
            'phone': '081315667766',
        }

        # url = _URL+'api/pln/topup/'
        url = _URL+'api/pln/topup_pln_rb/'

        r = requests.post(url=url, data=json.dumps(payload), headers={'Content-Type':'application/json'})
        rson = r.json()
        self.fedback_message(rson)

    # MESSAGE FEEDBACK
    def fedback_message(self, rson):
        if rson['code'] == 0:
            try:
                self.sender.sendMessage(
                    'TRANSAKSI {}\n<i>Pembelian {} dengan harga Rp {:0,.0f} pada nomor {} dalam process. Saldo anda saat ini adalah Rp {:0,.0f}.</i>'.format(
                        rson.get('trx'), rson.get('produk'), float(rson.get('price',0)),
                        rson.get('account_num') if rson.get('account_num',None)!=None else rson.get('phone'), float(rson.get('saldo',0))
                    ).replace('Rp -','-Rp '), parse_mode='HTML'
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

        self.bot.editMessageReplyMarkup(self._edit_mgs_ident)
        self.main_menu()


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
                'Maaf kode yang anda masukan salah, silahkan masukan kode aktivasi dengan benar atau daftarkan akun Anda di <a href="http://warungid.com/register/">warungid.com</a>',
                parse_mode='HTML'
            )
        else :
            self.sender.sendMessage(
                'Selamat, aktivasi akun anda telah berhasil. Ketik /menu untuk kembali ke menu utama, transaksi sudah dapat dilakukan.Kunjungi juga website kami di <a href="http://warungid.com">warungid.com</a>',
                parse_mode='HTML'
            )


    # MAIN ON CHAT
    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if content_type == 'text':
            try :
                dt_match = re.match(r'^/broadcast_img (https?://[\w\d/\._\-]+\.(jpe?g|png)) ([\s\S]+)$', msg['text'])
                img = dt_match.group(1)
                caption = dt_match.group(3)
                self.broadcast_img(img, caption)
                return
            except :
                pass

            try :
                dt_match = re.match(r'^/broadcast ([\s\S]+)$', msg['text'])
                data = dt_match.group(1) 
                self.broadcast_msg(data)
                return
            except:
                pass

            try :
                data = re.match(r'^/aktif (\d+)$', msg['text'])
                code = data.group(1)
                self.integrate_telegram(chat_id, code)
                return
            except:
                pass

            if msg['text'] in ['/start', '/menu']:
                self.main_menu()
                return

            if self._code != None:
                data = msg['text']
                if self._code in self._list_pulsa_prod:
                    valid = re.match(r'^0?\d+$', data)
                    if not valid:
                        self.sender.sendMessage('Silahkan masukan nomor handphone anda dengan benar atau ketik /menu untuk kembali ke menu utama.')
                        return
                    self.sender.sendMessage('Mohon tunggu transaksi anda sedang diproses.')
                    self.topup_pulsa(self._code, data, chat_id)
                    self._code = None
                    self._editor_2 = None
                    self._edit_mgs_ident_2 = None
                    self.close()
                    return
                if self._code in self._list_topup_prod:
                    valid = re.match(r'^0?\d+$', data)
                    if not valid:
                        self.sender.sendMessage('Silahkan masukan nomor handphone anda dengan benar atau ketik /menu untuk kembali ke menu utama.')
                        return
                    self.sender.sendMessage('Mohon tunggu transaksi anda sedang diproses.')
                    self.topup_etrans(self._code, data, chat_id)
                    self._code = None
                    self._editor_2 = None
                    self._edit_mgs_ident_2 = None
                    self.close()
                    return
                if self._code in self._list_listrik_prod:
                    valid = re.match(r'^(\d{11,12})$', data)
                    if not valid:
                        self.sender.sendMessage('Silahkan masukan Nomor Meter / ID Pelanggan anda dengan benar atau ketik /menu untuk kembali ke menu utama.')
                        return
                    self.sender.sendMessage('Mohon tunggu transaksi anda sedang diproses.')
                    acc = valid.group(1)
                        
                    self.topup_listrik(self._code, acc, chat_id)
                    self._code = None
                    self._editor_2 = None
                    self._edit_mgs_ident_2 = None
                    self.close()
                    return
                if self._code in self._list_game_prod:
                    self.sender.sendMessage('Mohon tunggu transaksi anda sedang diproses.')
                    self.topup_game(self._code, data, chat_id)
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
                self._cancel_last()
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

                if query_data in self._list_game_op:
                    self.game_produk(val=query_data)
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

                if query_data in self._list_game_prod:
                    self._cancel_last()
                    self.game_detail_prod(val=query_data)
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


# NOTIF TOPUP SALSO
def topup_notification():
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
            pop_message = "Yth Pelanggan Warungid,\nTerimakasih Anda sudah melakukan pengisisan deposit sebesar Rp {:0,.0f} Nomor Resi {} pada tanggal {}. Saldo anda saat ini menjadi Rp {:0,.0f}".format(float(debit), ids, tm, float(saldo)).replace('Rp -', '-Rp ')
            if kat == 2:
                pop_message = "Yth Pelanggan Warungid,\nTransaksi {} gagal diproses.\nDana sudah kami refund sebesar Rp {:0,.0f}, saldo Anda saat ini menjadi Rp {:0,.0f}. Mohon maaf atas ketidaknyamananya.".format(trx, float(abs(kredit)), float(saldo))
            
            try :
                url = _URL + 'api/manager/unconfirm/{}/update/'.format(ids)
                r = requests.put(url, data=json.dumps({'confrmed':True}), headers={'Content-Type':'application/json'})
                bot.sendMessage(teleid, pop_message, parse_mode='HTML')
            except:
                pass

    except :
        pass


# NOTIF PIUTANG USER
def piutang_notification():
    try:
        url = _URL + 'api/manager/piutang-user/'
        q = requests.get(url)
        qson = q.json()

        for i in qson:
            name = i.get('firstname', 'Unmane')
            teleid = i.get('telegram', None)
            nominal = abs(i.get('saldo', 0))
            message = 'Yth Pelanggan Warungid\na.n {}\n\nSampai dengan saat ini tagihan Anda tercatat sebesar Rp {:0,.0f} mohon untuk segera lunasi tagihan Anda. Terimakasih.\n\nWarungid\n<i>Serasa Warung Milik Kamu Sendiri</i>'.format(
                name.title(), float(nominal)
            )

            try :
                bot.sendMessage(teleid, message, parse_mode='HTML')
            except:
                pass
    except: 
        pass


bot = telepot.DelegatorBot(TOKEN, [
    include_callback_query_chat_id(
        pave_event_space())(
            per_chat_id(types=['private']), create_open, Epaybot, timeout=10),
])

MessageLoop(bot).run_as_thread()

# CALL TOPUP NOTIF
schedule.every(10).seconds.do(topup_notification)
# CALL PIUTANG NOTIF
schedule.every(2).day.at("10:00").do(piutang_notification)


while 1:
    schedule.run_pending()
    time.sleep(1)

