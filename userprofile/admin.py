from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


from .models import Profile, PembukuanTransaksi


class ProfileInline(admin.TabularInline):
    model = Profile
    max_num = 1


class UserAdminCustom(UserAdmin):
    inlines = [ProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)
admin.site.register(PembukuanTransaksi)