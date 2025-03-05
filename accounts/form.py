from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

class AccountFormRegister(forms.ModelForm):
    passwordConfirm = forms.CharField(label='Confirmar senha', required=True, max_length=255, widget=forms.PasswordInput(attrs={'name': 'passwordConfirm'}))
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs={'name': 'password'}),
        }

    def save(self, *args, **kwargs):
        self.instance.password = make_password(self.cleaned_data['password'])

        return super().save(*args, **kwargs)

class AccountFormLogin(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs={'name': 'password'}),
        }

class AccountFormUpdate(forms.ModelForm):
    class Meta: 
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        
class AccountFormEmail(forms.ModelForm):
    class Meta: 
        model = User
        fields = ['email']