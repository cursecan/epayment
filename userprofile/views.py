from django.shortcuts import render
from django.http.response import JsonResponse
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F, Sum, Q
from django.conf import settings
from django.contrib.auth.decorators import login_required

import requests, json

from mpulsa import models as pulsa_model
from etransport import models as trans_model
from epln import models as pln_model
from .models import PembukuanTransaksi

from .models import Profile

# USER INDEX
@login_required()
def userindex(request):
    profile_objs = Profile.objects.order_by('saldo')
    profile_obj = profile_objs.get(
        user = request.user
    )

    pembukuan_obj = PembukuanTransaksi.objects.all().select_related(
        'user'
    )
    struck_obj = pembukuan_obj.filter(
        status_type = 9
    )[:5]

    if not request.user.is_staff :
        struck_obj = pembukuan_obj.filter(
            Q(user = request.user) | Q(user__profile__profile_member=profile_obj)  
        )
        profile_objs = profile_objs.filter(
            profile_member = profile_obj
        )

    laporan = pembukuan_obj.aggregate(
        t_success = Sum('kredit', filter=Q(status_type=9)),
        t_topup = Sum('debit', filter=Q(status_type=1)),
        t_failed = Sum('kredit', filter=Q(status_type=3)),
        t_reverse = Sum('kredit', filter=Q(status_type=2))
    )

    content = {
        'laporan': laporan,
        'profile': profile_obj,
        'trx_histori': struck_obj,
        'profiles': profile_objs,
    }
    return render(request, 'userprofile/userindex.html', content)


# PRODUK PULSA
@login_required()
def pulsaProdukView(request):
    pulsa_objs_list = pulsa_model.Product.objects.order_by('operator', 'nominal')

    page = request.GET.get('page', 1)
    op = request.GET.get('op', None)
    if op :
        pulsa_objs_list = pulsa_objs_list.filter(operator_id=op).select_related(
            'operator'
        )

    oppulsa_obj = pulsa_model.Operator.objects.values('id', 'operator')
    

    paginator = Paginator(pulsa_objs_list, 10)
    try :
        pulsa_objs = paginator.page(page)
    except PageNotAnInteger :
        pulsa_objs = paginator.page(1)
    except EmptyPage:
        pulsa_objs = paginator.page(paginator.num_pages)

    content = {
        'operators': oppulsa_obj,
        'produks': pulsa_objs,
    }
    return render(request, 'userprofile/produk.html', content)


# PRODUK TRANSPORT
@login_required()
def etransProdukView(request):
    trans_objs_list = trans_model.Product.objects.order_by('operator', 'nominal')
    page = request.GET.get('page', None)

    op = request.GET.get('op', None)
    if op :
        trans_objs_list = trans_produk_list.filter(operator_id=op).select_related(
            'operator'
        )

    optrans_obj = trans_model.Operator.objects.values('id', 'operator')
    

    paginator = Paginator(trans_objs_list, 10)
    try :
        trans_objs = paginator.page(page)
    except PageNotAnInteger :
        trans_objs = paginator.page(1)
    except EmptyPage:
        trans_objs = paginator.page(paginator.num_pages)

    content = {
        'operators': optrans_obj,
        'produks': trans_objs,
    }
    return render(request, 'userprofile/produk.html', content)


# PRODUK LISTRIK
@login_required()
def listrikProdView(request):
    listrik_produk_list = pln_model.Product.objects.order_by('nominal')
    page = request.GET.get('page', None)

    paginator = Paginator(listrik_produk_list, 10)
    try :
        listrik_objs = paginator.page(page)
    except PageNotAnInteger:
        listrik_objs = paginator.page(1)
    except:
        listrik_objs = paginator.page(paginator.num_pages)

    content = {
        'produks': listrik_objs,
    }
    return render(request, 'userprofile/produk_listrik.html', content)


# TRX PULSA
@login_required()
def pulsaTrxView(request):
    trx_pulsa_list = pulsa_model.Transaksi.objects.annotate(
        profit = F('price') - F('responsetransaksi__price')
    )

    page = request.GET.get('page', None)

    paginator = Paginator(trx_pulsa_list, 10)
    try :
        trx_objs = paginator.page(page)
    except PageNotAnInteger:
        trx_objs = paginator.page(1)
    except EmptyPage:
        trx_objs = paginator.page(paginator.num_pages)

    selling_sumary = trx_pulsa_list.aggregate(
        t_profit = Sum('profit', filter=Q(status=0)),
        t_selling = Sum('price', filter=Q(status=0))
    )

    content = {
        'trxs': trx_objs,
        'profit': selling_sumary
    }
    return render(request, 'userprofile/transaksi.html', content)


