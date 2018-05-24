from django.db.models.signals import post_save
from django.dispatch import receiver

from django.conf import settings

import requests, json


from .models import Transaksi, ResponseTransaksi
from userprofile.models import PembukuanTransaksi


@receiver(post_save, sender=Transaksi)
def precess_requesting_to_sb(sender, instance, created, update_fields, **kwargs):
    if created:
        if instance.request_type == 'i':
            payload = {
                "opcode": "inquiry",
                "uid": settings.SIAPBAYAR_ID,
                "pin": settings.SIAPBAYAR_PASS,
                "productcode": "PLNT",
                "accno": instance.account_num,
                "nohp": instance.phone,
                "refca": instance.trx_code,
            }
        else :
            payload = {
                "opcode": "payment",
                "uid": settings.SIAPBAYAR_ID,
                "pin": settings.SIAPBAYAR_PASS,
                "productcode": "PLNT",
                "accno": instance.account_num,
                "nohp": instance.phone,
                "nominal": instance.nominal,
                "refca": instance.trx_code,
                "refsbinq": instance.ref_sb_trx.responsetransaksi.refsb
            }

        r = requests.post(settings.SIAP_URL, data=json.dumps(payload), headers={'Content-Type':'application/json'})
        rson = r.json()
        res = ResponseTransaksi.objects.create(
            trx = instance,
            rc = rson.get('rc', ''),
            info = rson.get('info', ''),
            productcode = rson.get('productcode', ''),
            trxtime = rson.get('trxtime', ''),
            accno = rson.get('accno', ''),
            nohp = rson.get('nohp', ''),
            accname = rson.get('accname', ''),
            billperiode = rson.get('billperiode', ''),
            serialno = rson.get('serialno', ''),
            nominal = rson.get('nominal',0),
            adminfee = rson.get('adminfee', 0),
            price = rson.get(';price', 0),
            balance = rson.get('balance', 0),
            url_struk = rson.get('urlstruk', ''),
            refca = rson.get('refca', ''),
            refsb = rson.get('refsb', '')
        )

        if instance.request_type == 'p':
            pebukuan_obj = PembukuanTransaksi.objects.create(
                user = instance.user,
                kredit = instance.price,
                balance = instance.user.profile.saldo - instance.price
            )
            try :
                r = requests.get(res.url_struk)
                instance.struk = r.text
            except :
                pass
            instance.pembukuan = pebukuan_obj
            instance.save(update_fields=['pembukuan', 'struk'])
    else :
        # update in admin to gagal transaksi    
        user = instance.user
        user.refresh_from_db()
        if instance.request_type == 'p':
            if update_fields is None:
                diskon_pembukuan = PembukuanTransaksi.objects.create(
                    user = user,
                    parent_id = instance.pembukuan,
                    seq = instance.pembukuan.seq +1,
                    kredit = -instance.pembukuan.kredit,
                    balance = user.profile.saldo + instance.pembukuan.kredit,
                    status_type = 2,
                    confrmed = True,
                )
                PembukuanTransaksi.objects.filter(pk=instance.pembukuan.id).update(status_type=3)
            else :
                # update in form
                if 'status' in update_fields and instance.status == 9:
                    diskon_pembukuan = PembukuanTransaksi.objects.create(
                        user = user,
                        parent_id = instance.pembukuan,
                        seq = instance.pembukuan.seq +1,
                        kredit = -instance.pembukuan.kredit,
                        balance = user.profile.saldo + instance.pembukuan.kredit,
                        status_type = 2
                    )
                    PembukuanTransaksi.objects.filter(pk=instance.pembukuan.id).update(status_type=3)