from django.conf import settings
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode

from .forms import AdditionalInfoForm
from .forms import UserRegisterForm
from .tokens import account_activation_token

User = get_user_model()

class AuthView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('accounts:additional_info')


def register(request):
    global form
    if request.method == 'POST':
        action = request.POST.get('form_action')

        if action == 'signup':
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
                email.content_subtype = "html"
                email.send()
                return redirect('accounts:email_verification_sent')

        elif action == 'signin':
            email = request.POST.get('email')
            password = request.POST.get('password1')
            user = authenticate(request, email=email, password=password)
            if user is not None and user.is_active:
                login(request, user)
                return redirect('accounts:account')
            else:
                form = UserRegisterForm()  # Reinitialize form for rendering

        elif action == 'reset':
            email = request.POST.get('email')
            user = User.objects.filter(email=email).first()
            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                full_reset_url = request.build_absolute_uri(reset_url)

                send_mail(
                    'Скидання паролю',
                    f'Будь ласка, перейдіть за посиланням для скидання вашого паролю: {full_reset_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                return redirect('accounts:password_reset_done')
            else:
                return render(request, 'accounts/register.html', {'form': None, 'error': 'Користувача з такою електронною поштою не знайдено.'})

    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

def activate(uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('accounts:additional_info')  # Переконайтеся, що маршрут налаштовано в urls.py
    else:
        return HttpResponse('Посилання для активації недійсне!')

@login_required
def additional_info(request):
    if request.method == 'POST':
        form = AdditionalInfoForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("accounts:account")
    else:
        form = AdditionalInfoForm(instance=request.user)
    return render(request, 'accounts/additional_info.html', {'form': form})

def email_verification_sent(request):
    return render(request, 'accounts/email_verification_sent.html')

def account(request):
    return render(request, 'accounts/account.html')


