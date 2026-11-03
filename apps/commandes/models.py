from django.db import models

from apps.accounts.models import Client
from apps.artisans.models import Artisan
from apps.devis.models import Devis


class Commande(models.Model):
    STATUS_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('CONFIRMEE', 'Confirmée'),
        ('EN_COURS', 'En cours'),
        ('TERMINEE', 'Terminée'),
        ('ANNULEE', 'Annulée'),
    ]

    devis = models.OneToOneField(Devis, on_delete=models.CASCADE, related_name='commande')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='commandes_client')
    artisan = models.ForeignKey(Artisan, on_delete=models.CASCADE, related_name='commandes_artisan')
    date_debut = models.DateTimeField('date de début', null=True, blank=True)
    date_fin_prevue = models.DateTimeField('date de fin prévue', null=True, blank=True)
    date_fin_reelle = models.DateTimeField('date de fin réelle', null=True, blank=True)
    statut = models.CharField('statut', max_length=30, choices=STATUS_CHOICES, default='EN_ATTENTE')
    commentaires = models.TextField('commentaires', blank=True)
    created_at = models.DateTimeField('date de création', auto_now_add=True)
    updated_at = models.DateTimeField('date de modification', auto_now=True)

    class Meta:
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-created_at']

    def __str__(self):
        return f'Commande {self.id} - {self.artisan}'

