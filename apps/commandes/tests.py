from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Client, User
from apps.artisans.models import Artisan
from apps.commandes.models import Commande
from apps.demandes.models import DemandeService
from apps.devis.models import Devis
from apps.metiers.models import Metier


class CommandesTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.metier = Metier.objects.create(nom='Peinture')
        self.client_user = User.objects.create_user(
            email='client@test.com',
            password='Password123!',
            role='CLIENT',
        )
        self.client_profile = Client.objects.create(user=self.client_user)

        self.artisan_user = User.objects.create_user(
            email='peintre@test.com',
            password='Password123!',
            role='ARTISAN',
        )
        self.artisan = Artisan.objects.create(user=self.artisan_user, metier=self.metier)

        self.demande = DemandeService.objects.create(
            client=self.client_profile,
            metier=self.metier,
            titre='Peinture salon',
            description='Peinture blanche',
            ville='Dakar',
        )
        self.devis = Devis.objects.create(
            demande=self.demande,
            artisan=self.artisan,
            montant=60000,
            description='Peinture et fourniture',
            statut='ACCEPTE',
        )
        self.commande = Commande.objects.create(
            devis=self.devis,
            client=self.client_profile,
            artisan=self.artisan,
            statut='EN_ATTENTE',
        )

    def test_workflow_demarrer_and_terminer_and_confirmer(self):
        # 1. Artisan demarre
        self.api.force_authenticate(user=self.artisan_user)
        res_start = self.api.post(f'/api/v1/commandes/{self.commande.id}/demarrer/')
        self.assertEqual(res_start.status_code, 200)
        self.commande.refresh_from_db()
        self.assertEqual(self.commande.statut, 'EN_COURS')
        self.assertIsNotNone(self.commande.date_debut)

        # 2. Artisan termine
        res_finish = self.api.post(f'/api/v1/commandes/{self.commande.id}/terminer/')
        self.assertEqual(res_finish.status_code, 200)
        self.commande.refresh_from_db()
        self.assertEqual(self.commande.statut, 'TERMINEE')
        self.assertIsNotNone(self.commande.date_fin_reelle)

        # 3. Client confirme
        self.api.force_authenticate(user=self.client_user)
        res_confirm = self.api.post(f'/api/v1/commandes/{self.commande.id}/confirmer/')
        self.assertEqual(res_confirm.status_code, 200)
        self.commande.refresh_from_db()
        self.assertEqual(self.commande.statut, 'CONFIRMEE')
