from django.db import models
from django.contrib.auth.models import User


from userprofile.models import PembukuanTransaksi, CatatanModal
from .utils import generate_code_game_rb_trx

class Game(models.Model):
    code = models.CharField(max_length=30, unique=True)
    nama_game = models.CharField(max_length=200)
    help_text = models.TextField(max_length=2000, blank=True)
    active = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.nama_game


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
    kode_internal = models.CharField(max_length=10, blank=True)
    developer = models.ForeignKey(Game, on_delete=models.CASCADE)
    biller = models.OneToOneField(Biller, on_delete=models.CASCADE)
    nominal = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    keterangan = models.CharField(max_length=200, blank=True)
    parse_text = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)


    objects = models.Manager()
    active_product = ActiveProdukmanager()

    def __str__(self):
        return self.kode_internal


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
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='egame_rbuser')
    pembukuan = models.OneToOneField(PembukuanTransaksi, on_delete=models.SET_NULL, null=True, blank=True, related_name='egame_rbbuku_transaksi')
    catatan_modal = models.OneToOneField(CatatanModal, on_delete=models.SET_NULL, null=True, blank=True, related_name='eegame_rbcctt_modal')
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
            self.trx_code = generate_code_game_rb_trx(self)
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
