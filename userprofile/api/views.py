from rest_framework.generics import RetrieveUpdateAPIView, UpdateAPIView, ListAPIView
from django.contrib.auth.models import User

from userprofile.models import Profile
from .serializers import ProfileSerializer, UserSerializer

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

    # def get(self, request, *args, **kwargs):
    #     return self.list(request, *args, **kwargs)