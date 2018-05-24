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
    limit = models.IntegerField(default=-50000)

    objects = models.Manager()
    active_profile = GetActiveProfile()

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        if self.token_code is None or self.token_code == '':
            self.token_code = get_init_profcode(self)
        super(Profile, self).save(*args, **kwargs)


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
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-timestamp']