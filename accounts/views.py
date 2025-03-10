from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.views import generic, View
from django.contrib.auth import get_user_model, login as singin, logout as out, authenticate, views, mixins, hashers
from .form import AccountFormRegister, AccountFormLogin, AccountFormUpdate, AccountFormEmail, AccountFormConfirm, AccountFormResetPassword
from django.contrib import messages
from json import loads
from django.conf import settings
from django.forms.models import model_to_dict
from .utils import TokenEmailAndPassoerdResetGerator, enviar_email_html
from django.utils.html import format_html
from django.core.validators import ValidationError
from django.db.models import Q

User = get_user_model()
TOKEN = TokenEmailAndPassoerdResetGerator()

class Accounts(generic.ListView):
    model = User
    template_name = 'accounts.html'
    context_object_name = 'accounts'

    def get_queryset(self):
       return User.objects.all()

class Register(generic.CreateView):
    model = User
    form_class = AccountFormRegister
    template_name = 'register.html'

    def form_valid(self, form):
        if form.cleaned_data.get('password') != form.cleaned_data.get('passwordConfirm'):
            messages.error(self.request, 'As senhas não conhecidem.')
            return self.form_invalid(form)
        
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        errors = loads(form.errors.as_json())
        erro_msg = ''
        for k, v in errors.items():
            for valor in v:
                if valor['code'] != 'unique':
                    erro_msg = valor['message']
                else:
                    erro_msg = f'Forneça um dado valido para o campo {k}'
        
        if erro_msg:
            messages.error(self.request, erro_msg)

        return super().form_invalid(form)


    def get_success_url(self):
        messages.warning(self.request, 'Conta criada com sucesso, mas precisa ser ativada, verifique seu e-mail.')
        return reverse('account:login')

class Auth(View):
    def get(self, request, id, token):
        try:
            account = get_object_or_404(User, pk=id)
            if not TOKEN.check_token(account, token):
                raise ValidationError('Token inválido.')
        except:
            return HttpResponse('Certifique-se de ter copiado a url corretamente.')
        else:
            account.is_active = True
            account.save()
            messages.success(request, 'Conta ativada')
            return redirect(reverse('account:login'))

        return redirect(reverse('account:accounts'))

class Login(generic.FormView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    form_class = AccountFormLogin

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        singin(self.request, form.user)
        return super().form_valid(form)

    def form_invalid(self, form):
        errors = loads(form.errors.as_json())
        erro_msg = ''
        for k, v in errors.items():
            for valor in v:
                if valor['code'] != 'unique':
                    erro_msg = valor['message']
        
        if erro_msg:
            messages.error(self.request, erro_msg)

        return super().form_invalid(form)

    def get_success_url(self):
        messages.success(self.request, 'Login realizado com sucesso')
        return reverse('account:accounts')

class Profile(generic.UpdateView):
    model = User
    form_class = AccountFormUpdate
    template_name = 'update.html'

    def form_invalid(self, form):
        errors = loads(form.errors.as_json())
        erro_msg = ''

        for k, v in errors.items():
            for valor in v:
                if valor['code'] != 'unique':
                    erro_msg = valor['message']
        
        messages.error(self.request, erro_msg)
        return super().form_invalid(form)

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        messages.success(self.request, 'Cadastro atualizado com sucesso.')
        return reverse('account:profile')

class Logout(View):
    def get(self, request):
        out(request)
        messages.success(request, 'Sessão encerrada.')
        return redirect(reverse('account:accounts'))
        
class Delete(mixins.LoginRequiredMixin, generic.FormView):
    model = User
    form_class = AccountFormConfirm
    template_name = 'delete.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        account = self.request.user
        out(self.request)
        account.delete()
        messages.success(self.request, 'Conta excluída com sucesso.')
        return super().form_valid(form)

    def form_invalid(self, form):
        error = loads(form.errors.as_json())
        error = error.get('password')[0]['message']
        messages.error(self.request, error)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('account:accounts')

class Superuser(View):
    def get(self, request):
        superuser = User.objects.filter(Q(is_staff=True) & Q(is_superuser=True))

        if not superuser:
            user = User.objects.create(username=settings.SUPERUSER_USERNAME, email=settings.SUPERUSER_EMAIL, password=hashers.make_password(settings.SUPERUSER_PASSWORD), is_staff=True, is_superuser=True, is_active=True)
            user.save()
            return HttpResponse(f"""<p>Superuser criado com sucesso. E-mail: {user.email} & password: {settings.SUPERUSER_PASSWORD}.
                                    <a href='{reverse('account:login')}'>Login aqui</a></p>""")
        else:
            return HttpResponse('Superusuário já criado.')

class Email(generic.FormView):
    model = User
    form_class = AccountFormEmail
    template_name = 'search_email.html'

    def form_valid(self, form):
        account = self.model.objects.get(email=form.cleaned_data.get('email'))
        token = TOKEN.make_token(account)
        url_absolute = settings.ABSOLUTE_URL + reverse('account:password') + f'?pk={account.id}&token={token}'
        link = format_html(f'<a href="{url_absolute}">Redefinir senha</a>')
        email = {
            'assunto': 'Redefinição de senha',
            'html': 'reset_password/email.html',
            'txt': 'reset_password/email.txt'
        }
        enviar_email_html(account, link, email)
        return HttpResponse('Enviamos o link de redefinição de conta, verifique seu e-mail.')

    def form_invalid(self, form):
        error = loads(form.errors.as_json())
        error = error.get('email')[0]['message']
        messages.error(self.request, error)
        return super().form_invalid(form)

class Password(generic.FormView):
    model = User
    template_name = 'reset_password.html'
    form_class = AccountFormResetPassword

    def get_initial(self):
        initial = super().get_initial()
        pk = self.request.GET.get('pk')
        token = self.request.GET.get('token')
        initial['pk'] = pk
        initial['token'] = token
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        password = form.cleaned_data.get('password')
        password = hashers.make_password(password)
        form.user.password = password
        form.user.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        errors = loads(form.errors.as_json())
        erro_msg = ''

        for k, v in errors.items():
            for valor in v:
                erro_msg = valor['message']
                break
        
        messages.error(self.request, erro_msg)
        return super().form_invalid(form)

    def get_success_url(self):
        messages.success(self.request, 'Senha alterada com sucesso.')
        return redirect(reverse('account:login'))