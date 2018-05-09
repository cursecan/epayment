from rest_framework import serializers

from userprofile.models import Profile
from django.contrib.auth.models import User


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['telegram', 'email_confirmed', 'phone']

class UserSerializer(serializers.ModelSerializer):
    phone = serializers.SerializerMethodField()
    telegram = serializers.SerializerMethodField()
    saldo = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'first_name', 'phone', 'telegram', 'saldo']

    def get_phone(self, obj):
        return obj.profile.phone

    def get_telegram(self, obj):
        return obj.profile.telegram

    def get_saldo(self, obj):
        return obj.profile.saldo