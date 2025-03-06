from django.shortcuts import render, reverse, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import get_user_model, login as singin, hashers, logout as out, authenticate
from .form import AccountFormRegister, AccountFormLogin, AccountFormUpdate, AccountFormEmail
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

def accounts(request: HttpRequest):
    if request.method == 'GET':
        accounts = User.objects.all()

        return render(request, 'accounts.html', {'accounts': accounts})

def register(request: HttpRequest):
    if request.method == 'GET':
        form = AccountFormRegister()

    else:
        form = AccountFormRegister(request.POST)
        if form.is_valid():
            if form.data.get('password') == form.data.get('passwordConfirm'):
                singup = form.save()

                return HttpResponse('<h2>Conta criada com sucesso, mas precisa ser ativada, verifique seu e-mail.</h2>')

            messages.error(request, 'As senhas não conhecidem.')
            
        else:
            erros = loads(form.errors.as_json())
            erro = ''
            
            if erros.get('username'):
                for e in erros.get('username'):
                    if e['code'] == 'unique':
                        erro = 'Digite um username válido.'
                        break
                    else: 
                        erro = e['message']

            elif erros.get('email'):
                erro = 'Digite um endereço de E-mail válido.'

            messages.error(request, erro)

    return render(request, 'register.html', {'form': form})

def auth(request: HttpRequest, id, token):
    if request.method == 'GET':
        account = User.objects.get(pk=id)
        if TOKEN.check_token(account, token):
            account.is_active = True
            account.save()

            messages.success(request, 'Conta ativada')
            return redirect(reverse('account:login'))

    return HttpResponse('<h1>Token inválido</h1>')

def login(request: HttpRequest):
    if request.method == 'GET':
        form = AccountFormLogin()

    else:
        form = AccountFormLogin(request.POST)

        erros = loads(form.errors.as_json())
        erro = ''

        if erros.get('email'):
            for e in erros.get('email'):
                if e['code'] != 'unique':
                    erro = e['message']

                else:
                    account = User.objects.get(email=form.data.get('email'))
                    user = authenticate(request, username=account.email, password=form.data.get('password'))

                    if user is not None:
                        if user.is_active:
                            singin(request, account)
                            messages.success(request, f'Login realizado com sucesso, {user.username}.')

                            return redirect(reverse('account:accounts'))

                        else:
                            messages.warning(request, 'Sua conta precisa ser ativada, verifique seu e-mail.')
                            return redirect(reverse('account:login'))
                    
                    else:
                        erro = 'Usuaário ou senha inválidos.'
        else:
            erro = 'Conta do usuário não encontrada'

        messages.error(request, erro)

    return render(request, 'login.html', {'form': form})    

def profile(request: HttpRequest):
    account = User.objects.get(email=request.user.email)
    data = model_to_dict(account)

    if request.method == 'GET':
        form = AccountFormUpdate(initial=data)

    else:
        form = AccountFormUpdate(request.POST)
        errors = loads(form.errors.as_json())
        erro = ''

        print(errors)
        for k, v in errors.items():
            for valor in v:
                if valor['code'] != 'unique':
                    erro = valor['message']
            
                else:
                    if form.data.get(k) == data.get(k):
                        break
                    else:
                        erro = f'Forneça um dado valido para o campo {k}'
        if not erro:
            for field, content in form.data.items():
                if content:
                    setattr(account, field, content)
            
            account.save()
            form = AccountFormUpdate(instance=account)
            messages.success(request, 'Dados atualizados com sucesso')
        else:
            messages.error(request, erro)

    return render(request, 'update.html', {'form': form})
    
def logout(request: HttpRequest):
    if request.method == 'GET':
        out(request)
        messages.success(request, 'Sessão encerrada')

    return redirect(reverse('account:accounts'))

def delete(request: HttpRequest):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            redirect(reverse('account:accounts'))

    else:
        password = request.POST.get('password')
        password = hashers.check_password(password, request.user.password)

        if password:
            request.user.delete()
            out(request)
            messages.success(request, 'Conta excluida com sucesso.')

            return redirect(reverse('account:accounts'))

        else:
            messages.error(request, 'Senha incorreta.')

    return render(request, 'confirm.html')

def superuser(request: HttpRequest):
    if request.method == "GET":
        superuser = User.objects.filter(Q(is_staff=True) & Q(is_superuser=True))

        if not superuser:
            user = User.objects.create(username=settings.SUPERUSER_USERNAME, email=settings.SUPERUSER_EMAIL, password=hashers.make_password(settings.SUPERUSER_PASSWORD), is_staff=True, is_superuser=True, is_active=True)
            user.save()

            return HttpResponse(f"""<p>Superuser criado com sucesso. E-mail: {user.email} & password: {settings.SUPERUSER_PASSWORD}.
                                    <a href='{reverse('account:login')}'>Login aqui</a></p>""")
        else:
            return HttpResponse('Superusuário já criado.')

def email(request: HttpRequest):

    if request.method == 'GET':\
        form = AccountFormEmail
    
    else:
        erro = ''
        form = AccountFormEmail(request.POST)
        if not form.is_valid():
            errors = loads(form.errors.as_json())
            for e in errors.get('email'):
                if e['code'] != 'unique':
                    erro = e['message']

                else:
                    account = User.objects.get(email=form.data.get('email'))
                    token = TOKEN.make_token(account)
                    url_absolute = settings.ABSOLUTE_URL + reverse('account:password') + f'?id={account.id}&token={token}'
                    link = format_html(f'<a href="{url_absolute}">Redefinir senha</a>')

                    email = {
                        'assunto': 'Redefinição de senha',
                        'html': 'reset_password/email.html',
                        'txt': 'reset_password/email.txt'
                    }

                    enviar_email_html(account, link, email)

                    return HttpResponse('Enviamos o link de redefinição de conta, verifique seu e-mail.')
        
        else:
            erro = 'Conta do usuário não encontrado.'
        
        messages.error(request, erro)
    
    return render(request, 'search_email.html', {'form': form})

def password(request: HttpRequest):
    context = {}
    if request.method == 'GET':
        _id = request.GET.get('id')
        token = request.GET.get('token')

        if _id or token:
            try:
                account = User.objects.get(pk=_id)
                if not TOKEN.check_token(account, token):
                    raise ValidationError('token inválido')
                context['account'] = account
                context['token'] = token
            except:
                return HttpResponse('Certifique-se que a url está correta. Ou que já tenha expirado.')

        return render(request, 'reset_password.html', context)
    
    else:
        erro = ''
        _id = request.POST.get('id')
        _token = request.POST.get('token')
        _password = request.POST.get('password')
        _passwordConfirm = request.POST.get('passwordConfirm')

        if _password == _passwordConfirm:
            _password == hashers.make_password(_password)

            if request.user.is_authenticated:
                request.user.password = _password
                request.user.save()

            else:
                try:
                    account = User.objects.get(pk=_id)
                    if not TOKEN.check_token(account, _token):
                        print(TOKEN.check_token(account, _token), 'Aqui')
                        raise ValidationError('token inválido')
                except:
                    return HttpResponse('Certifique-se de ter copiado a url corretamente. Ou que já tenha expirado.')

                else:
                    account.password = _password
                    account.save()
        else:
            erro = 'Certifique-se que as senhas sejan iguais.'
        
        if len(erro) > 1:
            messages.error(request, erro)
            if not request.user.is_authenticated:
                return redirect(reverse('account:password') + f'?id={_id}&token={_token}')  
        
        else:
            messages.success(request, 'Senha alterada com sucesso.')
            return redirect(reverse(f'account:login'))