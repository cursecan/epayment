from django.shortcuts import render
from django.http.response import HttpResponse

# Create your views here.
from .models import Transaksi

def strukView(request):
    trx = request.GET.get('id','')

    trx = Transaksi.objects.get(
        trx_code = trx
    )
    return HttpResponse(
        "<html><body><pre>{}</pre></body></html>".format(trx.struk)
    )