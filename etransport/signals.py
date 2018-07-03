from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings

import requests, json
import telepot

from .models import Product, Transaksi, ResponseTransaksi, ResponseTransaksiRb, TransaksiRb
from userprofile.models import PembukuanTransaksi, CatatanModal


@receiver(pre_save, sender=Product)
def generate_prod_code(sender, instance, **kwars):
    if instance.kode_internal is None or instance.kode_internal == '':
        instance.kode_internal = '{}{}'.format(instance.operator.kode, int(instance.nominal/1000))


# precess recording transaksi
@receiver(post_save, sender=Transaksi)
def transaction_recording(sender, instance, created, update_fields=[], **kwargs):
    if created :
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
        if not settings.DEBUG :
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

        if response_trx.response_code in ['00', '']:
            # proses pembukuan
            pembukuan_obj = PembukuanTransaksi(
                user = instance.user,
                kredit = instance.price,
                balance = instance.user.profile.saldo - instance.price,
            )
            pembukuan_obj.save()
            instance.pembukuan = pembukuan_obj
            instance.save(update_fields=['pembukuan'])

        # update instanly status transaksi if failed
        else :
            instance.status = 9
            instance.save()
            
    # update in admin to gagal transaksi    
    if update_fields is not None:
        # update in form
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
            response_trx_obj.save(update_fields=['response_code'])



# Signal perhitungan modal record terhd response transaksi
@receiver(post_save, sender=ResponseTransaksi)
def proses_catatan_modal(sender, instance, created, update_fields, **kwargs):
    last_catatan = CatatanModal.objects.latest()
    if created :
        if instance.response_code in ['00','']:
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

            
            if instance.serial_no != '' and instance.response_code == '00':
                modal_create_obj.confirmed = True
                modal_create_obj.save(update_fields=['confirmed'])


            trx_obj = Transaksi.objects.filter(
                trx_code = instance.trx.trx_code
            ).update(catatan_modal=modal_create_obj)


    if update_fields is not None:
        if 'response_code' in update_fields:
            instance_modal = instance.trx.catatan_modal
            # response trx gagal
            if instance.response_code in ['99','10','11','12','13','20','21','30','31','32','33','34','35','36','37','50','90']:
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

            # response berhasil
            elif instance.serial_no != '' and instance.response_code == '00' :
                if instance.trx.catatan_modal.kredit != instance.price :
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
                

# Process Transaksi Rajabiller
@receiver(post_save, sender=TransaksiRb)
def transaction_recording_rb(sender, instance, created, update_fields=[], **kwargs):
    if created :
        # proses transaksi ke server biling
        pord_code = instance.product.biller.code
        phone = instance.phone
        trx_code = instance.trx_code

        data = {
            "method": "rajabiller.game",
            "uid": settings.RAJABILLER_ID,
            "pin": settings.RAJABILLER_PASS,
            "kode_produk": pord_code,
            "no_hp": phone,
            "ref1": trx_code
        }

        url = settings.RAJA_URL
        rjson = dict()
        if not settings.DEBUG :
            try :
                r = requests.post(url, data=json.dumps(data), headers={'Content-Type':'application/json'}, verify=False)
                if r.status_code == requests.codes.ok :
                    rjson = r.json()
                r.raise_for_status()
            except :
                rjson['status'] = '99'
                rjson['ket'] = 'Gagal terhubung ke server atau timeout.'
        

        response_trx = ResponseTransaksiRb.objects.create(
            trx=instance,
            waktu=rjson.get('WAKTU',''),
            no_hp=rjson.get('NO_HP',''),
            sn=rjson.get('SN',''),
            ref1=rjson.get('REF1',''),
            ref2=rjson.get('REF2',''),
            status=rjson.get('STATUS', ''),
            ket=rjson.get('KET', ''),
            saldo_terpotong=int(rjson.get('SALDO_TERPOTONG',0)),
            sisa_saldo=int(rjson.get('SISA_SALDO',0)),
        )


        if response_trx.status in ['00', '']:
            # proses pembukuan
            pembukuan_obj = PembukuanTransaksi(
                user = instance.user,
                kredit = instance.price,
                balance = instance.user.profile.saldo - instance.price,
            )
            pembukuan_obj.save()
            instance.pembukuan = pembukuan_obj
            instance.save(update_fields=['pembukuan'])

        # update instanly status transaksi if failed
        else :
            instance.status = 9
            instance.save()
            
    # update in admin to gagal transaksi    
    if update_fields is not None:
        # update in form
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


# Proses Pencatatan Modal Response transaksi Rajabill
@receiver(post_save, sender=ResponseTransaksiRb)
def proses_catatan_modal_rajabill(sender, instance, created, update_fields, **kwargs):
    last_catatan = CatatanModal.objects.latest()
    if created :
        if instance.status in ['00','']:
            try :
                modal_create_obj = CatatanModal.objects.create(
                    kredit = instance.saldo_terpotong,
                    saldo = last_catatan.saldo - instance.saldo_terpotong,
                    biller = 'RB',
                )
            except:
                modal_create_obj = CatatanModal.objects.create(
                    kredit = instance.saldo_terpotong,
                    saldo = 0,
                    biller = 'RB',
                )

            
            if instance.sn != '' and instance.status == '00':
                modal_create_obj.confirmed = True
                modal_create_obj.save(update_fields=['confirmed'])


            trx_obj = TransaksiRb.objects.filter(
                trx_code = instance.trx.trx_code
            ).update(catatan_modal=modal_create_obj)


    if update_fields is not None:
        if 'status' in update_fields:
            instance_modal = instance.trx.catatan_modal
            # response trx gagal
            if instance.status not in ['', '00']:
                modal_create_obj_new = CatatanModal.objects.create(
                    debit = instance_modal.kredit,
                    saldo = last_catatan.saldo + instance_modal.kredit,
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

            # response berhasil
            elif instance.sn != '' and instance.status == '00' :
                if instance_modal.kredit != instance.saldo_terpotong :
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