from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.accounts.models import Client
from apps.artisans.models import Artisan
from apps.commandes.models import Commande


class Avis(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='avis_publications')
    artisan = models.ForeignKey(Artisan, on_delete=models.CASCADE, related_name='avis_recus')
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name='avis')
    note = models.IntegerField('note', validators=[MinValueValidator(1), MaxValueValidator(5)])
    commentaire = models.TextField('commentaire', blank=True)
    created_at = models.DateTimeField('date de création', auto_now_add=True)
    updated_at = models.DateTimeField('date de modification', auto_now=True)

    class Meta:
        verbose_name = 'Avis'
        verbose_name_plural = 'Avis'
        ordering = ['-created_at']

    def __str__(self):
        return f'Avis {self.id} - {self.artisan}'

