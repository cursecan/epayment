from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from django.contrib.auth.models import User

from datetime import date

from .serializers import OperatorSerializer, ProdukSerializer
from etransport.models import Operator, Product, Transaksi, TransaksiRb, ResponseTransaksiRb, ResponseTransaksi


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

# API LIST PRODUK
class ProductListingApi(ListAPIView):
    serializer_class = ProdukSerializer
    # permission_classes = [AllowAny]

    def get_queryset(self, *args, **kwargs):
        list_query = Product.active_product.all().order_by('operator', 'nominal')
        op = self.request.GET.get('op', None)
        kode = self.request.GET.get('kd', None)
        if kode:
            list_query = list_query.filter(
                kode_internal=kode
            )
            return list_query

        if op :
            list_query = list_query.filter(
                operator__kode = op
            )
        return list_query


class TopupEtransport(APIView):
    def get(self, request, format=None):
        return Response({'forbidend': 1},status=HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        result = dict()
        result['code'] = 0
        result['info'] = ''
        data = request.data
        teleid = data.get('telegram')
        produk_kode = data.get('produk')
        phone = data.get('phone')

        # cek user registered
        user_objs = User.objects.filter(profile__telegram=teleid, profile__active=True)
        if not user_objs.exists():
            result['code'] = 1
            result['status'] = 'User belum terintegrasi telegram/ belum terdaftar.'
            return Response(result, status=HTTP_200_OK)
        user_obj = user_objs.get()
        
        # cek produk avaliable
        produk_objs = Product.active_product.filter(kode_internal=produk_kode)
        if not produk_objs.exists():
            result['code'] = 2
            result['status'] = 'Produk tidak aktif'
            return Response(result, status=HTTP_200_OK)
        produk_obj = produk_objs.first()

        # cek duplikasi transaksi
        trx_recek = Transaksi.objects.filter(phone=phone, 
            product=produk_obj, timestamp__date=date.today(), status=0
        )
        if trx_recek.exists():
            result['code'] = 3
            result['status'] = 'Duplikasi transaksi.'
            return Response(result, status=HTTP_200_OK)

        # validasi limit piutang user
        if user_obj.profile.agen or user_obj.profile.saldo - produk_obj.price >= user_obj.profile.limit:
            trx_obj = Transaksi.objects.create(
                user = user_obj, price = produk_obj.price, 
                product=produk_obj, phone=phone
            )

            user_obj.refresh_from_db()
            trx_obj.refresh_from_db()

            result['trx'] = trx_obj.trx_code
            result['produk'] = produk_obj.keterangan
            result['nominal'] = produk_obj.nominal
            result['price'] = produk_obj.price
            result['saldo'] = user_obj.profile.saldo
            result['phone'] = trx_obj.phone

            if trx_obj.status != 0:
                result['code'] = 11
                result['status'] = 'Transaksi gagal diproses sistem billing.'
            
            return Response(result, status=HTTP_200_OK)

        result['code'] = 4
        result['status'] = 'Saldo tidak cukup/mencapai batas minimal.'
        return Response(result, status=HTTP_200_OK)


# Topup transapport Rabajiller
class TopupEtransportRajaBiller(APIView):
    def get(self, request, format=None):
        return Response({'forbidend': 1},status=HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        result = dict()
        result['code'] = 0
        result['info'] = ''
        data = request.data
        teleid = data.get('telegram')
        produk_kode = data.get('produk')
        phone = data.get('phone')

        # cek user registered
        user_objs = User.objects.filter(profile__telegram=teleid, profile__active=True)
        if not user_objs.exists():
            result['code'] = 1
            result['status'] = 'User belum terintegrasi telegram/ belum terdaftar.'
            return Response(result, status=HTTP_200_OK)
        user_obj = user_objs.get()
        
        # cek produk avaliable
        produk_objs = Product.active_product.filter(kode_internal=produk_kode)
        if not produk_objs.exists():
            result['code'] = 2
            result['status'] = 'Produk tidak aktif'
            return Response(result, status=HTTP_200_OK)
        produk_obj = produk_objs.first()

        # cek duplikasi transaksi
        trx_recek = TransaksiRb.objects.filter(phone=phone, 
            product=produk_obj, timestamp__date=date.today(), status=0
        )
        if trx_recek.exists():
            result['code'] = 3
            result['status'] = 'Duplikasi transaksi.'
            return Response(result, status=HTTP_200_OK)

        # validasi limit piutang user
        if user_obj.profile.agen or user_obj.profile.saldo - produk_obj.price >= user_obj.profile.limit:
            trx_obj = Transaksi.objects.create(
                user = user_obj, price = produk_obj.price, 
                product=produk_obj, phone=phone
            )

            user_obj.refresh_from_db()
            trx_obj.refresh_from_db()

            result['trx'] = trx_obj.trx_code
            result['produk'] = produk_obj.keterangan
            result['nominal'] = produk_obj.nominal
            result['price'] = produk_obj.price
            result['saldo'] = user_obj.profile.saldo
            result['phone'] = trx_obj.phone

            if trx_obj.status != 0:
                result['code'] = 11
                result['status'] = 'Transaksi gagal diproses sistem billing.'
            
            return Response(result, status=HTTP_200_OK)

        result['code'] = 4
        result['status'] = 'Saldo tidak cukup/mencapai batas minimal.'
        return Response(result, status=HTTP_200_OK)
