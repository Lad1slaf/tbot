from django.db import models

from django.contrib.auth.models import User


class TelegramUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='td_user')
    tg_user_id = models.CharField(max_length=50)
    link = models.URLField(max_length=255)
