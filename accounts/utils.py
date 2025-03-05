from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class TokenEmailAndPassoerdResetGerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.id) + str(timestamp) + str(user.is_active)

def enviar_email_html(user, url_ativacao, email):
    assunto = email['assunto']
    remetente = settings.EMAIL_HOST
    destinatario = [user.email]
    context = {
        'username': user.username,
        'url_ativacao': url_ativacao
    }
    conteudo_html = render_to_string(email['html'], context)
    conteudo_text = render_to_string(email['txt'], context)
    menssagem = EmailMultiAlternatives(assunto, conteudo_text, remetente, destinatario)
    menssagem.attach_alternative(conteudo_html, 'text/html')
    menssagem.send()