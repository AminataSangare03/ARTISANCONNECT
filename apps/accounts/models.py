from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField('email', unique=True)
    phone_number = models.CharField('téléphone', max_length=20, blank=True)
    profile_picture = models.ImageField('photo de profil', upload_to='profile_pictures/', blank=True, null=True)
    role = models.CharField(
        'rôle',
        max_length=20,
        choices=[('CLIENT', 'Client'), ('ARTISAN', 'Artisan'), ('ADMIN', 'Admin')],
        default='CLIENT',
    )
    is_active = models.BooleanField('actif', default=True)
    updated_at = models.DateTimeField('date de modification', auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.email})'


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    ville = models.CharField('ville', max_length=100, blank=True)
    quartier = models.CharField('quartier', max_length=100, blank=True)
    adresse = models.TextField('adresse', blank=True)
    created_at = models.DateTimeField('date de création', auto_now_add=True)
    updated_at = models.DateTimeField('date de modification', auto_now=True)

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return f'Client: {self.user.email}'
