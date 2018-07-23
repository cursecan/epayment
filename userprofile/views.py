from django.shortcuts import render, get_object_or_404, redirect
from django.http.response import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F, Sum, Q, Count, Value as V
from django.db.models.functions import TruncDate, Coalesce
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector
from django.utils import timezone

import requests, json, pendulum, datetime

from mpulsa import models as pulsa_model
from etransport import models as trans_model
from epln import models as pln_model
from egame import models as game_model
from .models import PembukuanTransaksi
from .forms import AddSaldoForm, AddSaldoNewForm, ModifyLimit

from .models import Profile, Payroll, UserPayment


# USER INDEX
@login_required(login_url='/login/')
def userindex(request):
    pembukuan_objs = PembukuanTransaksi.unclosed_book.all()
    profile_objs = Profile.objects.all()

    if not request.user.is_staff :
        pembukuan_objs = pembukuan_objs.filter(
            Q(user=request.user) | Q(user__profile__profile_member=request.user.profile)
        )
        profile_objs = profile_objs.filter(
            Q(profile_member = request.user.profile) | Q(user=request.user)
        )

    laporan = pembukuan_objs.aggregate(
        c_trx = Coalesce(Count('user', filter=Q(status_type=9)), V(0)),
        # v_collect = Coalesce(Sum('debit', filter=Q(status_type=1)), V(0)),
        # v_sold = Coalesce(Sum('kredit', filter=Q(status_type=9)), V(0)),
    )

    profile_resue = profile_objs.aggregate(
        c_user = Coalesce(Count('id'), V(0)),
        # v_utip = Coalesce(Sum('saldo', filter=Q(saldo__gt=0)), V(0)),
        v_piutang = -1 * Coalesce(Sum('saldo', filter=Q(saldo__lt=0)), V(0)),
    )

    # t_belanja = fix_collect - profile_resue.get('v_piutang')

    # col_rasio = 0
    # try :
    #     col_rasio = 
    # except:
    #     pass

    content = {
        'laporan': laporan,
        # 'col_rasio': col_rasio,
        'member': profile_resue,
    }
    return render(request, 'userprofile/index.html', content)


# UNRECORD TRX
@login_required(login_url='/login/')
def unrecord_trx(requests):
    # TRX PULSA RB
    trx_pulsa = pulsa_model.TransaksiRb.objects.filter(
        status=0, responsetransaksirb__isnull=True
    )

    trx_transport = trans_model.TransaksiRb.objects.filter(
        status=0, responsetransaksirb__isnull=True
    )

    trx_game = game_model.TransaksiRb.objects.filter(
        status=0, responsetransaksirb__isnull=True
    )

    trx_pln = pln_model.TransaksiRb.objects.filter(
        status=0, responsetransaksirb__isnull=True, request_type='p'
    )


    content = {
        'pulsa': trx_pulsa,
        'trans': trx_transport,
        'games': trx_game,
        'plns' : trx_pln,
    }

    return render(requests, 'userprofile/unrecord_trx.html', content)

# DATASET STATISTIK TRX
@login_required(login_url='/login/')
def trx_dataset(request):
    pembukuan_objs = PembukuanTransaksi.unclosed_book.filter(status_type=9)

    if not request.user.is_staff :
        pembukuan_objs = pembukuan_objs.filter(
            Q(user = request.user) | Q(user__profile__profile_member=request.user.profile)
        )

    data_in_date = dict()

    dataset = pembukuan_objs.annotate(
        date_on = TruncDate('timestamp')
    ).values('date_on').annotate(c_value = Count('id')).values('date_on', 'c_value').order_by()
    
    for i in dataset :
        data_in_date[i['date_on']] = i['c_value']

    sort_days = sorted(list(data_in_date.keys()))

    chart = {
        'chart': {'type': 'line', 'backgroundColor': 'transparent', 'height':350},
        'title': {'text': 'Transaksi'},
        'xAxis': {
            'categories': list(map(lambda x: x.strftime('%d/%m'), sort_days))
        },
        'series': [
            {
                'name': 'Trx',
                'data': list(map(lambda x : data_in_date[x], sort_days)),
            }
        ]
    }
    
    return JsonResponse(chart)


