from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .utils import TokenEmailAndPassoerdResetGerator

TOKEN = TokenEmailAndPassoerdResetGerator()
User = get_user_model()
INPUT = 'p-2 mt-2 mb-2 rounded focus:outline-none bg-zinc-100 border boerder-zinc-300'

class AccountFormRegister(forms.ModelForm):
    passwordConfirm = forms.CharField(label='Confirmar senha', max_length=255, widget=forms.PasswordInput(attrs={'name': 'passwordConfirm', 'required': 'required', 'placeholder': 'Digite a senha novamente.', 'class': INPUT}))
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'name': 'username', 'required': 'required', 'placeholder':'Digite um nome de usuário.', 'class': INPUT}),
            'email': forms.EmailInput(attrs={'name': 'email', 'required': 'required', 'placeholder': 'Digite seu endereço de e-mail.', 'class': INPUT}),
            'password': forms.PasswordInput(attrs={'name': 'password', 'required': 'required', 'placeholder': 'Digite uma senha.', 'class': INPUT}),
        }

    def save(self, *args, **kwargs):
        self.instance.password = make_password(self.cleaned_data['password'])
        return super().save(*args, **kwargs)

class AccountFormLogin(forms.Form):
        email = forms.EmailField(label=_('E-mail'), required=True, widget=forms.EmailInput(attrs={'name': 'email', 'required': 'required', 'placeholder': 'Digite seu endereço de e-mail', 'class': INPUT}))
        password = forms.CharField(label=_('Password'), required=True, widget=forms.PasswordInput(attrs={'name': 'password', 'required': 'required', 'placeholder': 'Digite sua senha', 'class': INPUT}))
        
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.user = None

        def clean_email(self):
            email = self.data.get('email')
            if not User.objects.filter(email=email).exists():
                raise ValidationError('Forneça um endereço de e-mail válido.')

            return email

        def clean(self):
            cleaned_data = super().clean()
            email = cleaned_data.get('email')
            password = cleaned_data.get('password')

            if email and password:
                user = authenticate(username=email, password=password)
                if user is None:
                    raise ValidationError('E-mail ou senha inválidos.')
                
                else:
                    if not user.is_active:
                        raise ValidationError('Sua conta precisa ser ativada. O link de ativação ja foi enviado, verifique seu e-mail.')

                    else:
                        self.user = user
                        
            return cleaned_data

class AccountFormUpdate(forms.ModelForm):
    class Meta: 
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'name': 'username', 'required': 'required', 'placeholder':'Digite um nome de usuário.', 'class': INPUT}),
            'first_name': forms.TextInput(attrs={'name': 'first_name', 'placeholder': 'Digite seu nome.', 'class': INPUT}),
            'last_name': forms.TextInput(attrs={'name': 'last_name', 'placeholder': 'Digite seu sobrenome.', 'class': INPUT}),
            'email': forms.EmailInput(attrs={'name': 'email', 'required': 'required', 'placeholder': 'Digite seu endereço de e-mail.', 'class': INPUT}),
        }
        labels = {
            'first_name': _('Nome'),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        account_id = self.instance.pk

        if User.objects.filter(email=email).exclude(pk=account_id).exists():
            raise ValidationError('certifique-se de fornecer um e-mail válido.')

        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        account_id = self.instance.pk

        if User.objects.filter(username=username).exclude(pk=account_id).exists():
            raise ValidationError('certifique-se de fornecer um username válido.')

        return username
        
class AccountFormEmail(forms.Form):
    email = forms.EmailField(label=_('E-mail'), required=True, widget=forms.EmailInput(attrs={'name': 'email', 'required': 'required', 'placeholder': 'Digite seu endereço de e-mail.', 'class': INPUT}))

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not User.objects.filter(email=email).exists():
            raise ValidationError('Endereço de e-mail não encontrado.')

        return email

class AccountFormConfirm(forms.Form):
    password = forms.CharField(label=_('Senha'), required=True, widget=forms.PasswordInput({'name': 'password', 'required': 'required', 'placeholder': 'Digite sua senha.', 'class': INPUT}))

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise forms.ValidationError('Senha incorreta. Tente novamente.')
            
        return password

class AccountFormResetPassword(forms.Form):
    pk = forms.CharField(widget=forms.HiddenInput(attrs={'name': 'pk'}), required=False, label=None)
    token = forms.CharField(widget=forms.HiddenInput(attrs={'name': 'token'}), required=False, label=None)
    password = forms.CharField(label=_('Password'), required=True, widget=forms.PasswordInput({'name': 'password', 'required': 'required', 'placeholder': 'Digite um nova senha.', 'class': INPUT}))
    passwordConfirm = forms.CharField(label=_('Password confirm'), required=True, widget=forms.PasswordInput(attrs={'name': 'passwordConfirm', 'required': 'required', 'placeholder': 'Digite a senha novamente.', 'class': INPUT})) 
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_pk(self):
        pk = self.cleaned_data.get('pk')

        if not self.user.is_authenticated:
            if not pk.isdigit() or not pk:
                raise ValidationError('Certifique-se de ter copiado a url corretamente.')

        return pk

    def clean_token(self):
        token = self.cleaned_data.get('token')

        if not self.user.is_authenticated:
            if not token:
                raise ValidationError('Certifique-se de ter copiado a url corretamente.')

        return token

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        passwordConfirm = cleaned_data.get('passwordConfirm')

        if password != passwordConfirm:
            raise ValidationError('As senha são diferentes.')

        if not self.user.is_authenticated:
            pk = cleaned_data.get('pk')
            token = cleaned_data.get('token')
            account = User.objects.filter(pk=pk)

            if not account.exists() or not TOKEN.check_token(account[0], token):
                raise ValidationError('Certifique-se de ter copiado a url corretamente.')
            
            self.user = account[0]

        return cleaned_data