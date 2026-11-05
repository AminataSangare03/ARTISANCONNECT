from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.metiers.models import Metier


class MetierTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.metier1 = Metier.objects.create(nom='Menuiserie', description='Mobilier et bois')
        self.metier2 = Metier.objects.create(nom='Plomberie', description='Sanitaires et forages', is_active=False)
        self.admin = User.objects.create_user(
            email='admin@test.com',
            password='Password123!',
            role='ADMIN',
            is_staff=True,
        )

    def test_str_representation(self):
        self.assertEqual(str(self.metier1), 'Menuiserie')

    def test_public_list_shows_only_active(self):
        response = self.api.get('/api/v1/metiers/')
        self.assertEqual(response.status_code, 200)
        noms = [item['nom'] for item in response.data['results']]
        self.assertIn('Menuiserie', noms)
        self.assertNotIn('Plomberie', noms)

    def test_search_metier(self):
        response = self.api.get('/api/v1/metiers/?search=bois')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nom'], 'Menuiserie')

    def test_unauthenticated_cannot_create_metier(self):
        response = self.api.post('/api/v1/metiers/', {'nom': 'Serrurerie'}, format='json')
        self.assertIn(response.status_code, [401, 403])

    def test_admin_can_create_metier(self):
        self.api.force_authenticate(user=self.admin)
        response = self.api.post('/api/v1/metiers/', {'nom': 'Serrurerie', 'description': 'Serrures'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Metier.objects.filter(nom='Serrurerie').exists())
