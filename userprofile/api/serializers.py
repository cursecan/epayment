from rest_framework import serializers

from userprofile.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['telegram', 'email_confirmed', 'phone']