# TRX TRANSPORT
@login_required()
def transTrxView(request):
    trx_trans_list = trans_model.Transaksi.objects.annotate(
        profit = F('price') - F('responsetransaksi__price')
    )
    page = request.GET.get('page', None)

    paginator = Paginator(trx_trans_list, 10)
    try :
        trx_objs = paginator.page(page)
    except PageNotAnInteger:
        trx_objs = paginator.page(1)
    except EmptyPage:
        trx_objs = paginator.page(paginator.num_pages)

    selling_sumary = trx_trans_list.aggregate(
        t_profit = Sum('profit', filter=Q(status=0)),
        t_selling = Sum('price', filter=Q(status=0))
    )

    content = {
        'trxs': trx_objs,
        'profit': selling_sumary,
    }
    return render(request, 'userprofile/transaksi.html', content)


# TRX LISTRIK
@login_required()
def transListrikView(request):
    trx_listrik_list = pln_model.Transaksi.objects.filter(
        request_type = 'p'    
    ).annotate(
        profit = F('price') - F('nominal') - 400
    )
    page = request.GET.get('page', None)

    paginator = Paginator(trx_listrik_list, 10)
    try :
        trx_objs = paginator.page(page)
    except PageNotAnInteger:
        trx_objs = paginator.page(1)
    except EmptyPage:
        trx_objs = paginator.page(paginator.num_pages)

    selling_sumary = trx_listrik_list.aggregate(
        t_profit = Sum('profit', filter=Q(status=0)),
        t_selling = Sum('price', filter=Q(status=0))
    )

    content = {
        'trxs': trx_objs,
        'profit': selling_sumary
    }
    return render(request, 'userprofile/transaksi_listrik.html', content)


# UPDATE TRX RESPONSE
@login_required()
def checkTrxView(request):
    data_update = []
    pulsa_trx = pulsa_model.Transaksi.objects.filter(
        status=0, responsetransaksi__serial_no=''
    )

    etrans_trx = trans_model.Transaksi.objects.filter(
        status=0, responsetransaksi__serial_no=''
    )

    pln_trx = pln_model.Transaksi.objects.filter(
        request_type='p', status=0, responsetransaksi__serialno=''
    )

    url = settings.SIAP_URL
    payload = {
        "opcode": "status",
        "uid": settings.SIAPBAYAR_ID,
        "pin": settings.SIAPBAYAR_PASS,
        "refca": ""
    }

    for trx_p in pulsa_trx:
        try:
            payload['refca'] = trx_p.trx_code
            r = requests.post(url, data=json.dumps(payload), headers={'Content-Type':'application/json'})
            rjson = r.json()
            pulsa_model.ResponseTransaksi.objects.filter(
                trx=trx_p
            ).update(
                nohp=rjson.get('nohp',''),
                info=rjson.get('info',''),
                product_code=rjson.get('productcode',''),
                trxtime=rjson.get('trxtime',''),
                serial_no=rjson.get('serialno',''),
                price=rjson.get('price', 0),
                balance=rjson.get('balance', 0),
                refca=rjson.get('refca',''),
                refsb=rjson.get('refsb',''),
                response_code=rjson.get('rc',''),
            )
            if trx_p.responsetransaksi.response_code in ['10','11','12','13','20','21','30','31','32','33','34','35','36','37','50','90']:
                trx_p.status = 9
                trx_p.save(update_fields=['status'])
                data_update.append(trx_p.trx_code)

        except:
            pass

    for trx_e in etrans_trx:
        try:
            payload['refca'] = trx_e.trx_code
            r = requests.post(url, data=json.dumps(payload), headers={'Content-Type':'application/json'})
            rjson = r.json()

            trans_model.ResponseTransaksi.objects.filter(
                trx = trx_e
            ).update(
                nohp=rjson.get('nohp',''),
                info=rjson.get('info',''),
                product_code=rjson.get('productcode',''),
                trxtime=rjson.get('trxtime',''),
                serial_no=rjson.get('serialno',''),
                price=rjson.get('price', 0),
                balance=rjson.get('balance', 0),
                refca=rjson.get('refca',''),
                refsb=rjson.get('refsb',''),
                response_code=rjson.get('rc',''),
            )
            if trx_e.responsetransaksi.response_code in ['10','11','12','13','20','21','30','31','32','33','34','35','36','37','50','90']:
                trx_e.status = 9
                trx_e.save(update_fields=['status'])
                data_update.append(trx_e.trx_code)
        except:
            pass

    for trx_pln in pln_trx:
        try:
            payload['refca'] = trx_pln.trx_code
            r = requests.post(url, data=json.dumps(payload), headers={'Content-Type':'application/json'})
            rjson = r.json()

            pln_model.ResponseTransaksi.objects.filter(
                trx = trx_pln
            ).update(
                rc = rson.get('rc', ''),
                info = rson.get('info', ''),
                productcode = rson.get('productcode', ''),
                trxtime = rson.get('trxtime', ''),
                accno = rson.get('accno', ''),
                nohp = rson.get('nohp', ''),
                accname = rson.get('accname', ''),
                billperiode = rson.get('billperiode', ''),
                serialno = rson.get('serialno', ''),
                nominal = rson.get('nominal',0),
                adminfee = rson.get('adminfee', 0),
                price = rson.get(';price', 0),
                balance = rson.get('balance', 0),
                url_struk = rson.get('urlstruk', ''),
                refca = rson.get('refca', ''),
                refsb = rson.get('refsb', '')
            )
            if trx_pln.responsetransaksi.rc in ['10','11','12','13','20','21','30','31','32','33','34','35','36','37','50','90']:
                trx_pln.status = 9
                trx_pln.save(update_fields=['status'])
                data_update.append(trx_pln.trx_code)
        except:
            pass

    return JsonResponse({'status':', '.join(data_update)})


