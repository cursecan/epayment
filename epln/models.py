from django.db import models
from django.contrib.auth.models import User

from userprofile.models import PembukuanTransaksi
from .utils import generate_pln_trx

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
    pembukuan = models.ForeignKey(PembukuanTransaksi, on_delete=models.SET_NULL , null=True, blank=True, related_name='bukupln')
    struk = models.TextField(max_length=2000, blank=True)
    ref_sb_trx = models.OneToOneField('self', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

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

# "rc": "RESPONSE_CODE",
# "info": "INFORMATION",
# "productcode": "PRODUCT_CODE",
# "trxtime": "TRANSACTION_TIME",
# "accno": "ACCOUNT_NO",
# "nohp": "NO_HP",
# "accname": "ACCOUNT_NAME",
# "billperiode": "BILL_PERIODE",
# "nominal": "NOMINAL",
# "adminfee": "ADMIN_FEE",
# "price": "PRICE",
# "balance": "BALANCE",
# "urlstruk": "URL_STRUK",
# "refca": "REF_CA",
# "refsb": "REF_SB"


# "rc": "RESPONSE_CODE",
#   "info": "INFORMATION",
#   "productcode": "PRODUCT_CODE",
#   "trxtime": "TRANSACTION_TIME",
#   "accno": "ACCOUNT_NO",
#   "accname": "ACCOUNT_NAME",
#   "billperiode": "BILL_PERIODE",
#   "nominal": "NOMINAL",
#   "adminfee": "ADMIN_FEE",
#   "price": "PRICE",
#   "balance": "BALANCE",
#   "urlstruk": "URL_STRUK",
#   "refca": "REF_CA",
#   "refsb": "REF_SB",
#   "refsbinq": "REF_SB_INQUIRY"