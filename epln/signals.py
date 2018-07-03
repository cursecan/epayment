from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

import requests, json, re
from lxml import html


from .models import Transaksi, ResponseTransaksi, TransaksiRb, ResponseTransaksiRb
from userprofile.models import PembukuanTransaksi, CatatanModal


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

        rson = dict()
        if not settings.DEBUG:
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
                if not settings.DEBUG:
                    try :
                        r = requests.get(res.url_struk)
                        tree = html.fromstring(r.text.replace(u'\xa0', ' '))
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
                    user = instance.user,
                    parent_id = instance.pembukuan,
                    seq = instance.pembukuan.seq +1,
                    kredit = -instance.pembukuan.kredit,
                    balance = instance.user.profile.saldo + instance.pembukuan.kredit,
                    status_type = 2
                )
                PembukuanTransaksi.objects.filter(pk=instance.pembukuan.id).update(status_type=3)

                response_trx_obj = ResponseTransaksi.objects.get(trx=instance)
                response_trx_obj.response_code = '99'
                response_trx_obj.save(update_fields=['rc'])


#Signal perubahan modal record thd response transaksi
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
            # filter jika gagal
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

                Transaksi.objects.filter(
                    responsetransaksi = instance
                ).update(catatan_modal=modal_create_obj_new)

            # Filter jika berhasil
            elif instance.serialno != '' and instance.rc == '00' :
                # berhasil dengan perubahan harga
                if instance.trx.catatan_modal.kredit != instance.price:
                    modal_create_obj_new = CatatanModal.objects.create(
                        debit = instance.trx.catatan_modal.kredit,
                        kredit = instance.price,
                        saldo = last_catatan.saldo + instance.trx.catatan_modal.kredit - instance.price,
                        parent_id = instance.trx.catatan_modal,
                        confirmed = True,
                        keterangan = 'Harga beli berubah!', 
                    )
                    instance_modal.type_transaksi = 2

                    Transaksi.objects.filter(
                        responsetransaksi = instance
                    ).update(catatan_modal=modal_create_obj_new)

                instance_modal.confirmed = True
                instance_modal.save()


# Process Transaksi RajaBiller
@receiver(post_save, sender=TransaksiRb)
def process_requesting_to_rb(sender, instance, created, update_fields, **kwargs):
    if created:
        if instance.request_type == 'i':
            payload = {
                "method": "rajabiller.inq",
                "uid": settings.RAJABILLER_ID,
                "pin": settings.RAJABILLER_PASS,
                "kode_produk": "PLNPRAH",
                "idpel1":"",
                "idpel2":"",
                "idpel3":"",
                "ref1": instance.trx_code,
            }
        else :
            payload = {
                "method": "rajabiller.paydetail",
                "uid": settings.RAJABILLER_ID,
                "pin": settings.RAJABILLER_PASS,
                "kode_produk": "PLNPRAH",
                "idpel1":"",
                "idpel2":"",
                "idpel3":"",
                "ref1": instance.trx_code,
                "ref2": instance.ref_inquery.responsetransaksirb.ref2,
                "ref3": "",
                "nominal": str(instance.product.nominal)
            }

        if len(instance.idpel) == 11:
            payload["idpel1"] = instance.idpel
        else:
            payload['idpel2'] = instance.idpel
        
        rson = dict()
        if not settings.DEBUG :
            url = settings.RAJA_URL
            try:
                r = requests.post(settings.RAJA_URL, data=json.dumps(payload), headers={'Content-Type':'application/json'}, verify=False)
                if r.status_code == requests.codes.ok :
                    rson = r.json()
                r.raise_for_status()
            except :
                rson['STATUS'] = '99'
                rson['KET'] = 'Gagal terhubung ke server atau timeout.'
       
        res = ResponseTransaksiRb.objects.create(
            trx = instance,
            kode_produk = rson.get('KODE_PRODUK',''),
            waktu = rson.get('WAKTU',''),
            idpel1 = rson.get('IDPEL1',''),
            idpel2 = rson.get('IDPEL2',''),
            idpel3 = rson.get('IDPEL3',''),
            nama_pelanggan = rson.get('NAMA_PELANGGAN',''),
            periode = rson.get('PERIODE',''),
            nominal = int(rson.get('NOMINAL',0)),
            admin = int(rson.get('ADMIN',0)),
            ref1 = rson.get('REF1',''),
            ref2 = rson.get('REF2',''),
            ref3 = rson.get('REF3',''),
            status = rson.get('STATUS',''),
            ket = rson.get('KET',''),
            saldo_terpotong = int(rson.get('SALDO_TERPOTONG',0)),
            sisa_saldo = int(rson.get('SISA_SALDO',0)),
            url_struk = rson.get('URL_STRUK',''),
            detail = str(rson.get('DETAIL','')),
        )

        if instance.request_type == 'p':
            if res.status in ['', '00']:
                pebukuan_obj = PembukuanTransaksi.objects.create(
                    user = instance.user,
                    kredit = instance.price,
                    balance = instance.user.profile.saldo - instance.price
                )
                if res.status == '00':
                    try :
                        token = re.findall(r'^(\d{5})(\d{5})(\d{5})(\d{5})$', rson['DETAIL']['TOKEN'])
                        kwh = rson['DETAIL']['PURCHASEDKWHUNIT']
                        struk = "STRUK PEMBELIAN\n\n"+"NO METER / IDPEL".ljust(20)+": "+instance.idpel+"\n"+"JML KWH".ljust(20)+": "+str(int(kwh)/100)+"\n"+"RP BAYAR".ljust(20)+": "+"Rp "+str(instance.price)+"\n"+"TOKEN".ljust(20)+": "+" ".join(token[0])+"\n\nTERIMA KASIH."
                    except:
                        struk = rson['DETAIL']['TOKEN']

                    instance.struk = 'TOKEN : ' + struk

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
                    user = instance.user,
                    parent_id = instance.pembukuan,
                    seq = instance.pembukuan.seq +1,
                    kredit = -instance.pembukuan.kredit,
                    balance = instance.user.profile.saldo + instance.pembukuan.kredit,
                    status_type = 2
                )
                PembukuanTransaksi.objects.filter(pk=instance.pembukuan.id).update(status_type=3)

                response_trx_obj = ResponseTransaksiRb.objects.get(trx=instance)
                response_trx_obj.status = '99'
                response_trx_obj.save(update_fields=['status'])



