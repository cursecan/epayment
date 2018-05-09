from rest_framework.generics import ListAPIView

from .serializers import OperatorSerializer, ProdukSerializer
from etransport.models import Operator, Product


class OperatorListView(ListAPIView):
    queryset = Operator.objects.all()
    serializer_class = OperatorSerializer


class ProdukListView(ListAPIView):
    serializer_class = ProdukSerializer

    def get_queryset(self, *args, **kwargs):
        new_queryset = Product.objects.all()
        oper = self.request.GET.get('op', None)

        if oper :
            new_queryset = new_queryset.filter(
                operator__kode = oper
            )

        return new_queryset