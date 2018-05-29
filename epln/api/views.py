from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from django.contrib.auth.models import User

from datetime import date

from .serializers import ProductSrializer
from epln.models import Product, Transaksi, ResponseTransaksi

class ProductsListApi(ListAPIView):
    model = Product
    serializer_class = ProductSrializer

    def get_queryset(self, *args, **kwargs):
        list_query = Product.active_product.all().order_by('nominal')
        pcode = self.request.GET.get('p', '')
        if pcode:
            list_query = list_query.filter(kode_produk=pcode)

        return list_query



class TopupTokenListrikView(APIView):
    def get(self, request, format=None):
        return Response({'forbidend': 1},status=HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        result = dict()
        result['code'] = 0
        result['info'] = ''
        data = request.data
        teleid = data.get('telegram')
        produk_kode = data.get('produk')
        user_pln = data.get('account')
        phone = data.get('phone')

        # cek user registered
        user_objs = User.objects.filter(profile__telegram=teleid, profile__active=True)
        if not user_objs.exists():
            result['code'] = 1
            result['status'] = 'User belum terintegrasi telegram/ belum terdaftar.'
            return Response(result, status=HTTP_200_OK)
        user_obj = user_objs.get()

        # cek produk avaliable
        produk_objs = Product.active_product.filter(kode_produk=produk_kode)
        if not produk_objs.exists():
            result['code'] = 2
            result['status'] = 'Produk tidak aktif'
            return Response(result, status=HTTP_200_OK)
        produk_obj = produk_objs.first()

        # cek duplikasi transaksi
        trx_recek = Transaksi.objects.filter(account_num=user_pln, 
            product=produk_obj, timestamp__date=date.today(), status=0,
            request_type='p'
        )
        if trx_recek.exists():
            result['code'] = 3
            result['status'] = 'Duplikasi transaksi.'
            return Response(result, status=HTTP_200_OK)

        if user_obj.profile.agen or user_obj.profile.saldo - produk_obj.price >= user_obj.profile.limit:
            trx_obj_1 = Transaksi.objects.create(
                user = user_obj, price = produk_obj.price, 
                product=produk_obj, phone=phone,
                account_num = user_pln, nominal = produk_obj.nominal
            )

            if trx_obj_1.responsetransaksi.rc == '00':
                trx_obj_2 = Transaksi.objects.create(
                    user = user_obj, price = produk_obj.price, 
                    product=produk_obj, phone=phone,
                    account_num = user_pln, nominal = produk_obj.nominal,
                    request_type='p', ref_sb_trx=trx_obj_1
                )

                user_obj.refresh_from_db()
                trx_obj_2.refresh_from_db()

                result['trx'] = trx_obj_2.trx_code
                result['produk'] = produk_obj.nama_produk
                result['nominal'] = produk_obj.nominal
                result['price'] = produk_obj.price
                result['saldo'] = user_obj.profile.saldo
                result['account_num'] = trx_obj_2.account_num
                result['phone'] = trx_obj_2.phone
                result['struk'] = trx_obj_2.struk
                
                
                return Response(result, status=HTTP_200_OK)
            else:
                result['code'] = 13
                result['status'] = 'Nomor pelanggan tidak valid.'
                return Response(result, status=HTTP_200_OK)
        
        result['code'] = 4
        result['status'] = 'Saldo tidak cukup/mencapai batas minimal.'
        return Response(result, status=HTTP_200_OK)