from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

class Users(AbstractUser):
    username = models.CharField(max_length=255, unique=True, validators=[MinLengthValidator(8)])
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(_('active'), default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username