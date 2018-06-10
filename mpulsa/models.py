from django.db import models
from django.contrib.auth.models import User

from userprofile.models import PembukuanTransaksi, CatatanModal

from .utils import generate_pulsa_trx, generate_code_trx


class Operator(models.Model):
    kode = models.CharField(max_length=20, unique=True)
    operator = models.CharField(max_length=50)

    def __str__(self):
        return '{} ({})'.format(self.operator, self.kode)


class PrefixNumber(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    prefix = models.CharField(max_length=4, unique=True)

    def __str__(self):
        return self.prefix


class Biller(models.Model):
    LIST_BILLER = (
        ('SB', 'Siap Bayar'),
        ('RB', 'Raja Biller'),
    )
    nama = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    price = models.PositiveIntegerField(default=0)
    biller = models.CharField(max_length=2, choices=LIST_BILLER)

    def __str__(self):
        return self.biller+' / '+self.code


class ActiveProdukmanager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)


class Product(models.Model):
    LAYANAN_LIST = (
        ('D', 'DATA'),
        ('P', 'PULSA')
    )
    kode_internal = models.CharField(max_length=50, blank=True)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    type_layanan = models.CharField(max_length=2, choices=LAYANAN_LIST, default='P')
    nominal = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    kode_external = models.CharField(max_length=15)
    price_beli = models.PositiveIntegerField(default=0)
    keterangan = models.CharField(max_length=200, blank=True)
    parse_text = models.CharField(max_length=200, blank=True)
    active = models.BooleanField(default=False)
    biller = models.OneToOneField(Biller, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    active_product = ActiveProdukmanager()

    class Meta:
        ordering = ['operator','-type_layanan', 'nominal']

    
    def __str__(self):
        return self.kode_internal

    def benefit(self):
        try :
            return self.price - self.biller.price
        except :
            return 0


class Transaksi(models.Model):
    status_number = (
        (0, 'Success'),
        (1, 'Pending'),
        (9, 'Gagal'),
    )
    trx_code  = models.CharField(max_length=16, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(default=0)
    phone = models.CharField(max_length=20)
    status = models.PositiveSmallIntegerField(choices=status_number, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    pembukuan = models.OneToOneField(PembukuanTransaksi, on_delete=models.SET_NULL, null=True)
    catatan_modal = models.OneToOneField(CatatanModal, on_delete=models.SET_NULL, null=True, blank=True, related_name='ctt_pulsa')
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = 'timestamp'
        ordering = ['-timestamp']

    def __str__(self):
        return self.trx_code

    def get_response(self):
        r = ResponseTransaksi.objects.get(trx=self)
        return r.response_code

    def save(self, *args, **kwargs):
        if self.trx_code is None or self.trx_code == '':
            self.trx_code = generate_pulsa_trx(self)
        super(Transaksi, self).save(*args, **kwargs)


class ResponseTransaksi(models.Model):
    response_code = models.CharField(max_length=200, blank=True)
    info = models.CharField(max_length=200, blank=True)
    product_code = models.CharField(max_length=20, blank=True)
    trxtime = models.CharField(max_length=50, blank=True)
    nohp = models.CharField(max_length=30, blank=True)
    serial_no = models.CharField(max_length=100, blank=True)
    price = models.PositiveIntegerField(default=0)
    balance = models.PositiveIntegerField(default=0)
    refca = models.CharField(max_length=50, blank=True)
    refsb = models.CharField(max_length=100, blank=True)
    trx = models.OneToOneField(Transaksi, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.trx)


# TRANSAKSI RAJABILLER
class TransaksiRb(models.Model):
    status_number = (
        (0, 'Success'),
        (1, 'Pending'),
        (9, 'Gagal'),
    )
    trx_code  = models.CharField(max_length=16, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(default=0)
    phone = models.CharField(max_length=20)
    status = models.PositiveSmallIntegerField(choices=status_number, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    pembukuan = models.OneToOneField(PembukuanTransaksi, on_delete=models.SET_NULL, null=True, blank=True, related_name='mpulsa_rbbuku_transaksi')
    catatan_modal = models.OneToOneField(CatatanModal, on_delete=models.SET_NULL, null=True, blank=True, related_name='mpulsa_rbcctt_modal')
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = 'timestamp'
        ordering = ['-timestamp']

    def __str__(self):
        return self.trx_code


    def save(self, *args, **kwargs):
        if self.trx_code is None or self.trx_code == '':
            self.trx_code = generate_code_trx(self)
        super(TransaksiRb, self).save(*args, **kwargs)



# RESPONSE TRANSAKSI RAJABILLER
class ResponseTransaksiRb(models.Model):
    trx = models.OneToOneField(TransaksiRb, on_delete=models.SET_NULL, null=True, blank=True)
    kode_produk = models.CharField(max_length=30, blank=True)
    waktu = models.CharField(max_length=40, blank=True)
    no_hp = models.CharField(max_length=20, blank=True)
    sn = models.CharField(max_length=100, blank=True)
    ref1 = models.CharField(max_length=100, blank=True)
    ref2 = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, blank=True)
    ket = models.CharField(max_length=200, blank=True)
    saldo_terpotong = models.IntegerField(default=0)
    sisa_saldo = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.trx)