from rest_framework.generics import RetrieveUpdateAPIView, UpdateAPIView, ListAPIView
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response

from userprofile.models import Profile, PembukuanTransaksi
from .serializers import ProfileSerializer, UserSerializer, PembukuanSerializer, PembukuanUpdateSerializer, PiutangUserSerializer

class ProfileUpdateView(RetrieveUpdateAPIView):
    # queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = 'token_code'

    def get_queryset(self, *args, **kwargs):
        queryset_list = Profile.objects.filter(
            email_confirmed = False
        )
        return queryset_list

class UserListView(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self, *args, **kwargs):
        list_queryset = User.objects.filter(is_active=True, profile__active=True)
        teleid = self.request.GET.get('t',None)
        if teleid:
            list_queryset = list_queryset.filter(profile__telegram=teleid)
        
        return list_queryset


class PembukuanPayReverseView(ListAPIView):
    queryset = PembukuanTransaksi.objects.filter(confrmed=False, status_type__in = [1, 2])
    serializer_class = PembukuanSerializer


class PembukuanUpdateApi(UpdateAPIView):
    queryset = PembukuanTransaksi.objects.all()
    serializer_class = PembukuanUpdateSerializer
    lookup_field = 'id'


    # def get(self, request, *args, **kwargs):
    #     return self.list(request, *args, **kwargs)


class PiutangUserView(ListAPIView):
    # queryset = Profile.objects.all()
    serializer_class = PiutangUserSerializer

    def get_queryset(self, *args, **kwargs):
        list_user = Profile.objects.filter(
            saldo__lte=-50000, user__is_staff=False
        )
        return list_user