# VIEW DETAIL PENDAPATAN AGEN
@login_required(login_url='/login/')
def pendapatanAgen(request):
    pembukuan_objs = PembukuanTransaksi.unclosed_book.all()
    profile_objs = Profile.objects.all()
    payroll_objs = Payroll.objects.filter(agen=request.user)

    if not request.user.is_staff :
        pembukuan_objs = pembukuan_objs.filter(
            Q(user=request.user) | Q(user__profile__profile_member=request.user.profile)
        )

        profile_objs = profile_objs.filter(
            Q(profile_member = request.user.profile) | Q(user=request.user)
        )

    resume_pemmbukuan = pembukuan_objs.aggregate(
        v_penjualan = Coalesce(Sum('kredit', filter=Q(status_type=9)), V(0)),
        v_collect = Coalesce(Sum('debit', filter=Q(status_type=1)), V(0)),
        v_beli = Coalesce(Sum('transaksi__responsetransaksi__price', filter=Q(status_type=9)), V(0)) + 
        Coalesce(Sum('bukutrans__responsetransaksi__price', filter=Q(status_type=9)), V(0)) + 
        Coalesce(Sum('bukupln__responsetransaksi__price', filter=Q(status_type=9)), V(0)) + 
        Coalesce(Sum('mpulsa_rbbuku_transaksi__responsetransaksirb__saldo_terpotong', filter=Q(status_type=9)), V(0)) +
        Coalesce(Sum('epln_rbbuku_transaksi__responsetransaksirb__saldo_terpotong', filter=Q(status_type=9)), V(0)) + 
        Coalesce(Sum('etrans_rbbuku_transaksi__responsetransaksirb__saldo_terpotong', filter=Q(status_type=9)), V(0))  +
        Coalesce(Sum('egame_rbbuku_transaksi__responsetransaksirb__saldo_terpotong', filter=Q(status_type=9)), V(0))
    )

    resume_profile = profile_objs.aggregate(
        v_utip = Coalesce(Sum('saldo', filter=Q(saldo__gt=0)), V(0)),
        v_piutang = Coalesce(Sum('saldo', filter=Q(saldo__lt=0)), V(0))
    )

    net_collect = resume_pemmbukuan.get('v_collect')
    uncollect = -resume_profile.get('v_piutang')

    sisa_piutang_sebelumnya =  uncollect - resume_pemmbukuan.get('v_penjualan')
    if sisa_piutang_sebelumnya < 0:
        sisa_piutang_sebelumnya = 0
    
    # try :
    #     prensentase_collect = net_collect / (net_collect + uncollect) * 100
    # except :
    #     prensentase_collect = 0

    agen_salary = resume_pemmbukuan.get('v_penjualan') - resume_pemmbukuan.get('v_beli')
    if not request.user.is_staff :
        agen_salary = int(agen_salary * 0.8)

    content = {
        'sisa_piutang': sisa_piutang_sebelumnya,
        'penjualan': resume_pemmbukuan.get('v_penjualan'),
        'total_piutang': uncollect,
        # 'persen_coll': prensentase_collect,
        'net_collect': net_collect,
        'uncollect': uncollect,
        'utip': resume_profile.get('v_utip'),
        'salary': agen_salary,
        'payroll': payroll_objs,
    }

    return render(request, 'userprofile/perolehan_agen.html', content)



