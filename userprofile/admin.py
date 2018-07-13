from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportModelAdmin


from .models import Profile, PembukuanTransaksi, CatatanModal, Payroll, UserPayment,SoldMarking
from .forms import PembukuanTransaksiForm
from .resources import PembukuanResource


@admin.register(SoldMarking)
class SoldMarkingAdmin(admin.ModelAdmin):
    list_display = ['transaksi','balance', 'timestamp', 'update']
    class Meta:
        model = SoldMarking

@admin.register(UserPayment)
class UserPayment(admin.ModelAdmin):
    list_display = [
        'timestamp','user', 'agen','method_payment', 'berita_acara', 'debit'
    ]
    class Meta:
        model = UserPayment


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = [
        'agen', 'periode','penjualan','piutang', 'utip', 'collection', 'uncollect', 'salary', 'complete'
    ]
    class Meta:
        model = Payroll


class ProfileInline(admin.TabularInline):
    model = Profile
    max_num = 1


class UserAdminCustom(UserAdmin):
    inlines = [ProfileInline]


@admin.register(PembukuanTransaksi)
class PembukuanTransaksiAdmin(ImportExportModelAdmin):
    form = PembukuanTransaksiForm
    list_display = [
        'id', 'debit', 'kredit', 'balance','status_type', 'keterangan', 'user','parent_id','seq','confrmed', 'timestamp'
    ]
    resource_class = PembukuanResource


@admin.register(CatatanModal)
class CatatanModalAdmin(admin.ModelAdmin):
    class Meta:
        model = CatatanModal

    list_display = ['id','debit', 'kredit', 'saldo', 'type_transaksi','parent_id','confirmed','keterangan','timestamp', 'biller']

admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)
# admin.site.register(SoldMarking)
