from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

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
        fields = ['first_name', 'last_name', 'patronymic', 'age', 'phone_number', 'country', 'visit_reason']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Ім\'я'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Прізвище'}),
            'patronymic': forms.TextInput(attrs={'placeholder': 'По батькові'}),
            'gender': forms.TextInput(attrs={'placeholder': 'Стать'}),
            'age': forms.NumberInput(attrs={'placeholder': 'Вік'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Номер телефону'}),
            'country': forms.Select(attrs={'placeholder': 'Країна'}),
            'visit_reason': forms.Textarea(attrs={'placeholder': 'Причина візиту сайту'}),
        }