# PAYROL
@login_required(login_url='/login/')
def generate_payroll(request):
    agen_objs = Profile.objects.filter(agen=True)
    if request.method == 'POST':
        periode = request.POST.get('periode', None)
        if periode is not None :
            for agen in agen_objs:
                pembukuan_objs = PembukuanTransaksi.unclosed_book.filter(user__profile__profile_member__user__profile=agen)
                profile_objs = Profile.objects.filter(profile_member=agen)
                
                if agen.user.is_staff :
                    pembukuan_objs = PembukuanTransaksi.unclosed_book.filter(timestamp__date__lte=periode)
                    profile_objs = Profile.objects.all()

                resume_pemmbukuan = pembukuan_objs.aggregate(
                    v_penjualan = Coalesce(Sum('kredit', filter=Q(status_type=9)), V(0)),
                    v_collect = Coalesce(Sum('debit', filter=Q(status_type=1)), V(0)),
                    v_beli = Coalesce(Sum('transaksi__responsetransaksi__price', filter=Q(status_type=9)), V(0)) + 
                    Coalesce(Sum('bukutrans__responsetransaksi__price', filter=Q(status_type=9)), V(0)) + 
                    Coalesce(Sum('bukupln__responsetransaksi__price', filter=Q(status_type=9)), V(0)) + 
                    Coalesce(Sum('mpulsa_rbbuku_transaksi__responsetransaksirb__saldo_terpotong', filter=Q(status_type=9)), V(0)) +
                    Coalesce(Sum('epln_rbbuku_transaksi__responsetransaksirb__saldo_terpotong', filter=Q(status_type=9)), V(0)) + 
                    Coalesce(Sum('etrans_rbbuku_transaksi__responsetransaksirb__saldo_terpotong', filter=Q(status_type=9)), V(0))  +
                    Coalesce(Sum('egame_rbbuku_transaksi__responsetransaksirb__saldo_terpotong', filter=Q(status_type=9)), V(0))
                )

                resume_profile = profile_objs.aggregate(
                    v_utip = Coalesce(Sum('saldo', filter=Q(saldo__gt=0)), V(0)),
                    v_piutang = Coalesce(Sum('saldo', filter=Q(saldo__lt=0)), V(0))
                )

                utip = resume_profile.get('v_utip')
                net_collect = resume_pemmbukuan.get('v_collect')

                uncollect = -resume_profile.get('v_piutang')

                penjualan = resume_pemmbukuan.get('v_penjualan')
                piutang = uncollect

                agen_salary = resume_pemmbukuan.get('v_penjualan') - resume_pemmbukuan.get('v_beli')
                if not agen.user.is_staff :
                    agen_salary = int(agen_salary * 0.8)

                # save payroll
                Payroll.objects.create(
                    agen = agen.user,
                    periode = periode,
                    piutang = piutang,
                    utip = utip,
                    collection = net_collect,
                    uncollect = uncollect,
                    salary = agen_salary,
                    penjualan = penjualan,
                )

            PembukuanTransaksi.unclosed_book.update(closed=True)
            return redirect('userprofile:index')
    return render(request, 'userprofile/payroll.html')


# PRODUK
@login_required(login_url='/login/')
def produk_View(request):
    produk_objs = pulsa_model.Product.objects.filter(operator__kode='TEL')
    p_operator = pulsa_model.Operator.objects.values('operator')
    t_operator = trans_model.Operator.objects.values('operator')
    content = {
        'products': produk_objs,
        'pulsa_operators': p_operator,
        'trans_operators': t_operator,
    }
    return render(request, 'userprofile/produk.html', content)


# MEMBER LIST
@login_required(login_url='/login/')
def member_View(request):
    page = request.GET.get('page', 1)
    profile_objs = Profile.objects.all()
    userpayment_objs = UserPayment.objects.filter(setor_payment=False)
    if not request.user.is_staff:
        profile_objs = profile_objs.filter(
            profile_member = request.user.profile
        )
        userpayment_objs = userpayment_objs.filter(agen=request.user)

    
    paginator = Paginator(profile_objs, 10)

    try:
        member_objs = paginator.page(page)
    except PageNotAnInteger:
        member_objs = paginator.page(1)
    except EmptyPage:
        member_objs = paginator.page(paginator.page_range)

    content = {
        'members': member_objs,
        'has_members': profile_objs.exists(),
        'payment': userpayment_objs.aggregate(tunai=Sum('debit', filter=Q(method_payment='MN')), nonTunai=Sum('debit',filter=Q(method_payment__in=('VA','TR'))))
    }

    return render(request, 'userprofile/members.1.html', content)


# DATA COLLECTTION
@login_required(login_url='/login/')
def colrasio_dataset(request):
    buku_objs = PembukuanTransaksi.unclosed_book.all()
    if not request.user.is_staff:
        buku_objs = buku_objs.filter(
            Q(user = request.user) | Q(user__profile__profile_member=request.user.profile)
        )
    
    collection = buku_objs.aggregate(
        v_collect = Coalesce(Sum('debit', filter=Q(status_type=1)), V(0)),
        v_sold = Coalesce(Sum('kredit', filter=Q(status_type=9)), V(0)),
    )

    chart = {
        'chart': {'type': 'pie'},
        'title': {'text': 'Collection Rasio'},
        'series': [
            {
                'name': 'admin',
                'data': [
                    {
                        'name': 'Collect',
                        'y': collection.get('v_collect', 0)
                    },
                    {
                        'name': 'Uncollect',
                        'y': collection.get('v_sold')-collection.get('v_collect')
                    }
                ]
            }
        ]
    }
    return JsonResponse(chart)


