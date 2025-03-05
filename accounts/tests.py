from django.test import TestCase, override_settings
from django.core import mail
from django.shortcuts import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class TestEmailDeAtivacao(TestCase):
    def test_envio_email_ativacao_via_singal(self):
        account = User.objects.create(username='teste1234', email='teste1234@gmail.com', password='2810')
        self.assertEqual(len(mail.outbox), 1, 'Deveria ter sido enviado exatamente 1 e-mail')
        email_enviado = mail.outbox[0]
        self.assertIn('Ativação de Conta.', email_enviado.subject)
        self.assertIn(account.email, email_enviado.to)
        self.assertIn('/auth/', email_enviado.body)
        self.assertIn(str(account.id), email_enviado.body)