from django.shortcuts import render
from userprofile.forms import SignUpForm
from userprofile.models import Profile

# Create your views here.
def home(request):
    return render(request, 'dashboard/home.html')


def signupView(request):
    form = SignUpForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

    content = {
        'form': form
    }

    return render(request, 'dashboard/signup.html', content)


def waiting_confirmation_user(request):
    return render(request, 'dashboard/waiting_confirmation_user.html')
