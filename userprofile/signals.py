from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import F


from .models import PembukuanTransaksi, Profile, CatatanModal, UserPayment


# UPDATE SALDO USER DARI RECORD PEMBUKUAN
@receiver(post_save, sender=PembukuanTransaksi)
def saldo_profile(sender, instance, created, **kwargs):
    if created:
        get_last_modal = CatatanModal.objects.latest()

        instance.balance = instance.user.profile.saldo + instance.debit - instance.kredit
        instance.save()

        Profile.objects.filter(user = instance.user).update(saldo=instance.balance)



# CREATE USER SIGNAL
@receiver(post_save, sender=User)
def initial_profile(sender, instance, created, **kwargs):
    if created:
        profile_obj = Profile.objects.create(
            user=instance, active=True
        )


# TAMBAH SALDO
@receiver(post_save, sender=UserPayment)
def update_bukutransaksi_payment(sender, instance, created, **kwargs):
    if created:
        PembukuanTransaksi.objects.create(
            user = instance.user,
            debit = instance.debit,
            status_type = 1,
        )