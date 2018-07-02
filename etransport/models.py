from django.db import models
from django.contrib.auth.models import User


from userprofile.models import PembukuanTransaksi, CatatanModal
from .utils import generate_pulsa_trx, generate_code_etransrb_trx


class Operator(models.Model):
    kode = models.CharField(max_length=10, unique=True)
    operator = models.CharField(max_length=50)

    def __str__(self):
        return '{} ({})'.format(self.operator, self.kode)

class ActiveProdukmanager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)


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


class Product(models.Model):
    kode_internal = models.CharField(max_length=10, blank=True)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    biller = models.OneToOneField(Biller, on_delete=models.SET_NULL, blank=True, null=True)
    nominal = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    kode_external = models.CharField(max_length=15)
    price_beli = models.PositiveIntegerField(default=0)
    keterangan = models.CharField(max_length=200, blank=True)
    parse_text = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)
    
    objects = models.Manager()
    active_product = ActiveProdukmanager()

    class Meta:
        ordering = ['operator', 'nominal']
    
    def __str__(self):
        return self.kode_internal

    def benefit(self):
        return self.price - self.price_beli


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
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='usertrans')
    pembukuan = models.OneToOneField(PembukuanTransaksi, on_delete=models.SET_NULL, null=True, blank=True, related_name='bukutrans')
    catatan_modal = models.OneToOneField(CatatanModal, on_delete=models.SET_NULL, null=True, blank=True, related_name='ctt_trans')
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='etrans_rbuser')
    pembukuan = models.OneToOneField(PembukuanTransaksi, on_delete=models.SET_NULL, null=True, blank=True, related_name='etrans_rbbuku_transaksi')
    catatan_modal = models.OneToOneField(CatatanModal, on_delete=models.SET_NULL, null=True, blank=True, related_name='etrans_rbcctt_modal')
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
            self.trx_code = generate_code_etransrb_trx(self)
        super(TransaksiRb, self).save(*args, **kwargs)


class ResponseTransaksiRb(models.Model):
    trx = models.OneToOneField(TransaksiRb, on_delete=models.CASCADE)
    waktu = models.CharField(max_length=40, blank=True)
    no_hp = models.CharField(max_length=20, blank=True)
    sn = models.CharField(max_length=100, blank=True)
    ref1 = models.CharField(max_length=30, blank=True)
    ref2 = models.CharField(max_length=30, blank=True)
    status = models.CharField(max_length=20, blank=True)
    ket = models.CharField(max_length=100, blank=True)
    saldo_terpotong = models.PositiveIntegerField(default=0)
    sisa_saldo = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.trx)
