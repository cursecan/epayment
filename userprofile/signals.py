from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import F


from .models import PembukuanTransaksi, Profile


@receiver(post_save, sender=PembukuanTransaksi)
def saldo_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.filter(user = instance.user).update(saldo=instance.balance)


@receiver(post_save, sender=User)
def initial_profile(sender, instance, created, **kwargs):
    if created:
        profile_obj = Profile.objects.create(
            user=instance,
        )

# @receiver(pre_delete, sender=PembukuanTransaksi)
# def delete_failed_trx(sender, instance, **kwargs):
#     profile_objs = Profile.objects.filter(user=instance.user).update(saldo=F('saldo')+instance.kredit)