# UPDATE HARGA SERVER
@login_required()
def checkHargaView(request):
    group_name =['TELKOMSEL','ISAT','XL','AXIS','BOLT','FREN','SMART','THREE', 'XL']
    url = settings.SIAP_URL
    payload = {
        "opcode": "price",
        "uid": settings.SIAPBAYAR_ID,
        "pin": settings.SIAPBAYAR_PASS,
        "group": ""
    }
    for i in group_name:
        try :
            payload['group'] = i
            r = requests.post(url, data=json.dumps(payload), headers={'Content-Type':'application/json'})
            rson = r.json()
            if rson['rc'] == '00':
                for prod in rson['products']['product']:
                    try :
                        p_pulsa = pulsa_model.Product.objects.filter(
                            kode_external=prod['productcode']
                        ).update(price_beli=prod['price'])
                    except:
                        pass
        except:
            pass

    group_name =['topup saldo']
    
    for i in group_name:
        try :
            payload['group'] = i
            r = requests.post(url, data=json.dumps(payload), headers={'Content-Type':'application/json'})
            rson = r.json()
            if rson['rc'] == '00':
                for prod in rson['products']['product']:
                    try :
                        p_trans = trans_model.Product.objects.filter(
                            kode_external=prod['productcode']
                        ).update(price_beli=prod['price'])
                    except:
                        pass
        except:
            pass
    
    return JsonResponse({'status':0})


# TRX ALL
@login_required
def trx_produk_all(request):
    page = request.GET.get('page', 1)
    pembukuan_obj = PembukuanTransaksi.objects.all().select_related(
        'user', 'transaksi__product', 'transaksi', 'bukutrans', 'bukutrans__product',
        'bukupln', 'bukupln__product'
    )

    publish_trx = pembukuan_obj.filter(status_type__in = [3,9])

    if not request.user.is_staff:
        publish_trx = publish_trx.filter(
            Q(user=request.user) | Q(user__profile__profile_member=request.user.profile)
        )

    paginator = Paginator(publish_trx, 20)

    try :
        trxs = paginator.page(page)
    except PageNotAnInteger:
        trxs = paginator.page(1)
    except EmptyPage:
        trxs = paginator.page(paginator.page_range)

    content = {
        'trxs' : trxs
    }
    return render(request, 'userprofile/transaksi_produk.html', content)