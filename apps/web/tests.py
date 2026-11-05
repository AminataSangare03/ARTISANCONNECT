from django.test import Client as TestClient, TestCase
from django.urls import reverse

from apps.accounts.models import Client, User
from apps.artisans.models import Artisan, Realisation
from apps.demandes.models import DemandeService
from apps.devis.models import Devis
from apps.metiers.models import Metier


class WebPlatformTests(TestCase):
    def setUp(self):
        self.client = TestClient()
        self.metier = Metier.objects.create(nom='Plomberie', description='Depannage plomberie')

        self.client_user = User.objects.create_user(
            email='fatou@example.com',
            password='Password123!',
            first_name='Fatou',
            last_name='Kone',
            role='CLIENT',
        )
        self.client_profile = Client.objects.create(
            user=self.client_user,
            ville='Abidjan',
            quartier='Cocody',
        )

        self.artisan_user = User.objects.create_user(
            email='ibrahim@example.com',
            password='Password123!',
            first_name='Ibrahim',
            last_name='Diop',
            role='ARTISAN',
        )
        self.artisan = Artisan.objects.create(
            user=self.artisan_user,
            metier=self.metier,
            description='Plombier pro',
            experience=8,
            ville='Abidjan',
            quartier='Cocody',
            tarif_indicatif=25000,
            disponibilite=True,
        )
        self.realisation = Realisation.objects.create(
            artisan=self.artisan,
            titre='Pose de chauffe-eau',
            description='Installation chauffe-eau 100L',
        )

    def test_home_page_renders_successfully(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ArtisanConnect')
        self.assertContains(response, 'Plomberie')
        self.assertContains(response, 'Ibrahim Diop')

    def test_artisan_list_and_search_renders(self):
        response = self.client.get(reverse('artisan_list') + '?q=Plomberie')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ibrahim Diop')

    def test_artisan_detail_renders_with_realisations(self):
        response = self.client.get(reverse('artisan_detail', args=[self.artisan.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pose de chauffe-eau')
        self.assertContains(response, '25000 FCFA')

    def test_demande_list_renders(self):
        DemandeService.objects.create(
            client=self.client_profile,
            metier=self.metier,
            titre='Fuite sous lavabo',
            description='Besoin rapide',
            ville='Abidjan',
        )
        response = self.client.get(reverse('demande_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fuite sous lavabo')

    def test_client_can_publish_demande_via_web(self):
        self.client.login(email='fatou@example.com', password='Password123!')
        response = self.client.post(reverse('demande_create'), {
            'metier': self.metier.id,
            'titre': 'Reparation tuyauterie',
            'description': 'Travaux dans la salle de bain',
            'ville': 'Abidjan',
            'quartier': 'Cocody',
            'budget_indicatif': 30000,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(DemandeService.objects.filter(titre='Reparation tuyauterie').exists())

    def test_artisan_can_submit_quote_via_web(self):
        demande = DemandeService.objects.create(
            client=self.client_profile,
            metier=self.metier,
            titre='Changement robinetterie',
            description='Robinet mitigeur',
            ville='Abidjan',
            statut='EN_ATTENTE',
        )
        self.client.login(email='ibrahim@example.com', password='Password123!')
        response = self.client.post(reverse('demande_detail', args=[demande.id]), {
            'montant': 22000,
            'duree_estimee': '1 journee',
            'description': 'Pose et fourniture des raccords',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Devis.objects.filter(demande=demande, artisan=self.artisan).exists())

    def test_web_auth_login_and_logout(self):
        login_res = self.client.post(reverse('web_login'), {
            'email': 'fatou@example.com',
            'password': 'Password123!',
        }, follow=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(login_res.context['user'].is_authenticated)

        logout_res = self.client.get(reverse('web_logout'), follow=True)
        self.assertEqual(logout_res.status_code, 200)
        self.assertFalse(logout_res.context['user'].is_authenticated)
