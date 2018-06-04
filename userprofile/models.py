from django.db import models

from django.contrib.auth.models import User
from .utils import get_init_profcode


class GetActiveProfile(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=25, blank=True)
    telegram = models.CharField(max_length=25, blank=True)
    saldo = models.IntegerField(default=0)
    active = models.BooleanField(default=False)
    agen = models.BooleanField(default=False)
    email_confirmed = models.BooleanField(default=False)
    token_code = models.CharField(max_length=10, blank=True)
    limit = models.IntegerField(default=-110000)
    profile_member = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='usermember')

    objects = models.Manager()
    active_profile = GetActiveProfile()

    class Meta:
        ordering = ['user__first_name']

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        if self.token_code is None or self.token_code == '':
            self.token_code = get_init_profcode(self)
        super(Profile, self).save(*args, **kwargs)


class UncloseBook(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(closed=False)


class PembukuanTransaksi(models.Model):
    TYPE_LIST = (
        (1, 'Topup saldo'),
        (2, 'Reversed'),
        (9, 'Success'),
        (3, 'Failed')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_id = models.OneToOneField('self', on_delete=models.SET_NULL, null=True)
    seq = models.PositiveSmallIntegerField(default=1)
    debit = models.IntegerField(default=0)
    kredit = models.IntegerField(default=0)
    balance = models.IntegerField(default=0)
    status_type = models.PositiveSmallIntegerField(choices=TYPE_LIST, default=9)
    keterangan = models.CharField(max_length=200, blank=True)
    confrmed = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    unclosed_book = UncloseBook()


    class Meta:
        ordering = ['-timestamp']


    def __str__(self):
        return str(self.id)

    
    def get_transaksi_obj(self):
        try:
            if hasattr(self, 'transaksi'):
                return self.transaksi
            elif hasattr(self, 'bukutrans'):
                return self.bukutrans
            else :
                return self.bukupln
        except Exception as e:
            return None

    
    def harga_beli(self):
        try:
            if hasattr(self, 'transaksi'):
                return self.transaksi.responsetransaksi.price
            elif hasattr(self, 'bukutrans'):
                return self.bukutrans.responsetransaksi.price
            else :
                return self.bukupln.responsetransaksi.price
        except Exception as e:
            return 0

    
    def profit(self):
        return self.kredit - self.harga_beli()


class CatatanModal(models.Model):
    TYPE_LIST = (
        (1, 'Pembelian'),
        (2, 'Beli Gagal'),
        (3, 'Refund'),
        (4, 'Tambah Saldo')
    )
    LIST_BILLER = (
        ('SB', 'Siap Bayar'),
        ('RB', 'Raja Biller'),
    )

    debit = models.PositiveIntegerField(default=0)
    kredit = models.PositiveIntegerField(default=0)
    saldo = models.PositiveIntegerField(default=0)
    type_transaksi = models.PositiveSmallIntegerField(choices=TYPE_LIST, default=1)
    parent_id = models.OneToOneField('self', on_delete=models.SET_NULL, null=True, blank=True)
    confirmed = models.BooleanField(default=False)
    keterangan = models.CharField(max_length=200, blank=True)
    biller = models.CharField(max_length=2, choices=LIST_BILLER, default='RB')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'timestamp'

    def __str__(self):
        return str(self.id)

