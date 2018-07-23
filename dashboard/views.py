from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.template.loader import render_to_string
from userprofile.forms import SignUpForm
from userprofile.models import Profile

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect('userprofile:index')
    return render(request, 'dashboard/home.html')


def signupView(request):
    form = SignUpForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            subject = 'Register Warungid'
            message = render_to_string(
                'dashboard/register_user_email.html',
                {'user': user}
            )
            user.email_user(subject, message)
            return redirect('home')

    content = {
        'form': form
    }

    return render(request, 'dashboard/signup.html', content)


def waiting_confirmation_user(request):
    return render(request, 'dashboard/regiter_success.html')
