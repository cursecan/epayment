# from django.db import models
# from django.contrib.auth.models import User

# from userprofile.models import PembukuanTransaksi
# from .utils import generate_pln_trx


# class Product(models.Model):
#     kode_produk = models.CharField(max_length=10, unique=True)
#     nama_produk = models.CharField(max_length=100)
#     nominal = models.PositiveIntegerField()
#     price = models.PositiveIntegerField()
#     kode_external = models.CharField(max_length=15)
#     price_beli = models.PositiveIntegerField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     update = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return self.kode_internal


# class Transaksi(models.Model):
#     status_number = (
#         (0, 'Success'),
#         (1, 'Pending'),
#         (9, 'Gagal'),
#     )
#     trx_code  = models.CharField(max_length=16, blank=True)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     price = models.PositiveIntegerField(default=0)
#     phone = models.CharField(max_length=20)
#     status = models.PositiveSmallIntegerField(choices=status_number, default=0)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
#     pembukuan = models.ForeignKey(PembukuanTransaksi, on_delete=models.SET_NULL, null=True)
#     timestamp = models.DateTimeField(auto_now_add=True)
#     update = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.trx_code

#     def save(self, *args, **kwargs):
#         if self.trx_code is None or self.trx_code == '':
#             self.trx_code = generate_pln_trx(self)
#         super(Transaksi, self).save(*args, **kwargs)


# class ResponseTransaksi(models.Model):
#     trx = models.OneToOneField(Transaksi, on_delete=models.CASCADE)
#     rc = models.CharField(max_length=30)
#     info = models.CharField()
#     productcode = models.CharField()
#     trxtime = models.CharField()
#     accno = models.CharField()
#     nohp = models.CharField()
#     accname = models.CharField()
#     billperiode = models.CharField()
#     nominal = models.IntegerField(default=0)



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