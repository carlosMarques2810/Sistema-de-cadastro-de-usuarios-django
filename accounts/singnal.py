from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from .utils import enviar_email_html, TokenEmailAndPassoerdResetGerator

User = get_user_model()

@receiver(post_save, sender=User)
def enviar_eamil_apos_criacao(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        gerador_token = TokenEmailAndPassoerdResetGerator()
        token = gerador_token.make_token(instance)
        url_absolute = settings.ABSOLUTE_URL + reverse('account:auth', kwargs={'id': instance.id, 'token': token})
        email = {
            'assunto': 'Ativação de Conta.',
            'html': 'active_account/email.html',
            'txt': 'active_account/email.txt',
        }
        enviar_email_html(instance, url_absolute, email)
