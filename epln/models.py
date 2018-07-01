from django.db import models
from django.contrib.auth.models import User

from userprofile.models import PembukuanTransaksi, CatatanModal
from .utils import generate_pln_trx, generate_code_pln_trx

class ActiveProdukmanager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)

class Product(models.Model):
    kode_produk = models.CharField(max_length=10, unique=True)
    nama_produk = models.CharField(max_length=100)
    nominal = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    parse_text = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    active_product = ActiveProdukmanager()


    class Meta:
        ordering = ['nominal']
    
    def __str__(self):
        return self.kode_produk


class Transaksi(models.Model):
    status_number = (
        (0, 'Success'),
        (1, 'Pending'),
        (9, 'Gagal'),
    )
    TYPE_REQUEST_LIST = (
        ('i', 'INQUIRY'),
        ('p', 'PAY')
    )
    trx_code  = models.CharField(max_length=16, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    nominal = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField(default=0)
    account_num = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20)
    status = models.PositiveSmallIntegerField(choices=status_number, default=0)
    request_type = models.CharField(max_length=1, choices=TYPE_REQUEST_LIST, default='i')
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='userpln')
    pembukuan = models.OneToOneField(PembukuanTransaksi, on_delete=models.SET_NULL , null=True, blank=True, related_name='bukupln')
    catatan_modal = models.OneToOneField(CatatanModal, on_delete=models.SET_NULL, null=True, blank=True, related_name='ctt_pln')
    struk = models.TextField(max_length=2000, blank=True)
    ref_sb_trx = models.OneToOneField('self', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = 'timestamp'
        ordering = ['-timestamp']

    def __str__(self):
        return self.trx_code

    def get_response(self):
        r = ResponseTransaksi.objects.get(trx=self)
        return r.rc

    def save(self, *args, **kwargs):
        if self.trx_code is None or self.trx_code == '':
            self.trx_code = generate_pln_trx(self)
        super(Transaksi, self).save(*args, **kwargs)


class ResponseTransaksi(models.Model):
    trx = models.OneToOneField(Transaksi, on_delete=models.CASCADE)
    rc = models.CharField(max_length=30, blank=True)
    info = models.CharField(max_length=200, blank=True)
    productcode = models.CharField(max_length=30, blank=True)
    trxtime = models.CharField(max_length=50, blank=True)
    accno = models.CharField(max_length=50, blank=True)
    nohp = models.CharField(max_length=50, blank=True)
    accname = models.CharField(max_length=200, blank=True)
    billperiode = models.CharField(max_length=50, blank=True)
    serialno = models.CharField(max_length=200, blank=True)
    nominal = models.IntegerField(default=0)
    adminfee = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    balance = models.IntegerField(default=0)
    url_struk = models.CharField(max_length=200, blank=True)
    refca = models.CharField(max_length=100, blank=True)
    refsb = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return str(self.trx)



class TransaksiRb(models.Model):
    status_number = (
        (0, 'Success'),
        (1, 'Pending'),
        (9, 'Gagal'),
    )
    TYPE_REQUEST_LIST = (
        ('i', 'INQUIRY'),
        ('p', 'PAY')
    )
    trx_code  = models.CharField(max_length=16, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    nominal = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField(default=0)
    idpel = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    status = models.PositiveSmallIntegerField(choices=status_number, default=0)
    request_type = models.CharField(max_length=1, choices=TYPE_REQUEST_LIST, default='i')
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='epln_rbuser')
    pembukuan = models.OneToOneField(PembukuanTransaksi, on_delete=models.SET_NULL , null=True, blank=True, related_name='epln_rbbuku_transaksi')
    catatan_modal = models.OneToOneField(CatatanModal, on_delete=models.SET_NULL, null=True, blank=True, related_name='epln_rbcctt_modal')
    struk = models.TextField(max_length=2000, blank=True)
    ref1 = models.CharField(max_length=16, blank=True)
    ref2 = models.CharField(max_length=16, blank=True)
    ref3 = models.CharField(max_length=16, blank=True)
    ref_inquery = models.OneToOneField('self', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = 'timestamp'
        ordering = ['-timestamp']

    def __str__(self):
        return self.trx_code

    def get_response(self):
        r = ResponseTransaksiRb.objects.get(trx=self)
        return r.status


    def save(self, *args, **kwargs):
        if self.trx_code is None or self.trx_code == '':
            self.trx_code = generate_code_pln_trx(self)
        super(TransaksiRb, self).save(*args, **kwargs)


class ResponseTransaksiRb(models.Model):
    trx = models.OneToOneField(TransaksiRb, on_delete=models.CASCADE)
    kode_produk = models.CharField(max_length=20, blank=True)
    waktu = models.CharField(max_length=40, blank=True)
    idpel1 = models.CharField(max_length=20, blank=True)
    idpel2 = models.CharField(max_length=20, blank=True)
    idpel3 = models.CharField(max_length=20, blank=True)
    nama_pelanggan = models.CharField(max_length=200, blank=True)
    periode = models.CharField(max_length=40, blank=True)
    nominal = models.PositiveIntegerField(default=0)
    admin = models.PositiveIntegerField(default=0)
    ref1 = models.CharField(max_length=100, blank=True)
    ref2 = models.CharField(max_length=100, blank=True)
    ref3 = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, blank=True)
    ket  = models.CharField(max_length=100, blank=True)
    saldo_terpotong = models.PositiveIntegerField(default=0)
    sisa_saldo = models.PositiveIntegerField(default=0)
    url_struk = models.CharField(max_length=200, blank=True)
    detail = models.TextField(max_length=2000, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.trx)




# {
#     "KODE_PRODUK"     : "KODE_PRODUK_VALUE",
#     "WAKTU"           : "WAKTU_VALUE",
#     "IDPEL1"          : "IDPEL1_VALUE",
#     "IDPEL2"          : "IDPEL2_VALUE",
#     "IDPEL3"          : "IDPEL3_VALUE",
#     "NAMA_PELANGGAN"  : "NAMA_PELANGGAN_VALUE",
#     "PERIODE"         : "PERIODE_VALUE",
#     "NOMINAL"         : "NOMINAL_VALUE",
#     "ADMIN"           : "ADMIN_VALUE",
#     "REF1"            : "REF1_VALUE",
#     "REF2"            : "REF2_VALUE",
#     "REF3"            : "REF3_VALUE",
#     "STATUS"          : "STATUS_VALUE",
#     "KET"             : "KET_VALUE",
#     "SALDO_TERPOTONG" : "SALDO_TERPOTONG_VALUE",
#     "SISA_SALDO"      : "SISA_SALDO_VALUE",
#     "URL_STRUK"       : "URL_STRUK_VALUE"
# }


#     "KODE_PRODUK"     : "KODE_PRODUK_VALUE",
#     "WAKTU"           : "WAKTU_VALUE",
#     "IDPEL1"          : "IDPEL1_VALUE",
#     "IDPEL2"          : "IDPEL2_VALUE",
#     "IDPEL3"          : "IDPEL3_VALUE",
#     "NAMA_PELANGGAN"  : "NAMA_PELANGGAN_VALUE",
#     "PERIODE"         : "PERIODE_VALUE",
#     "NOMINAL"         : "NOMINAL_VALUE",
#     "ADMIN"           : "ADMIN_VALUE",
#     "REF1"            : "REF1_VALUE",
#     "REF2"            : "REF2_VALUE",
#     "REF3"            : "REF3_VALUE",
#     "STATUS"          : "STATUS_VALUE",
#     "KET"             : "KET_VALUE",
#     "SALDO_TERPOTONG" : "SALDO_TERPOTONG_VALUE",
#     "SISA_SALDO"      : "SISA_SALDO_VALUE",
#     "URL_STRUK"       : "URL_STRUK_VALUE",
#     "DETAIL"          : {
#         "CATATAN"                     : "TIDAK DIIJINKAN MENAMBAH CHARGE",
#         "TOKEN"                       : "TOKEN_VALUE",
#         "SUBSCRIBERSEGMENTATION"      : "SUBSCRIBERSEGMENTATION_VALUE",
#         "POWERCONSUMINGCATEGORY"      : "POWERCONSUMINGCATEGORY_VALUE",
#         "POWERPURCHASE"               : "POWERPURCHASE_VALUE",
#         "MINORUNITOFPOWERPURCHASE"    : "MINORUNITOFPOWERPURCHASE_VALUE",
#         "PURCHASEDKWHUNIT"            : "PURCHASEDKWHUNIT_VALUE",
#         "MINORUNITOFPURCHASEDKWHUNIT" : "MINORUNITOFPURCHASEDKWHUNIT_VALUE"
#     }
# }