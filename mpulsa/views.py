from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Transaksi, Product
from .forms import TransaksiModelForm


@login_required
def pulsaTopup(request):
    form = TransaksiModelForm(request.POST or None)
    if request.method == 'POST':
        instance = form.save(commit=False)
        if form.is_valid():
            instance.price = instance.product.price
            instance.user = request.user
            instance.save()

    content = {
        'form': form
    }
    return render(request, 'mpulsa/pulsa-view.html', content)