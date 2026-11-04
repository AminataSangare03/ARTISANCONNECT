from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Client, User
from apps.artisans.models import Artisan, Realisation
from apps.avis.models import Avis
from apps.commandes.models import Commande
from apps.demandes.models import DemandeService
from apps.devis.models import Devis
from apps.metiers.models import Metier


class ArtisanTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.metier = Metier.objects.create(nom='Electricite', description='Installations electriques')
        self.artisan_user = User.objects.create_user(
            email='electricien@example.com',
            password='Password123!',
            first_name='Abdou',
            last_name='Diallo',
            role='ARTISAN',
        )
        self.artisan = Artisan.objects.create(
            user=self.artisan_user,
            metier=self.metier,
            description='Electricien certifie',
            experience=7,
            ville='Dakar',
            quartier='Medina',
            disponibilite=True,
            tarif_indicatif=20000,
        )
        self.realisation = Realisation.objects.create(
            artisan=self.artisan,
            titre='Installation tableau electrique',
            description='Tableau norme NFC 15-100',
        )

    def test_public_artisan_list_and_filter(self):
        response = self.api.get('/api/v1/artisans/?ville=Dakar')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['full_name'], 'Abdou Diallo')

    def test_artisan_detail_includes_realisations(self):
        response = self.api.get(f'/api/v1/artisans/{self.artisan.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('realisations', response.data)
        self.assertEqual(len(response.data['realisations']), 1)
        self.assertEqual(response.data['realisations'][0]['titre'], 'Installation tableau electrique')

    def test_artisan_nested_avis_and_note(self):
        note_response = self.api.get(f'/api/v1/artisans/{self.artisan.id}/note/')
        self.assertEqual(note_response.status_code, 200)
        self.assertEqual(note_response.data['note_moyenne'], 0.0)

        avis_response = self.api.get(f'/api/v1/artisans/{self.artisan.id}/avis/')
        self.assertEqual(avis_response.status_code, 200)

    def test_public_can_view_realisations(self):
        response = self.api.get('/api/v1/artisans/realisations/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_artisan_can_add_realisation(self):
        self.api.force_authenticate(user=self.artisan_user)
        response = self.api.post('/api/v1/artisans/realisations/', {
            'titre': 'Cablage complet villa',
            'description': 'Travaux neufs',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Realisation.objects.filter(titre='Cablage complet villa').exists())