@receiver(post_save, sender=ResponseTransaksiRb)
def proses_catatan_modal_Rb(sender, instance, created, update_fields, **kwargs):
    last_catatan = CatatanModal.objects.latest()
    if created :
        if instance.trx.request_type == 'p' and instance.status in ['00','']:
            try :
                modal_create_obj = CatatanModal.objects.create(
                    kredit = instance.saldo_terpotong,
                    saldo = last_catatan.saldo - instance.saldo_terpotong,
                    biller = 'RB'
                )
            except:
                modal_create_obj = CatatanModal.objects.create(
                    kredit = instance.saldo_terpotong,
                    saldo = 0,
                    biller = 'RB'
                )

            # if instance.serialno != '' and instance.rc == '00':
            #     modal_create_obj.confirmed = True
            #     modal_create_obj.save(update_fields=['confirmed'])


            trx_obj = TransaksiRb.objects.filter(
                trx_code = instance.trx.trx_code
            ).update(catatan_modal=modal_create_obj)



    if update_fields is not None:
        if 'status' in update_fields:
            instance_modal = instance.trx.catatan_modal
            # filter jika gagal catatan modal
            if instance.status not in ['00','']:
                modal_create_obj_new = CatatanModal.objects.create(
                    debit = instance.saldo_terpotong,
                    saldo = last_catatan.saldo + instance.saldo_terpotong,
                    parent_id = instance_modal,
                    type_transaksi = 3,
                    confirmed = True,
                    biller = 'RB',
                )
                instance_modal.type_transaksi = 2
                instance_modal.confirmed = True
                instance_modal.save()

                TransaksiRb.objects.filter(
                    responsetransaksirb = instance
                ).update(catatan_modal=modal_create_obj_new)

            # Filter jika berhasil
            elif instance.status == '00' :
                # berhasil dengan perubahan harga
                if instance_modal.kredit != instance.saldo_terpotong:
                    modal_create_obj_new = CatatanModal.objects.create(
                        debit = instance_modal.kredit,
                        kredit = instance.saldo_terpotong,
                        saldo = last_catatan.saldo + instance_modal.kredit - instance.saldo_terpotong,
                        parent_id = instance_modal,
                        confirmed = True,
                        keterangan = 'Harga beli berubah!', 
                        biller = 'RB',
                    )
                    instance_modal.type_transaksi = 2

                    TransaksiRb.objects.filter(
                        responsetransaksirb = instance
                    ).update(catatan_modal=modal_create_obj_new)

                instance_modal.confirmed = True
                instance_modal.save()