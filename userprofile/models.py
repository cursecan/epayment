from django.db import models
from django.db.models import Sum, Value as V, Q, F
from django.db.models.functions import Coalesce

from datetime import datetime

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
    saldo_agen = models.IntegerField(default=0)
    active = models.BooleanField(default=False)
    agen = models.BooleanField(default=False)
    email_confirmed = models.BooleanField(default=False)
    token_code = models.CharField(max_length=10, blank=True)
    limit = models.IntegerField(default=0)
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

    def uncollect(self):
        uncoll = Profile.objects.filter(
            profile_member=self
        ).aggregate(
            rp = Coalesce(Sum('saldo', filter=Q(saldo__lt=0)), V(0))
        )
        return abs(uncoll['rp'])


    def trx_profit(self):
        trx_obj = PembukuanTransaksi.unclosed_book.filter(
            user__profile__profile_member=self
        ).aggregate(
            v_penjualan = Coalesce(Sum('kredit', filter=Q(status_type=9)), V(0)),
            v_beli = Coalesce(Sum('transaksi__responsetransaksi__price', filter=Q(status_type=9)), V(0)) + 
            Coalesce(Sum('bukutrans__responsetransaksi__price', filter=Q(status_type=9)), V(0)) + 
            Coalesce(Sum('bukupln__responsetransaksi__price', filter=Q(status_type=9)), V(0)) + 
            Coalesce(Sum('mpulsa_rbbuku_transaksi__responsetransaksirb__saldo_terpotong', filter=Q(status_type=9)), V(0)) +
            Coalesce(Sum('epln_rbbuku_transaksi__responsetransaksirb__saldo_terpotong', filter=Q(status_type=9)), V(0)) + 
            Coalesce(Sum('etrans_rbbuku_transaksi__responsetransaksirb__saldo_terpotong', filter=Q(status_type=9)), V(0))  +
            Coalesce(Sum('egame_rbbuku_transaksi__responsetransaksirb__saldo_terpotong', filter=Q(status_type=9)), V(0))
        )
        profit = trx_obj['v_penjualan'] - trx_obj['v_beli']
        if self.user.is_staff:
            profit *= 0.8
        return profit

    
    def last_salary(self):
        try :
            sall = Payroll.objects.filter(
                agen = self.user
            ).latest()
            # print(sall)
        except :
            sall = None
        finally:
            return sall

    def c_anggota(self):
        return Profile.objects.filter(
            profile_member = self
        ).count()


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
            elif hasattr(self, 'bukupln') :
                return self.bukupln
            elif hasattr(self, 'mpulsa_rbbuku_transaksi'):
                return self.mpulsa_rbbuku_transaksi
            elif hasattr(self, 'epln_rbbuku_transaksi') :
                return self.epln_rbbuku_transaksi
            elif hasattr(self, 'egame_rbbuku_transaksi'):
                return self.egame_rbbuku_transaksi
            else :
                return self.etrans_rbbuku_transaksi
        except Exception as e:
            return None

    @property
    def harga_beli(self):
        try:
            if hasattr(self, 'transaksi'):
                return self.transaksi.responsetransaksi.price
            elif hasattr(self, 'bukutrans'):
                return self.bukutrans.responsetransaksi.price
            elif hasattr(self, 'bukupln') :
                return self.bukupln.responsetransaksi.price
            elif hasattr(self, 'mpulsa_rbbuku_transaksi'):
                return self.mpulsa_rbbuku_transaksi.responsetransaksirb.saldo_terpotong
            elif hasattr(self, 'epln_rbbuku_transaksi') :
                return self.epln_rbbuku_transaksi.responsetransaksirb.saldo_terpotong
            elif hasattr(self, 'egame_rbbuku_transaksi'):
                return self.egame_rbbuku_transaksi.responsetransaksirb.saldo_terpotong
            else :
                return self.etrans_rbbuku_transaksi.responsetransaksirb.saldo_terpotong
        except Exception as e:
            return 0


    def customer(self):
        try:
            if hasattr(self, 'transaksi'):
                return self.transaksi.phone
            elif hasattr(self, 'bukutrans'):
                return self.bukutrans.phone
            elif hasattr(self, 'bukupln') :
                return self.bukupln.account_num
            elif hasattr(self, 'mpulsa_rbbuku_transaksi'):
                return self.mpulsa_rbbuku_transaksi.phone
            elif hasattr(self, 'epln_rbbuku_transaksi') :
                return self.epln_rbbuku_transaksi.idpel
            elif hasattr(self, 'egame_rbbuku_transaksi'):
                return self.egame_rbbuku_transaksi.phone
            else :
                return self.etrans_rbbuku_transaksi.phone
        except Exception as e:
            return None


    def product_label(self):
        try:
            if hasattr(self, 'transaksi'):
                return self.transaksi.product.keterangan
            elif hasattr(self, 'bukutrans'):
                return self.bukutrans.product.keterangan
            elif hasattr(self, 'bukupln') :
                return self.bukupln.product.nama_produk
            elif hasattr(self, 'mpulsa_rbbuku_transaksi'):
                return self.mpulsa_rbbuku_transaksi.product.keterangan
            elif hasattr(self, 'epln_rbbuku_transaksi') :
                return self.epln_rbbuku_transaksi.product.nama_produk
            elif hasattr(self, 'egame_rbbuku_transaksi'):
                return self.egame_rbbuku_transaksi.product.keterangan
            else :
                return self.etrans_rbbuku_transaksi.product.keterangan
        except Exception as e:
            return None

    
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
    biller = models.CharField(max_length=2, choices=LIST_BILLER, default='SB')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'timestamp'

    def __str__(self):
        return str(self.id)



class Payroll(models.Model):
    agen = models.ForeignKey(User, on_delete=models.CASCADE)
    periode = models.DateField()
    penjualan = models.PositiveIntegerField(default=0)
    piutang = models.PositiveIntegerField(default=0)
    utip = models.PositiveIntegerField(default=0)
    collection = models.PositiveIntegerField(default=0)
    uncollect = models.PositiveIntegerField(default=0)
    salary = models.PositiveIntegerField(default=0)
    complete = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=datetime.now)

    class Meta:
        get_latest_by = 'timestamp'

    def __str__(self):
        return str(self.agen)


class UserPayment(models.Model):
    MPAYMENT = (
        ('MN', 'MANUAL PAYMENT'),
        ('VA', 'VIRTUAL ACCOUNT'),
        ('TR', 'TRANSFER')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    agen = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='agen')
    debit = models.PositiveIntegerField(default=1000)
    method_payment = models.CharField(max_length=2, choices=MPAYMENT, default='MN')
    berita_acara = models.CharField(max_length=200, blank=True)
    setor_payment = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)



class SoldMarking(models.Model):
    transaksi = models.OneToOneField(PembukuanTransaksi, on_delete=models.CASCADE)
    balance = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.transaksi)


class PembukuanPartner(models.Model):
    partner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='partner')
    user_lfg = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flg')
    nominal = models.PositiveIntegerField()
    flag = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = 'timestamp'

    def __str__(self):
        return str(self.nominal)

    




