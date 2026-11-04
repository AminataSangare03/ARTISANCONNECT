from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import Client, User
from apps.artisans.models import Artisan
from apps.commandes.models import Commande
from apps.demandes.models import DemandeService
from apps.devis.models import Devis
from apps.metiers.models import Metier


class ArtisanConnectAPITests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='Admin1234!',
            first_name='Admin',
            last_name='User',
            role='ADMIN',
        )
        self.client_user = User.objects.create_user(
            email='client@example.com',
            password='Client1234!',
            first_name='Client',
            last_name='Test',
            role='CLIENT',
        )
        self.client_profile = Client.objects.create(
            user=self.client_user,
            ville='Dakar',
            quartier='Plateau',
            adresse='Rue 1',
        )
        self.artisan_user = User.objects.create_user(
            email='artisan@example.com',
            password='Artisan1234!',
            first_name='Artisan',
            last_name='Test',
            role='ARTISAN',
        )
        self.metier = Metier.objects.create(
            nom='Plomberie',
            description='Travaux de plomberie',
            is_active=True,
        )
        self.artisan = Artisan.objects.create(
            user=self.artisan_user,
            metier=self.metier,
            description='Expert plomberie',
            experience=5,
            ville='Dakar',
            quartier='Hlm',
            adresse='Rue 2',
            disponibilite=True,
            tarif_indicatif=25000,
            telephone_professionnel='221777777777',
        )

    def authenticate(self, user):
        self.client_api.force_authenticate(user=user)

    def test_register_client_and_login(self):
        response = self.client_api.post(reverse('register'), {
            'first_name': 'Marie',
            'last_name': 'Sow',
            'email': 'marie@example.com',
            'password': 'SecurePass123!',
            'role': 'CLIENT',
            'ville': 'Saint-Louis',
            'quartier': 'Centre',
            'adresse': 'Rue 22',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email='marie@example.com').exists())
        self.assertTrue(Client.objects.filter(user__email='marie@example.com').exists())

        login_response = self.client_api.post(reverse('token_obtain_pair'), {
            'email': 'marie@example.com',
            'password': 'SecurePass123!',
        }, format='json')
        self.assertEqual(login_response.status_code, 200)
        self.assertIn('access', login_response.data)

    def test_admin_can_create_metier_and_user_can_read(self):
        self.authenticate(self.admin)
        response = self.client_api.post('/api/v1/metiers/', {
            'nom': 'Menuiserie',
            'description': 'Travaux de menuiserie',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Metier.objects.filter(nom='Menuiserie').exists())

        self.client_api.force_authenticate(user=None)
        public_list = self.client_api.get('/api/v1/metiers/')
        self.assertEqual(public_list.status_code, 200)

    def test_artisan_can_create_profile(self):
        artisan_user = User.objects.create_user(
            email='newartisan@example.com',
            password='Artisan1234!',
            first_name='New',
            last_name='Artisan',
            role='ARTISAN',
        )
        self.authenticate(artisan_user)
        response = self.client_api.post('/api/v1/artisans/profile/', {
            'metier': self.metier.id,
            'description': 'Specialiste plomberie',
            'experience': 4,
            'ville': 'Dakar',
            'quartier': 'Yoff',
            'adresse': 'Rue 11',
            'disponibilite': True,
            'tarif_indicatif': 30000,
            'telephone_professionnel': '221777777778',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Artisan.objects.filter(user=artisan_user).exists())

    def test_client_can_publish_request_and_artisan_can_send_quote(self):
        self.authenticate(self.client_user)
        demande_response = self.client_api.post('/api/v1/demandes/', {
            'metier': self.metier.id,
            'titre': 'Fuite d eau',
            'description': 'Besoin d un plombier urgent',
            'ville': 'Dakar',
            'quartier': 'Plateau',
            'adresse': 'Rue principale',
            'budget_indicatif': 50000,
            'date_souhaitee': '2026-12-01',
        }, format='json')
        self.assertEqual(demande_response.status_code, 201)
        demande = DemandeService.objects.get(titre='Fuite d eau')

        self.authenticate(self.artisan_user)
        devis_response = self.client_api.post('/api/v1/devis/', {
            'demande': demande.id,
            'montant': 45000,
            'description': 'Reparation complete',
            'duree_estimee': '3 jours',
            'validite': '2026-12-10',
        }, format='json')
        self.assertEqual(devis_response.status_code, 201)

        self.authenticate(self.client_user)
        devis = Devis.objects.get(demande=demande)
        accept_response = self.client_api.post(f'/api/v1/devis/{devis.id}/accepter/', {}, format='json')
        self.assertEqual(accept_response.status_code, 200)
        self.assertTrue(Commande.objects.filter(devis=devis).exists())

    def test_avis_is_blocked_after_duplicate_submission(self):
        self.authenticate(self.client_user)
        demande = DemandeService.objects.create(
            client=self.client_profile,
            metier=self.metier,
            titre='Travaux',
            description='Test',
            ville='Dakar',
            quartier='Plateau',
            adresse='Rue 99',
            budget_indicatif=40000,
            statut='EN_ATTENTE',
        )
        devis = Devis.objects.create(
            demande=demande,
            artisan=self.artisan,
            montant=35000,
            description='Test devis',
            duree_estimee='2 jours',
        )
        devis.statut = 'ACCEPTE'
        devis.save(update_fields=['statut'])
        demande.statut = 'ACCEPTEE'
        demande.save(update_fields=['statut'])
        commande = Commande.objects.create(
            devis=devis,
            client=self.client_profile,
            artisan=self.artisan,
            statut='CONFIRMEE',
        )

        avis_response = self.client_api.post('/api/v1/avis/', {
            'commande': commande.id,
            'note': 5,
            'commentaire': 'Tres bon travail',
        }, format='json')
        self.assertEqual(avis_response.status_code, 201)

        duplicate_response = self.client_api.post('/api/v1/avis/', {
            'commande': commande.id,
            'note': 4,
            'commentaire': 'Deuxieme avis',
        }, format='json')
        self.assertEqual(duplicate_response.status_code, 400)
