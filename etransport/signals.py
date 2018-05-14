from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings

import requests, json
import telepot

from .models import Product, Transaksi, ResponseTransaksi
from userprofile.models import PembukuanTransaksi


@receiver(pre_save, sender=Product)
def generate_prod_code(sender, instance, **kwars):
    if instance.kode_internal is None or instance.kode_internal == '':
        instance.kode_internal = '{}{}'.format(instance.operator.kode, int(instance.nominal/1000))


# precess recording transaksi
@receiver(post_save, sender=Transaksi)
def transaction_recording(sender, instance, created, update_fields=[], **kwargs):
    if created :
        # proses pembukuan
        pembukuan_obj = PembukuanTransaksi(
            user = instance.user,
            kredit = instance.price,
            balance = instance.user.profile.saldo - instance.price,
        )
        pembukuan_obj.save()
        instance.pembukuan = pembukuan_obj
        instance.save(update_fields=['pembukuan'])

        # proses transaksi ke server biling
        pord_code = instance.product.kode_external
        phone = instance.phone
        trx_code = instance.trx_code

        data = {
            "opcode": "pulsa",
            "uid": settings.SIAPBAYAR_ID,
            "pin": settings.SIAPBAYAR_PASS,
            "productcode": pord_code,
            "nohp": phone,
            "refca": trx_code
        }

        url = settings.SIAP_URL
        rjson = dict()
        try :
            r = requests.post(url, data=json.dumps(data), headers={'Content-Type':'application/json'})
            if r.status_code == requests.codes.ok :
                rjson = r.json()
            r.raise_for_status()
        except :
            rjson['rc'] = '99'
            rjson['info'] = 'Gagal terhubung ke server atau timeout.'
        

        response_trx = ResponseTransaksi.objects.create(
            trx=instance,
            nohp=rjson.get('nohp',''),
            info=rjson.get('info',''),
            product_code=rjson.get('productcode',''),
            trxtime=rjson.get('trxtime',''),
            serial_no=rjson.get('serialno',''),
            price=rjson.get('price', 0),
            balance=rjson.get('balance', 0),
            refca=rjson.get('refca',''),
            refsb=rjson.get('refsb',''),
            response_code=rjson.get('rc',''),
        )


        # update instanly status transaksi if failed
        if response_trx.response_code in ['99','10','11','12','13','20','21','30','31','32','33','34','35','36','37','50','90']:
            instance.status = 9
            instance.save(update_fields=['status'])
            
            # tele = telepot.Bot('513055446:AAEd1gnV_Zts_fGpO3L6uyNiRLCmfx-fK9Y')
            # user = instance.user
            # user.refresh_from_db()
            # # try :
            # tele.sendMessage(user.profile.telegram, 'Transaksi {}, nilai transaksi telah direfund. Saldo anda saat ini Rp {}'.format(instance.trx_code, user.profile.saldo))
            # # except:
            # #     pass


    # jika updatetable
    else :
        # update in admin to gagal transaksi    
        user = instance.user
        user.refresh_from_db()
        if update_fields is None:
            diskon_pembukuan = PembukuanTransaksi.objects.create(
                user = user,
                parent_id = instance.pembukuan,
                seq = instance.pembukuan.seq +1,
                debit = instance.pembukuan.kredit,
                balance = user.profile.saldo + instance.pembukuan.kredit,
                keterangan = 'Transaksi gagal'
            )
        else :
            # update in form
            if 'status' in update_fields:
                diskon_pembukuan = PembukuanTransaksi.objects.create(
                    user = user,
                    parent_id = instance.pembukuan,
                    seq = instance.pembukuan.seq +1,
                    debit = instance.pembukuan.kredit,
                    balance = user.profile.saldo + instance.pembukuan.kredit,
                    keterangan = 'Transaksi gagal'
                )