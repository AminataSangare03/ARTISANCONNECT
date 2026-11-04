from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Client, User
from apps.artisans.models import Artisan
from apps.commandes.models import Commande
from apps.demandes.models import DemandeService
from apps.devis.models import Devis
from apps.metiers.models import Metier


class DevisTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.metier1 = Metier.objects.create(nom='Menuiserie')
        self.metier2 = Metier.objects.create(nom='Plomberie')

        self.client_user = User.objects.create_user(
            email='client@test.com',
            password='Password123!',
            role='CLIENT',
        )
        self.client_profile = Client.objects.create(user=self.client_user)

        self.artisan_user = User.objects.create_user(
            email='menuisier@test.com',
            password='Password123!',
            role='ARTISAN',
        )
        self.artisan = Artisan.objects.create(
            user=self.artisan_user,
            metier=self.metier1,
        )

        self.demande = DemandeService.objects.create(
            client=self.client_profile,
            metier=self.metier1,
            titre='Table en bois',
            description='Table sur mesure',
            ville='Dakar',
        )

    def test_mes_devis_endpoint_routes_correctly(self):
        Devis.objects.create(
            demande=self.demande,
            artisan=self.artisan,
            montant=75000,
            description='Devis table chene',
        )
        self.api.force_authenticate(user=self.artisan_user)
        response = self.api.get('/api/v1/devis/mes-devis/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(float(response.data['results'][0]['montant']), 75000.0)

    def test_artisan_cannot_quote_for_wrong_metier(self):
        demande_plomberie = DemandeService.objects.create(
            client=self.client_profile,
            metier=self.metier2,
            titre='Fuite tuyau',
            description='Fuite',
            ville='Dakar',
        )
        self.api.force_authenticate(user=self.artisan_user)
        response = self.api.post('/api/v1/devis/', {
            'demande': demande_plomberie.id,
            'montant': 20000,
            'description': 'Je peux essayer',
        }, format='json')
        self.assertEqual(response.status_code, 403)
