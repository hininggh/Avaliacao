from django.contrib.auth.decorators import login_required
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('avaliador', 'Avaliador'),
        ('distribuidor', 'Distribuidor'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    formacao_academica = models.CharField(max_length=255)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="customuser_set",
        related_query_name="customuser",
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_set",
        related_query_name="customuser",
    )