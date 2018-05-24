from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


from .models import Profile, PembukuanTransaksi
from .forms import PembukuanTransaksiForm


class ProfileInline(admin.TabularInline):
    model = Profile
    max_num = 1


class UserAdminCustom(UserAdmin):
    inlines = [ProfileInline]


@admin.register(PembukuanTransaksi)
class PembukuanTransaksiAdmin(admin.ModelAdmin):
    form = PembukuanTransaksiForm
    list_display = [
        'id', 'debit', 'kredit', 'balance','status_type', 'keterangan', 'user','parent_id','seq','confrmed', 'timestamp'
    ]



admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)
# admin.site.register(PembukuanTransaksi)
