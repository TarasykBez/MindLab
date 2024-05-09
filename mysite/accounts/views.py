from datetime import date
import os
from django.conf import settings
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.http import FileResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from tests.models import TestResult

from .forms import AdditionalInfoForm, ProfilePhotoForm, CaptchaTestForm
from .forms import UserRegisterForm
from .tokens import account_activation_token

User = get_user_model()


def calculate_age(birth_date):
    today = date.today()
    if birth_date:
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    else:
        return "Дата народження не вказана"


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
                return redirect('accounts:show_captcha')
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

def activate(request, uidb64, token):
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
            return redirect('accounts:account')
    else:
        form = AdditionalInfoForm(instance=request.user)
    return render(request, 'accounts/additional_info.html', {'form': form})

def email_verification_sent(request):
    return render(request, 'accounts/email_verification_sent.html')


@login_required
def account(request):
    age = calculate_age(request.user.birth_date)
    return render(request, 'accounts/account.html', {'age': age})

@login_required
def account_reset_data(request):
    if request.method == 'POST':
        info_form = AdditionalInfoForm(request.POST, instance=request.user)
        photo_form = ProfilePhotoForm(request.POST, request.FILES, instance=request.user)

        if info_form.is_valid() and photo_form.is_valid():
            info_form.save()
            photo_form.save()
            return redirect('accounts:account')
    else:
        info_form = AdditionalInfoForm(instance=request.user)
        photo_form = ProfilePhotoForm(instance=request.user)

    return render(request, 'accounts/account_reset_data.html', {'info_form': info_form, 'photo_form': photo_form})

@login_required
def account_test_results(request):
    return render(request, 'accounts/account_test_results.html')

def logout_view(request):
    logout(request)
    return redirect('accounts:register')

def index(request):
    return render(request, 'app/index.html')


@login_required
def test_results_view(request):
    test_results = TestResult.objects.filter(user=request.user)
    return render(request, 'accounts/test_results.html', {'test_results': test_results})

def show_captcha(request):
    # Ініціалізуємо спроби, якщо вони ще не були ініціалізовані
    if 'captcha_attempts' not in request.session:
        request.session['captcha_attempts'] = 0

    if request.method == 'POST':
        form = CaptchaTestForm(request.POST)
        if form.is_valid():
            # Якщо капча валідна, видаляємо інформацію про спроби з сесії та перенаправляємо на сторінку account
            del request.session['captcha_attempts']
            return redirect('accounts:account')
        else:
            # Збільшуємо кількість спроб на 1
            request.session['captcha_attempts'] += 1
            if request.session['captcha_attempts'] >= 5:
                # Якщо спроби вичерпані, видаляємо інформацію про спроби з сесії та перенаправляємо на сторінку реєстрації
                del request.session['captcha_attempts']
                return redirect('accounts:register')  # Переадресація на сторінку реєстрації
    else:
        form = CaptchaTestForm()

    captcha_attempts = request.session.get('captcha_attempts', 0)
    return render(request, 'accounts/captcha.html', {'form': form, 'captcha_attempts': captcha_attempts})

def download_file(request, filename):
    filepath = os.path.join(settings.BASE_DIR, 'files', filename)

    if os.path.exists(filepath):
        response = FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)
        return response
    else:
        return HttpResponse("File not found.", status=404)