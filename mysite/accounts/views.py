from urllib import request

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import AdditionalInfoForm, UserRegisterForm
from .tokens import account_activation_token
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy



User = get_user_model()

class AuthView(LoginView):
    template_name = 'accounts/login.html'  # Вкажіть шлях до вашого шаблону входу
    redirect_authenticated_user = True  # Автоматично перенаправляє аутентифікованих користувачів
    next_page = reverse_lazy('accounts/additional_info')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Активуйте свій обліковий запис'
            message = render_to_string('accounts/email_activation.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            email = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
            email.content_subtype = "html"  # Важливо для відправлення HTML-контенту
            email.send()
            return redirect('email_verification_sent')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('additional_info')  # Переконайтеся, що маршрут налаштовано в urls.py
    else:
        return HttpResponse('Посилання для активації недійсне!')

@login_required
def additional_info(request):
    if request.method == 'POST':
        form = AdditionalInfoForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("account")
    else:
        form = AdditionalInfoForm(instance=request.user)
    return render(request, 'accounts/additional_info.html', {'form': form})

def email_verification_sent(request):
    return render(request, 'accounts/email_verification_sent.html')

def account(request):
    return render(request, 'accounts/account.html')


