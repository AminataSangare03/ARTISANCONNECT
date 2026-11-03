from django.conf import settings
from django.db import models

from apps.metiers.models import Metier


class Artisan(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='artisan_profile')
    metier = models.ForeignKey(Metier, on_delete=models.SET_NULL, null=True, blank=True, related_name='artisans')
    description = models.TextField('description', blank=True)
    experience = models.PositiveIntegerField('expérience (ans)', default=0)
    ville = models.CharField('ville', max_length=100, blank=True)
    quartier = models.CharField('quartier', max_length=100, blank=True)
    adresse = models.TextField('adresse', blank=True)
    disponibilite = models.BooleanField('disponible', default=True)
    tarif_indicatif = models.DecimalField('tarif indicatif', max_digits=10, decimal_places=2, default=0)
    photo_profil = models.ImageField('photo de profil', upload_to='artisans/', blank=True, null=True)
    telephone_professionnel = models.CharField('téléphone professionnel', max_length=20, blank=True)
    created_at = models.DateTimeField('date de création', auto_now_add=True)
    updated_at = models.DateTimeField('date de modification', auto_now=True)

    class Meta:
        verbose_name = 'Artisan'
        verbose_name_plural = 'Artisans'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.email}'


class Realisation(models.Model):
    artisan = models.ForeignKey(Artisan, on_delete=models.CASCADE, related_name='realisations')
    titre = models.CharField('titre', max_length=200)
    description = models.TextField('description', blank=True)
    image = models.ImageField('image', upload_to='realisations/', blank=True, null=True)
    date_realisation = models.DateField('date de réalisation', auto_now_add=True)
    created_at = models.DateTimeField('date de création', auto_now_add=True)

    class Meta:
        verbose_name = 'Réalisation'
        verbose_name_plural = 'Réalisations'
        ordering = ['-date_realisation']

    def __str__(self):
        return self.titre
