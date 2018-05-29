from django.db.models.signals import post_save
from django.dispatch import receiver

from django.conf import settings

import requests, json
from lxml import html


from .models import Transaksi, ResponseTransaksi, CatatanModal
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
            price = rson.get('price', 0),
            balance = rson.get('balance', 0),
            url_struk = rson.get('urlstruk', ''),
            refca = rson.get('refca', ''),
            refsb = rson.get('refsb', '')
        )

        if instance.request_type == 'p':
            if res.rc in ['', '00']:
                pebukuan_obj = PembukuanTransaksi.objects.create(
                    user = instance.user,
                    kredit = instance.price,
                    balance = instance.user.profile.saldo - instance.price
                )

                try :
                    r = requests.get(res.url_struk)
                    tree = html.fromstring(r.text.replace(u'\xa0', ''))
                    instance.struk = tree.xpath('//pre/text()')[0]
                except Exception as es :
                    pass

                instance.pembukuan = pebukuan_obj
                instance.save(update_fields=['pembukuan', 'struk'])
            else :
                instance.status = 9
                instance.save()

    if update_fields is not None :
        # update in admin to gagal transaksi    
        if instance.request_type == 'p':
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


@receiver(post_save, sender=ResponseTransaksi)
def proses_catatan_modal(sender, instance, created, update_fields, **kwargs):
    last_catatan = CatatanModal.objects.latest()
    if created :
        if instance.trx.request_type == 'p' and instance.rc in ['00','']:
            try :
                modal_create_obj = CatatanModal.objects.create(
                    kredit = instance.price,
                    saldo = last_catatan.saldo - instance.price,
                )
            except:
                modal_create_obj = CatatanModal.objects.create(
                    kredit = instance.price,
                    saldo = 0,
                )

            
            if instance.serialno != '' and instance.rc == '00':
                modal_create_obj.confirmed = True
                modal_create_obj.save(update_fields=['confirmed'])


            trx_obj = Transaksi.objects.filter(
                trx_code = instance.trx.trx_code
            ).update(catatan_modal=modal_create_obj)



    if update_fields is not None:
        if 'response_code' in update_fields:
            instance_modal = instance.trx.catatan_modal
            if instance.has_changed('rc') and instance.trx.catatan_modal.confirmed == False:
                if instance.rc in ['99','10','11','12','13','20','21','30','31','32','33','34','35','36','37','50','90']:
                    modal_create_obj_new = CatatanModal.objects.create(
                        debit = instance.trx.catatan_modal.kredit,
                        saldo = last_catatan.saldo + instance.trx.catatan_modal.kredit,
                        parent_id = instance.trx.catatan_modal,
                        type_transaksi = 3,
                        confirmed = True
                    )
                    instance_modal.type_transaksi = 2
                    instance_modal.confirmed = True
                    instance_modal.save()

                elif instance.serialno != '' and instance.rc == '00' and instance.trx.catatan_modal.kredit != instance.price:
                    modal_create_obj_new = CatatanModal.objects.create(
                        debit = instance.trx.catatan_modal.kredit,
                        kredit = instance.price,
                        saldo = last_catatan.saldo + instance.trx.catatan_modal.kredit - instance.price,
                        parent_id = instance.trx.catatan_modal,
                        confirmed = True,
                        keterangan = 'Harga beli berubah!', 
                    )
                    instance_modal.type_transaksi = 2
                    instance_modal.confirmed = True
                    instance_modal.save()

                Transaksi.objects.filter(
                    responsetransaksi = instance
                ).update(catatan_modal=modal_create_obj_new)
                    