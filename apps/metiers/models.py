from django.db import models


class Metier(models.Model):
    nom = models.CharField('nom', max_length=100, unique=True)
    description = models.TextField('description', blank=True)
    image = models.ImageField('image', upload_to='metiers/', blank=True, null=True)
    is_active = models.BooleanField('actif', default=True)
    created_at = models.DateTimeField('date de création', auto_now_add=True)

    class Meta:
        verbose_name = 'Métier'
        verbose_name_plural = 'Métiers'
        ordering = ['nom']

    def __str__(self):
        return self.nom
