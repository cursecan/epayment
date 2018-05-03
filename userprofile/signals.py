from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


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