# TAMBAH SALDO USER
@login_required(login_url='/login/')
def tambahSaldo_view(request, id):
    profile_obj = get_object_or_404(Profile, pk=id)
    data = dict()
    data['form_is_valid'] = False
    form = AddSaldoForm(request.POST or None)

    content = {
        'form': form,
        'member': profile_obj,
    }

    data['html'] = render_to_string(
        'userprofile/includes/partial_add_saldo.html',
        content,
        request = request
    )

    
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = profile_obj.user
            instance.status_type = 1
            instance.save()
            data['form_is_valid'] = True

            profile_obj.refresh_from_db()
            data['html'] = render_to_string(
                'userprofile/includes/partial_member_data.html',
                {'member': profile_obj},
                request = request
            )
            data['id'] = profile_obj.id

    return JsonResponse(data)


# TAMBAH SALDO USER 2
@login_required(login_url='/login/')
def tambahSaldo2_view(request):
    form = AddSaldoNewForm(request.user, request.POST or None)
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            try :
                instance.agen = instance.user.profile.profile_member.user
            except :
                pass
            instance.save()
            data['form_is_valid'] = True
        else :
            data['form_is_valid'] = False

    content = {
        'form': form,
    }

    data['html'] = render_to_string(
        'userprofile/includes/partial_add_saldo.1.html',
        content,
        request = request
    )
    return JsonResponse(data)


# MODIFY LIMIT SALDO
@login_required(login_url='/login/')
def limitModifierView(request, id):
    profile_obj = get_object_or_404(Profile, pk=id)
    data = dict()
    form =  ModifyLimit(request.POST or None, instance=profile_obj)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else :
            data['form_is_valid'] = False
    
    data['html'] = render_to_string(
        'userprofile/includes/partial_modif_limit_form.html',
        {'form': form, 'member': profile_obj},
        request=request
    )
    return JsonResponse(data)
        


# UPDATE BULK TRX MPULSA
@login_required(login_url='/login/')
def bulk_update_trx_mpulsa(request):
    # NON RAJABILLER
    pulsa_trx = pulsa_model.Transaksi.objects.filter(
        status=0, responsetransaksi__serial_no='', pembukuan__closed=False
    )

    # TRX RAJABILLER
    trx_rajabil = pulsa_model.TransaksiRb.objects.filter(
        status=0, responsetransaksirb__sn='', pembukuan__closed=False
    )

    url_sb = settings.SIAP_URL
    url_rb = [settings.RAJA_URL, settings.RAJA_URL2]

    # BULK RAJABILLER TRX
    for trx_p in trx_rajabil:
        try:
            payload = {
                'method':'rajabiller.datatransaksi',
                'uid': settings.RAJABILLER_ID,
                'pin': settings.RAJABILLER_PASS,
                'tgl1': trx_p.responsetransaksirb.waktu,
                'tgl2': trx_p.responsetransaksirb.waktu,
                'id_transaksi': trx_p.responsetransaksirb.ref2,
                'id_produk': '',
                'idpel': trx_p.phone,
                'limit': '1'
            }

            for url in url_rb:
                try:
                    r = requests.post(url, data=json.dumps(payload), verify=False, headers={'Content-Type':'application/json'})
                    if r.status_code == requests.codes.ok :
                        rson = r.json()
                        if rson['STATUS'] == '00':
                            detail = rson['RESULT_TRANSAKSI'][0].split('#')
                            pulsa_model.ResponseTransaksiRb.objects.filter(
                                trx=trx_p
                            ).update(
                                ket=detail[6],
                                sn=detail[-1],
                                status=detail[5],
                            )

                            if trx_p.responsetransaksirb__status not in ['','00']:
                                trx_p.status = 9
                                trx_p.save(update_fields=['status'])

                        break
                    r.raise_for_status()
                except:
                    pass
        except:
            pass

    return redirect('userprofile:index')


