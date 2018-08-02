from django.conf import settings

from django.shortcuts import render, redirect, get_object_or_404, reverse, Http404
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect

from django.contrib.auth.models import User

from django.core.mail import send_mail

from accounts import helpers
from .forms import CustomUserCreationForm
from .models import *

# https://overiq.com/django/1.10/django-creating-users-using-usercreationform/
def signup(request):
    if request.method == 'POST':
        f = CustomUserCreationForm(request.POST)
        if f.is_valid():

            activation_key = helpers.generate_activation_key(username=request.POST['username'])
            activation_link = f"{request.scheme}://{request.get_host()}/activate/account/?key={activation_key}"

            email_subject = "Pinocchios Account Verification"
            email_content = f"\n\nPlease visit the following link to verify your account:\n\n{activation_link}"

            error = False

            alert = ''
            try:
                send_mail(email_subject, email_content, settings.SERVER_EMAIL, [request.POST['email']])
                alert = 'Account created! Click on the link sent to your email to activate the account'
            except:
                error = True
                alert = 'Unable to send email verification. Please try again'
            if not error:

                user = User.objects.create_user(
                    request.POST['username'],
                    request.POST['email'],
                    request.POST['password1'],
                    first_name=request.POST['first_name'],
                    last_name=request.POST['last_name'],
                    is_active = 0
                )

                customer = Customer()
                customer.activation_key = activation_key
                customer.user = user
                customer.save()

            return render(request, 'registration/signup.html', {'form': f, 'alert': alert})

    else:
        f = CustomUserCreationForm()

    return render(request, 'registration/signup.html', {'form': f})


def activate_account(request):
    key = request.GET['key']
    if not key:
        raise Http404()

    r = get_object_or_404(Customer, activation_key=key, email_validated=False)
    r.user.is_active = True
    r.user.save()
    r.email_validated = True
    r.save()

    return render(request, 'accounts/activated.html')


