from django.db import models

from apps.metiers.models import Metier


class DemandeService(models.Model):
    STATUS_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('EN_COURS', 'En cours'),
        ('ACCEPTEE', 'Acceptée'),
        ('TERMINEE', 'Terminée'),
        ('ANNULEE', 'Annulée'),
    ]

    client = models.ForeignKey('accounts.Client', on_delete=models.CASCADE, related_name='demandes')
    metier = models.ForeignKey(Metier, on_delete=models.PROTECT, related_name='demandes')
    titre = models.CharField('titre', max_length=200)
    description = models.TextField('description')
    ville = models.CharField('ville', max_length=100)
    quartier = models.CharField('quartier', max_length=100, blank=True)
    adresse = models.TextField('adresse', blank=True)
    budget_indicatif = models.DecimalField('budget indicatif', max_digits=10, decimal_places=2, default=0)
    date_souhaitee = models.DateField('date souhaitée', null=True, blank=True)
    statut = models.CharField('statut', max_length=30, choices=STATUS_CHOICES, default='EN_ATTENTE')
    created_at = models.DateTimeField('date de création', auto_now_add=True)
    updated_at = models.DateTimeField('date de modification', auto_now=True)

    class Meta:
        verbose_name = 'Demande de service'
        verbose_name_plural = 'Demandes de services'
        ordering = ['-created_at']

    def __str__(self):
        return self.titre
