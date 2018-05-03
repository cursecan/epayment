from rest_framework.generics import RetrieveUpdateAPIView, UpdateAPIView

from userprofile.models import Profile
from .serializers import ProfileSerializer

class ProfileUpdateView(RetrieveUpdateAPIView):
    # queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = 'token_code'

    def get_queryset(self, *args, **kwargs):
        queryset_list = Profile.objects.filter(
            email_confirmed = False
        )
        return queryset_list