# UPDATE BULK TRX GAME
@login_required(login_url='/login/')
def bulk_update_trx_mgame(request):

    # TRX RAJABILLER
    trx_rajabil = game_model.TransaksiRb.objects.filter(
        status=0, responsetransaksirb__sn='', pembukuan__closed=False
    )

    url_rb = [settings.RAJA_URL, settings.RAJA_URL2]

    # BULK RAJABILLER TRX
    for trx_p in trx_rajabil:
        try:
            payload = {
                'method':'rajabiller.datatransaksi',
                'uid': settings.RAJABILLER_ID,
                'pin': settings.RAJABILLER_PASS,
                'tgl1': trx_p.responsetransaksirb.waktu,
                'tgl2': trx_p.responsetransaksirb.waktu,
                'id_transaksi': trx_p.responsetransaksirb.ref2,
                'id_produk': '',
                'idpel': trx_p.phone,
                'limit': '1'
            }

            for url in url_rb:
                try:
                    r = requests.post(url, data=json.dumps(payload), verify=False, headers={'Content-Type':'application/json'})
                    if r.status_code == requests.codes.ok :
                        rson = r.json()
                        if rson['STATUS'] == '00':
                            detail = rson['RESULT_TRANSAKSI'][0].split('#')
                            game_model.ResponseTransaksiRb.objects.filter(
                                trx=trx_p
                            ).update(
                                ket=detail[6],
                                sn=detail[-1],
                                status=detail[5],
                                saldo_terpotong=detail[7]
                            )

                            if trx_p.responsetransaksirb__status not in ['','00']:
                                trx_p.status = 9
                                trx_p.save(update_fields=['status'])

                        break
                    r.raise_for_status()
                except:
                    pass
        except:
            pass

    return redirect('userprofile:index')


# UPDATE BULK TRX TRANSPORT
@login_required(login_url='/login/')
def bulk_update_trx_etrans(request):

    # TRX RAJABILLER
    trx_rajabil = trans_model.TransaksiRb.objects.filter(
        status=0, responsetransaksirb__sn='', pembukuan__closed=False
    )

    url_rb = [settings.RAJA_URL, settings.RAJA_URL2]

    # BULK RAJABILLER TRX
    for trx_p in trx_rajabil:
        try:
            payload = {
                'method':'rajabiller.datatransaksi',
                'uid': settings.RAJABILLER_ID,
                'pin': settings.RAJABILLER_PASS,
                'tgl1': trx_p.responsetransaksirb.waktu,
                'tgl2': trx_p.responsetransaksirb.waktu,
                'id_transaksi': trx_p.responsetransaksirb.ref2,
                'id_produk': '',
                'idpel': trx_p.phone,
                'limit': '1'
            }

            for url in url_rb:
                try:
                    r = requests.post(url, data=json.dumps(payload), verify=False, headers={'Content-Type':'application/json'})
                    if r.status_code == requests.codes.ok :
                        rson = r.json()
                        if rson['STATUS'] == '00':
                            detail = rson['RESULT_TRANSAKSI'][0].split('#')
                            trans_model.ResponseTransaksiRb.objects.filter(
                                trx=trx_p
                            ).update(
                                ket=detail[6],
                                sn=detail[-1],
                                status=detail[5],
                            )

                            if trx_p.responsetransaksirb__status not in ['','00']:
                                trx_p.status = 9
                                trx_p.save(update_fields=['status'])

                        break
                    r.raise_for_status()
                except:
                    pass
        except:
            pass

    return redirect('userprofile:index')


