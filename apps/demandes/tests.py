from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Client, User
from apps.artisans.models import Artisan
from apps.demandes.models import DemandeService
from apps.metiers.models import Metier


class DemandesTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.metier = Metier.objects.create(nom='Plomberie')
        self.client_user = User.objects.create_user(
            email='client1@test.com',
            password='Password123!',
            first_name='Fatou',
            last_name='Ndiaye',
            role='CLIENT',
        )
        self.client_profile = Client.objects.create(user=self.client_user, ville='Dakar')
        self.artisan_user = User.objects.create_user(
            email='artisan1@test.com',
            password='Password123!',
            role='ARTISAN',
        )
        self.artisan = Artisan.objects.create(user=self.artisan_user, metier=self.metier, ville='Dakar')

    def test_mes_demandes_endpoint_routes_correctly(self):
        DemandeService.objects.create(
            client=self.client_profile,
            metier=self.metier,
            titre='Reparation robinet',
            description='Robinet cassé cuisine',
            ville='Dakar',
        )
        self.api.force_authenticate(user=self.client_user)
        response = self.api.get('/api/v1/demandes/mes-demandes/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['titre'], 'Reparation robinet')

    def test_artisan_sees_matching_demandes_in_mes_demandes(self):
        DemandeService.objects.create(
            client=self.client_profile,
            metier=self.metier,
            titre='Fuite lavabo',
            description='Urgent',
            ville='Dakar',
        )
        self.api.force_authenticate(user=self.artisan_user)
        response = self.api.get('/api/v1/demandes/mes-demandes/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
