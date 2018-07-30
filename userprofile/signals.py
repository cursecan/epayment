from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import F, Q


from .models import PembukuanTransaksi, Profile, CatatanModal, UserPayment, SoldMarking, PembukuanPartner


# UPDATE SALDO USER DARI RECORD PEMBUKUAN
@receiver(post_save, sender=PembukuanTransaksi)
def saldo_profile(sender, instance, created, **kwargs):
    if created:
        if instance.status_type == 9:
            mysaldo = instance.user.profile.saldo
            if mysaldo >= instance.kredit:
                SoldMarking.objects.create(
                    transaksi=instance,
                    balance = 0
                )
            else :
                if mysaldo < 0:
                    new_balance = instance.kredit
                else:
                    new_balance = abs(mysaldo-instance.kredit)
                    
                SoldMarking.objects.create(
                    transaksi=instance,
                    balance = new_balance
                )

        get_last_modal = CatatanModal.objects.latest()

        instance.balance = instance.user.profile.saldo + instance.debit - instance.kredit
        instance.save()
        Profile.objects.filter(user = instance.user).update(
            saldo=instance.balance,
        )

        # Filter jika memiliki agen
        if instance.user.profile.profile_member:
            Profile.objects.filter(profile_member=instance.user.profile.profile_member).update(
                saldo_agen = F('saldo_agen') - instance.debit
            )



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

        marking_objs = SoldMarking.objects.filter(
            transaksi__user=instance.user,
            balance__gt=0
        )

        new_balance = instance.debit
        for mark in marking_objs:
            new_balance -= mark.balance
            if new_balance >= 0:
                mark.balance =0
                mark.save()
            else :
                mark.balance = abs(new_balance)
                mark.save()
                break

            
@receiver(post_save, sender=PembukuanPartner)
def update_buku_utang_partner(sender, instance, created, **kwargs):
    if created:
        Profile.objects.filter(profile_member=instance.partner.profile).update(
            saldo_agen = F('saldo_agen') + instance.nominal
        )