# UPDATE TRX RESPONSE
@login_required(login_url='/login/')
def checkTrxView(request):
    data_update = []
    pulsa_trx = pulsa_model.Transaksi.objects.filter(
        status=0, responsetransaksi__serial_no=''
    )

    pulsa_trx_rajabil = pulsa_model.TransaksiRb.objects.filter(
        status=0, responsetransaksirb__sn=''
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

    # payload = {
    # 'method':'rajabiller.datatransaksi',
    # 'uid': 'SP118171',
    # 'pin': '009988',
    # 'tgl1': '20180707154120',
    # 'tgl2': '20180707154120',
    # 'id_produk': '',
    # 'idpel': '',
    # 'limit': '10',
    # 'id_transaksi':'1051913619',
    # }


    url_rb = [settings.RAJA_URL, settings.RAJA_URL2]
    for trx_p in pulsa_trx_rajabil:
        try:
            payload = {
                'method':'rajabiller.datatransaksi',
                'uid': settings.RAJABILLER_ID,
                'pin': settings.RAJABILLER_PASS,
                'tgl1': trx_p.responsetransaksirb.waktu,
                'tgl2': trx_p.responsetransaksirb.waktu,
                'id_transaksi': trx_p.responsetransaksirb.ref2,
                'id_produk': trx_p.responsetransaksirb.kode_produk,
                'idpel': trx_p.phone,
                'limit': '1'
            }

            for url in url_rb:
                try:
                    r = requests.post(url, data=json.dumps(payload), verify=False, headers={'Content-Type':'application/json'})
                    if r.status_code == requests.codes.ok :
                        rson = r.json()

                        pulsa_model.ResponseTransaksiRb.objects.filter(
                            trx=trx_p
                        ).update(
                            ket=rson['RESULT_TRANSAKSI'][0],
                            sn=rson['RESULT_TRANSAKSI'][0].split('#')[-1]
                        )

                        
                        break
                    r.raise_for_status()
                except:
                    pass
        except:
            pass


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
                # rc = rson.get('rc', ''),
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

            # trxs = pln_model.ResponseTransaksi.objects.get(trx=trx_pln)
            # try :
            #     trxs.rc = rjson.get('rc','')
            #     trxs.save(update_fields=['rc'])
            # except :
            #     pass

            if trx_pln.responsetransaksi.rc in ['10','11','12','13','20','21','30','31','32','33','34','35','36','37','50','90']:
                trx_pln.status = 9
                trx_pln.save(update_fields=['status'])
                data_update.append(trx_pln.trx_code)
        except:
            pass

    return JsonResponse({'status':', '.join(data_update)})


# UPDATE HARGA RAJABILLER
@login_required(login_url='/login/')
def checkHargaViewRajabiller(request):
    biller_objs = pulsa_model.Biller.objects.filter(biller='RB')
    payload = {
        'method': 'rajabiller.info_produk',
        'uid': settings.RAJABILLER_ID,
        'pin': settings.RAJABILLER_PASS,
        'kode_produk': ''
    }
    url = settings.RAJA_URL

    for biller in biller_objs:
        payload['kode_produk'] = biller.code
        try :
            r = requests.post(url, data=json.dumps(payload), headers={'Content-Type':'application/json'}, verify=False)
            rson = r.json()
            print(rson)
            if rson['STATUS'] == '00':
                pulsa_model.Biller.objects.filter(
                    pk=biller.id
                ).update(price=int(rson['HARGA']))
        except:
            pass
    return redirect('userprofile:index')


# UPDATE HARGA SERVER
@login_required(login_url='/login/')
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


# TRX ALL VIEW
@login_required(login_url='/login/')
def trx_produk_all(request):
    page = request.GET.get('page', 1)
    search = request.GET.get('search', None)
    pembukuan_obj = PembukuanTransaksi.unclosed_book.select_related(
        'user', 'transaksi__product', 'transaksi', 'bukutrans', 'bukutrans__product',
        'bukupln', 'bukupln__product', 'mpulsa_rbbuku_transaksi', 'mpulsa_rbbuku_transaksi__product',
        'epln_rbbuku_transaksi', 'epln_rbbuku_transaksi__product',
        'etrans_rbbuku_transaksi', 'etrans_rbbuku_transaksi__product',
        'egame_rbbuku_transaksi', 'egame_rbbuku_transaksi__product',
    )

    profile_objs = Profile.objects.all()

    # TRX SUCCESS & FAILED
    publish_trx = pembukuan_obj.filter(status_type__in = [3,9])
    
    if search:
        publish_trx = publish_trx.annotate(
            search = SearchVector(
                'transaksi__trx_code', 'transaksi__phone', 
                'bukutrans__trx_code', 'bukutrans__phone',
                'bukupln__trx_code', 'bukupln__account_num',
                'mpulsa_rbbuku_transaksi__trx_code', 'mpulsa_rbbuku_transaksi__phone',
                'user__username', 'epln_rbbuku_transaksi__idpel',
                'etrans_rbbuku_transaksi__phone',
                'egame_rbbuku_transaksi__phone',
            )
        ).filter(
            search = search
        )

    if not request.user.is_staff:
        publish_trx = publish_trx.filter(
            Q(user=request.user) | Q(user__profile__profile_member=request.user.profile)
        )

        pembukuan_obj = pembukuan_obj.filter(
            Q(user=request.user) | Q(user__profile__profile_member=request.user.profile)
        )

        profile_objs = profile_objs.filter(
            Q(profile_member = request.user.profile) | Q(user=request.user)
        )


    buku_laporan = pembukuan_obj.aggregate(
        c_trx = Coalesce(Count('user', filter=Q(status_type=9)), V(0)),
        v_collect = Coalesce(Sum('debit', filter=Q(status_type=1)), V(0)),
        v_sold = Coalesce(Sum('kredit', filter=Q(status_type=9)), V(0)),
        v_beli = Coalesce(Sum('transaksi__responsetransaksi__price', filter=Q(status_type=9)), V(0)) + 
            Coalesce(Sum('bukutrans__responsetransaksi__price', filter=Q(status_type=9)), V(0)) + 
            Coalesce(Sum('bukupln__responsetransaksi__price', filter=Q(status_type=9)), V(0)) + 
            Coalesce(Sum('mpulsa_rbbuku_transaksi__responsetransaksirb__saldo_terpotong', filter=Q(status_type=9)), V(0)) +
            Coalesce(Sum('epln_rbbuku_transaksi__responsetransaksirb__saldo_terpotong', filter=Q(status_type=9)), V(0)) + 
            Coalesce(Sum('etrans_rbbuku_transaksi__responsetransaksirb__saldo_terpotong', filter=Q(status_type=9)), V(0))  +
            Coalesce(Sum('egame_rbbuku_transaksi__responsetransaksirb__saldo_terpotong', filter=Q(status_type=9)), V(0))
    )

    profile_resue = profile_objs.aggregate(
        v_utip = Coalesce(Sum('saldo', filter=Q(saldo__gt=0)), V(0))
    )
    
    paginator = Paginator(publish_trx, 10)

    try :
        trxs = paginator.page(page)
    except PageNotAnInteger:
        trxs = paginator.page(1)
    except EmptyPage:
        trxs = paginator.page(paginator.page_range)

    v_collect = buku_laporan.get('v_collect')-profile_resue.get('v_utip')
    v_profit = 0
    try :
        v_profit = buku_laporan.get('v_sold') - buku_laporan.get('v_beli')
    except : 
        pass

    content = {
        'trxs' : trxs,
        'c_trx': publish_trx.count(),
        'laporan': buku_laporan,
        'prof_resume': profile_resue,
        'collection': v_collect,
        'piutang': buku_laporan.get('v_sold')-v_collect,
        'v_profit': v_profit,
    }
    return render(request, 'userprofile/transaksi.html', content)


# DETAIL TRX PULSA
@login_required(login_url='/login/')
def trx_detail_pulsa_view(request, id):
    data = dict()
    trx_obj = get_object_or_404(pulsa_model.Transaksi, pk=id)

    data['html'] = render_to_string(
        'userprofile/includes/partial_pulsa_trx.html',
        {'trx': trx_obj},
        request=request
    )
    return JsonResponse(data)



#DETAIL TRX PULSA RAJABILER
@login_required(login_url='/login/')
def trx_detail_pulsa_rajabiler_view(request, id):
    data = dict()
    trx_obj = get_object_or_404(pulsa_model.TransaksiRb, pk=id)

    data['html'] = render_to_string(
        'userprofile/includes/partial_pulsa_trx.html',
        {'trx': trx_obj},
        request=request
    )
    return JsonResponse(data)


# DETAIL TRX TRANSPORT
@login_required(login_url='/login/')
def trx_detail_trans_view(request, id):
    data = dict()
    trx_obj = get_object_or_404(trans_model.Transaksi, pk=id)

    data['html'] = render_to_string(
        'userprofile/includes/partial_pulsa_trx.html',
        {'trx': trx_obj},
        request=request
    )
    return JsonResponse(data)


# DETAIL TRX TRANSPORT RAJABILLER
@login_required(login_url='/login/')
def trx_detail_trans_rb_view(request, id):
    data = dict()
    trx_obj = get_object_or_404(trans_model.TransaksiRb, pk=id)

    data['html'] = render_to_string(
        'userprofile/includes/partial_trans_trx.html',
        {'trx': trx_obj},
        request=request
    )
    return JsonResponse(data)


# DETAIL TRX GAME RAJABILLER
@login_required(login_url='/login/')
def trx_detail_game_rb_view(request, id):
    data = dict()
    trx_obj = get_object_or_404(game_model.TransaksiRb, pk=id)

    data['html'] = render_to_string(
        'userprofile/includes/partial_trans_trx.html',
        {'trx': trx_obj},
        request=request
    )
    return JsonResponse(data)


# DETAIL TRX PLN
@login_required(login_url='/login/')
def trx_detail_pln_view(request, id):
    data = dict()
    trx_obj = get_object_or_404(pln_model.Transaksi, pk=id)

    data['html'] = render_to_string(
        'userprofile/includes/partial_pulsa_trx.html',
        {'trx': trx_obj},
        request=request
    )
    return JsonResponse(data)


# DETAIL TRX PLN RAJABILLER
@login_required(login_url='/login/')
def trx_detail_pln_rb_view(request, id):
    data = dict()
    trx_obj = get_object_or_404(pln_model.TransaksiRb, pk=id)

    data['html'] = render_to_string(
        'userprofile/includes/partial_pln_trx.html',
        {'trx': trx_obj},
        request=request
    )
    return JsonResponse(data)



# DELETE TRX PULSA
@login_required(login_url='/login/')
def trx_edit_pulsa_view(request, id):
    data = dict()
    data['id'] = id
    data['form_is_valid'] = False
    trx_obj = get_object_or_404(pulsa_model.Transaksi, pk=id, status__lt=9)
    data['html'] = render_to_string(
        'userprofile/includes/partial_trx_edit.html',
        {'trx': trx_obj},
        request=request
    )

    if request.method == 'POST':
        trx_obj.status = 9
        trx_obj.save(update_fields=['status'])
        data['html'] = render_to_string(
            'userprofile/includes/partial_trx_data.html',
            {'trx': trx_obj},
            request=request
        )
        data['form_is_valid'] = True
    
    return JsonResponse(data)


# DELETE TRX PULSA RAJABILLER
@login_required(login_url='/login/')
def trx_edit_pulsa_view_rajabiller(request, id):
    data = dict()
    data['id'] = id
    data['form_is_valid'] = False
    trx_obj = get_object_or_404(pulsa_model.TransaksiRb, pk=id, status__lt=9)
    data['html'] = render_to_string(
        'userprofile/includes/partial_trx_edit_raja_biller.html',
        {'trx': trx_obj},
        request=request
    )

    if request.method == 'POST':
        trx_obj.status = 9
        trx_obj.save(update_fields=['status'])
        data['html'] = render_to_string(
            'userprofile/includes/partial_trx_data.html',
            {'trx': trx_obj},
            request=request
        )
        data['form_is_valid'] = True
    
    return JsonResponse(data)


# DELETE TRX ETRANS RAJABILLER
@login_required(login_url='/login/')
def trx_edit_trans_view_rajabiller(request, id):
    data = dict()
    data['id'] = id
    data['form_is_valid'] = False
    trx_obj = get_object_or_404(trans_model.TransaksiRb, pk=id, status__lt=9)
    data['html'] = render_to_string(
        'userprofile/includes/partial_trx_edit_trans_rajabiller.html',
        {'trx': trx_obj},
        request=request
    )

    if request.method == 'POST':
        trx_obj.status = 9
        trx_obj.save(update_fields=['status'])
        data['form_is_valid'] = True
    
    return JsonResponse(data)


# DELETE TRX GAME RAJABILLER
@login_required(login_url='/login/')
def trx_edit_game_view_rajabiller(request, id):
    data = dict()
    data['id'] = id
    data['form_is_valid'] = False
    trx_obj = get_object_or_404(game_model.TransaksiRb, pk=id, status__lt=9)
    data['html'] = render_to_string(
        'userprofile/includes/partial_trx_edit_game_rajabiller.html',
        {'trx': trx_obj},
        request=request
    )

    if request.method == 'POST':
        trx_obj.status = 9
        trx_obj.save(update_fields=['status'])
        data['form_is_valid'] = True
    
    return JsonResponse(data)
    


# DELETE TRX PLN RAJABILLER
@login_required(login_url='/login/')
def trx_edit_pln_view_rajabiller(request, id):
    data = dict()
    data['id'] = id
    data['form_is_valid'] = False
    trx_obj = get_object_or_404(pln_model.TransaksiRb, pk=id, status__lt=9)
    data['html'] = render_to_string(
        'userprofile/includes/partial_trx_edit_pln_rajabiller.html',
        {'trx': trx_obj},
        request=request
    )

    if request.method == 'POST':
        trx_obj.status = 9
        trx_obj.save(update_fields=['status'])
        data['form_is_valid'] = True
    
    return JsonResponse(data)





        