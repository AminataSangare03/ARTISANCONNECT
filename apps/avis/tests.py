from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Client, User
from apps.artisans.models import Artisan
from apps.avis.models import Avis
from apps.commandes.models import Commande
from apps.demandes.models import DemandeService
from apps.devis.models import Devis
from apps.metiers.models import Metier


class AvisTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.metier = Metier.objects.create(nom='Soudure')
        self.client_user = User.objects.create_user(
            email='client@test.com',
            password='Password123!',
            role='CLIENT',
        )
        self.client_profile = Client.objects.create(user=self.client_user)

        self.artisan_user = User.objects.create_user(
            email='soudeur@test.com',
            password='Password123!',
            role='ARTISAN',
        )
        self.artisan = Artisan.objects.create(user=self.artisan_user, metier=self.metier)

        self.demande = DemandeService.objects.create(
            client=self.client_profile,
            metier=self.metier,
            titre='Portail en fer',
            description='Portail coulissant',
            ville='Dakar',
        )
        self.devis = Devis.objects.create(
            demande=self.demande,
            artisan=self.artisan,
            montant=150000,
            description='Fabrication portail',
            statut='ACCEPTE',
        )
        self.commande = Commande.objects.create(
            devis=self.devis,
            client=self.client_profile,
            artisan=self.artisan,
            statut='EN_ATTENTE',
        )

    def test_cannot_review_unconfirmed_order(self):
        self.api.force_authenticate(user=self.client_user)
        response = self.api.post('/api/v1/avis/', {
            'commande': self.commande.id,
            'note': 5,
            'commentaire': 'Bien',
        }, format='json')
        self.assertEqual(response.status_code, 403)

    def test_can_review_confirmed_order_and_average_updates(self):
        self.commande.statut = 'CONFIRMEE'
        self.commande.save()

        self.api.force_authenticate(user=self.client_user)
        response = self.api.post('/api/v1/avis/', {
            'commande': self.commande.id,
            'note': 5,
            'commentaire': 'Travail remarquable et rapide',
        }, format='json')
        self.assertEqual(response.status_code, 201)

        note_res = self.api.get(f'/api/v1/artisans/{self.artisan.id}/note/')
        self.assertEqual(note_res.status_code, 200)
        self.assertEqual(note_res.data['note_moyenne'], 5.0)
        self.assertEqual(note_res.data['nombre_avis'], 1)
