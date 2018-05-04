from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import Q, F

from datetime import datetime, date

from django.contrib.auth.models import User

from mpulsa.models import Product, Transaksi
from .serializers import TopupSerializer, ProductListSerializer, TransaksiListSerializer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST


# API LIST PRODUK
class ProductListApi(ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self, *args, **kwargs):
        list_query = Product.objects.all()
        prefix = self.request.GET.get('p')
        nominal = self.request.GET.get('n', 0)
        try :
            if prefix and int(nominal) > 0:
                list_query = list_query.filter(
                    operator__prefixnumber__prefix = prefix,
                    nominal = int(nominal),
                )
        except :
            pass
        return list_query


# API VIEW TRANSAKSI LIST
class TransaksiListApi(ListAPIView):
    queryset = Transaksi.objects.all()
    serializer_class = TransaksiListSerializer

    permission_classes = [IsAuthenticated]



# API TOPUP PULSA / TRANSAKSI
class TransaksiCreateApiView(APIView):
    def get(self, request, format=None):
        return Response({'forbidend':1}, status=HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        result = dict()
        data = request.data
        teleid = data.get('teleuser')
        nominal = data.get('amount')

        user_objs = User.objects.filter(profile__telegram=teleid)
        if user_objs.exists():
            result['exists'] = True
            user_obj = user_objs.get()

            phone = user_obj.profile.phone
            prefix = phone[:4]

            prod_objs = Product.objects.filter(
                nominal=nominal, operator__prefixnumber__prefix=prefix
            )
            if prod_objs.exists():
                prod_obj = prod_objs.first()

                trx_prefcek = Transaksi.objects.filter(phone=phone, product=prod_obj, timestamp__date=date.today(), status=0)
                if trx_prefcek.exists:
                    return Response({'invalid':'Duplikasi transaksi, silahkan pilih nominal yang lain'}, status=HTTP_400_BAD_REQUEST) # CHECK 2X TRX DALAM 1 NOMIINAL 1 NUMBER

                if user_obj.profile.saldo - prod_obj.price >= -50000:
                    trx_obj = Transaksi.objects.create(
                        user = user_obj, price = prod_obj.price, product=prod_obj,
                        phone=phone
                    )
                    serializer = TransaksiListSerializer(trx_obj)
                    return Response(serializer.data, status=HTTP_200_OK)
                else:
                    if user_obj.profile.agen:
                        trx_obj = Transaksi.objects.create(
                            user = user_obj, price = prod_obj.price, product=prod_obj,
                            phone=phone
                        )
                        serializer = TransaksiListSerializer(trx_obj)
                        return Response(serializer.data, status=HTTP_200_OK)
                    else :
                        return Response({'invalid':'Silahkan lakukan pembayaran, karena saldo sudah mencapai limit'}, status=HTTP_400_BAD_REQUEST)
            return Response({'invalid':'Produk tidak terdaftar'}, status=HTTP_400_BAD_REQUEST)
        return Response({'invalid':'Telegram anda belum tersinkronisasi, atau user tidak dikenal.'}, status=HTTP_400_BAD_REQUEST)

class TopupCreateApiView(CreateAPIView):
    queryset = Transaksi.objects.all()
    serializer_class = TopupSerializer