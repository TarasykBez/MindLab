from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Пошта', 'id': 'email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль', 'id': 'pass'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Повтор паролю', 'id': 'repass'}))

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']


class AdditionalInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'patronymic', 'gender', 'birth_date', 'phone_number', 'country', 'visit_reason']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Ім\'я'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Прізвище'}),
            'patronymic': forms.TextInput(attrs={'placeholder': 'По батькові'}),
            'gender': forms.Select(choices=[('male', 'Чоловік'), ('female', 'Жінка')], attrs={'placeholder': 'Стать'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'Дата народження'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Номер телефону'}),
            'country': forms.Select( choices=[('AU', 'Australia'), ('BR', 'Brazil'), ('CA', 'Canada'), ('CN', 'China'), ('FR', 'France'), ('DE', 'Germany'), ('IN', 'India'), ('IT', 'Italy'), ('JP', 'Japan'), ('ES', 'Spain'), ('UA', 'Ukraine'), ('UK', 'UK'), ('USA', 'USA'), ('ZA', 'South Africa'),('AR', 'Argentina'), ('BE', 'Belgium'), ('CL', 'Chile'), ('DK', 'Denmark'), ('EG', 'Egypt'), ('FI', 'Finland'), ('GR', 'Greece'), ('HU', 'Hungary'), ('IE', 'Ireland'), ('MX', 'Mexico'), ('NL', 'Netherlands'), ('NO', 'Norway'), ('PL', 'Poland'), ('PT', 'Portugal'), ('SE', 'Sweden'),],attrs={'placeholder': 'Країна'}),
            'visit_reason': forms.Textarea(attrs={'placeholder': 'Причина візиту сайту'}),
        }

class ProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_photo']
        widgets = {
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CaptchaTestForm(forms.Form):
    captcha = CaptchaField()