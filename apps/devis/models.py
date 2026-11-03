from django.db import models

from apps.artisans.models import Artisan
from apps.demandes.models import DemandeService


class Devis(models.Model):
    STATUS_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('ACCEPTE', 'Accepté'),
        ('REFUSE', 'Refusé'),
        ('EXPIRE', 'Expiré'),
        ('ANNULE', 'Annulé'),
    ]

    demande = models.ForeignKey(DemandeService, on_delete=models.CASCADE, related_name='devis')
    artisan = models.ForeignKey(Artisan, on_delete=models.CASCADE, related_name='devis_envoyes')
    montant = models.DecimalField('montant', max_digits=10, decimal_places=2)
    description = models.TextField('description')
    duree_estimee = models.CharField('durée estimée', max_length=50, blank=True)
    validite = models.DateField('validité', null=True, blank=True)
    statut = models.CharField('statut', max_length=20, choices=STATUS_CHOICES, default='EN_ATTENTE')
    created_at = models.DateTimeField('date de création', auto_now_add=True)
    updated_at = models.DateTimeField('date de modification', auto_now=True)

    class Meta:
        verbose_name = 'Devis'
        verbose_name_plural = 'Devis'
        ordering = ['-created_at']

    def __str__(self):
        return f'Devis {self.id} - {self.artisan}'

