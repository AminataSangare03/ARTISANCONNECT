from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import Client, User
from apps.artisans.models import Artisan, Realisation
from apps.avis.models import Avis
from apps.commandes.models import Commande
from apps.demandes.models import DemandeService
from apps.devis.models import Devis
from apps.metiers.models import Metier


class Command(BaseCommand):
    help = 'Initialise des donnees realistes de demonstration pour ArtisanConnect.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Initialisation des donnees ArtisanConnect...'))

        # 1. Metiers
        metiers_data = [
            ('Plomberie', 'Depannage, installation de sanitaires, canalisations et chauffe-eau.'),
            ('Menuiserie', 'Fabrication de meubles sur mesure, portes, fenetres et parquets.'),
            ('Electricite', 'Installation, maintenance electrique, mise aux normes et eclairage.'),
            ('Couture', 'Confection sur mesure, tenues traditionnelles, retouches et ameublement.'),
            ('Soudure', 'Metallerie, ferronnerie d art, portails, antivols et garde-corps.'),
            ('Maconnerie', 'Gros oeuvre, cloisons, dallage, finitions et renovations.'),
            ('Peinture', 'Peinture interieure et exterieure, enduits decoratifs et ravalement.'),
            ('Climatisation', 'Pose, entretien et recharge de systemes de climatisation split et centralises.'),
            ('Mecanique', 'Entretien automobile, diagnostic panne et reparations mecaniques.'),
            ('Coiffure & Esthetique', 'Coiffure a domicile, tresses, soins capillaires et bien-etre.'),
        ]

        metiers_map = {}
        for nom, desc in metiers_data:
            metier, _ = Metier.objects.get_or_create(nom=nom, defaults={'description': desc, 'is_active': True})
            metiers_map[nom] = metier
        self.stdout.write(self.style.SUCCESS(f'{len(metiers_map)} metiers crees ou mis a jour.'))

        # 2. Superadmin
        admin, _ = User.objects.get_or_create(
            email='admin@artisanconnect.ci',
            defaults={
                'first_name': 'Admin',
                'last_name': 'ArtisanConnect',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        admin.set_password('Admin1234!')
        admin.save()

        # 3. Clients
        clients_data = [
            ('fatou.kone@example.com', 'Fatou', 'Kone', '0701020304', 'Abidjan', 'Cocody', 'Riviera Palmeraie, Rue Ministre'),
            ('jean.kouassi@example.com', 'Jean', 'Kouassi', '0705060708', 'Abidjan', 'Plateau', 'Boulevard de la Republique'),
            ('awa.traore@example.com', 'Awa', 'Traore', '0709101112', 'Abidjan', 'Yopougon', 'Quartier Maroc, Carrefour Sable'),
        ]

        clients_map = {}
        for email, fn, ln, tel, ville, quartier, adresse in clients_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': fn,
                    'last_name': ln,
                    'phone_number': tel,
                    'role': 'CLIENT',
                },
            )
            if created or not user.has_usable_password():
                user.set_password('Client1234!')
                user.save()
            profile, _ = Client.objects.get_or_create(
                user=user,
                defaults={'ville': ville, 'quartier': quartier, 'adresse': adresse},
            )
            clients_map[email] = profile
        self.stdout.write(self.style.SUCCESS('Clients de demonstration crees.'))

        # 4. Artisans
        artisans_data = [
            (
                'ibrahim.diop@example.com', 'Ibrahim', 'Diop', '0751525354',
                'Plomberie', 'Plombier qualifie avec 8 ans d experience. Interventions rapides et garanties pour fuites, chauffe-eau et canalisations.',
                8, 'Abidjan', 'Cocody', 'Riviera 3, Cite Riviera', 25000,
            ),
            (
                'moussa.traore@example.com', 'Moussa', 'Traore', '0755565758',
                'Menuiserie', 'Maitre menuisier specialiste du bois massif, cuisines modernes et meubles de salon haut de gamme.',
                12, 'Abidjan', 'Marcory', 'Zone 4, Rue du Canal', 40000,
            ),
            (
                'salif.ouattara@example.com', 'Salif', 'Ouattara', '0759606162',
                'Electricite', 'Electricien du batiment et industriel. Realisation d installations neuves et depannages 7j/7.',
                6, 'Abidjan', 'Treichville', 'Avenue 21, Rue 12', 30000,
            ),
            (
                'aminata.toure@example.com', 'Aminata', 'Toure', '0763646566',
                'Couture', 'Styliste modeliste passionnee. Creation de tenues traditionnelles, robes de mariee et pret-a-porter sur mesure.',
                10, 'Abidjan', 'Plateau', 'Immeuble Kharrat, 2e etage', 35000,
            ),
            (
                'koffi.yao@example.com', 'Koffi', 'Yao', '0767686970',
                'Soudure', 'Ferronnier et soudeur certifie. Fabrication de portails blindes, antivols artistiques et hangars.',
                7, 'Abidjan', 'Yopougon', 'Zone Industrielle Yopougon', 20000,
            ),
            (
                'amadou.diallo@example.com', 'Amadou', 'Diallo', '0771727374',
                'Peinture', 'Artisan peintre decorateur. Peintures interieures lessivables, stucco et ravalements soignes.',
                5, 'Abidjan', 'Koumassi', 'Remblais, Terminus 05', 18000,
            ),
        ]

        artisans_map = {}
        for email, fn, ln, tel, metier_nom, desc, exp, ville, quartier, adresse, tarif in artisans_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': fn,
                    'last_name': ln,
                    'phone_number': tel,
                    'role': 'ARTISAN',
                },
            )
            if created or not user.has_usable_password():
                user.set_password('Artisan1234!')
                user.save()
            artisan, _ = Artisan.objects.get_or_create(
                user=user,
                defaults={
                    'metier': metiers_map[metier_nom],
                    'description': desc,
                    'experience': exp,
                    'ville': ville,
                    'quartier': quartier,
                    'adresse': adresse,
                    'disponibilite': True,
                    'tarif_indicatif': tarif,
                    'telephone_professionnel': tel,
                },
            )
            artisans_map[email] = artisan
        self.stdout.write(self.style.SUCCESS('Artisans de demonstration crees.'))

        # 5. Realisations
        realisations_data = [
            ('ibrahim.diop@example.com', 'Installation sanitaire villa duplex', 'Pose de baignoire balneo, colonne de douche et tuyauterie PER.'),
            ('ibrahim.diop@example.com', 'Remplacement ballon chauffe-eau 150L', 'Demontage ancien materiel et raccordement securise.'),
            ('moussa.traore@example.com', 'Table a manger 8 places en teck massif', 'Finition huile naturelle avec 8 chaises coordonnees.'),
            ('moussa.traore@example.com', 'Dressing sur mesure avec eclairage LED', 'Amenagement complet de chambre parentale avec penderie.'),
            ('salif.ouattara@example.com', 'Tableau electrique tertiaire mis aux normes', 'Installation de disjoncteurs differentiels et parafoudre.'),
            ('aminata.toure@example.com', 'Robe de gala en pagne baoule et dentelle', 'Confection soignee pour reception officielle.'),
            ('koffi.yao@example.com', 'Portail metallique coulissant motorise', 'Structure en acier traite anticorrosion avec motif personnalise.'),
            ('amadou.diallo@example.com', 'Finition peinture salon effet velours', 'Application enduit de lissage et peinture acrylique satin.'),
        ]

        for email, titre, desc in realisations_data:
            artisan = artisans_map.get(email)
            if artisan:
                Realisation.objects.get_or_create(
                    artisan=artisan,
                    titre=titre,
                    defaults={'description': desc},
                )
        self.stdout.write(self.style.SUCCESS('Realisations de demonstration creees.'))

        # 6. Demandes de service
        demande1, _ = DemandeService.objects.get_or_create(
            titre='Fuite d eau urgente sous evier et buanderie',
            defaults={
                'client': clients_map['fatou.kone@example.com'],
                'metier': metiers_map['Plomberie'],
                'description': 'Important suintement d eau sous le bac d evier. Necessite un changement de bonde et joint.',
                'ville': 'Abidjan',
                'quartier': 'Cocody',
                'adresse': 'Riviera Palmeraie',
                'budget_indicatif': 35000,
                'date_souhaitee': date.today() + timedelta(days=2),
                'statut': 'ACCEPTEE',
            },
        )

        demande2, _ = DemandeService.objects.get_or_create(
            titre='Fabrication bibliotheque murale sur mesure',
            defaults={
                'client': clients_map['jean.kouassi@example.com'],
                'metier': metiers_map['Menuiserie'],
                'description': 'Bibliotheque en bois clair avec 5 etageres et rangements bas fermes, dimensions 2m50 x 2m20.',
                'ville': 'Abidjan',
                'quartier': 'Plateau',
                'adresse': 'Boulevard de la Republique',
                'budget_indicatif': 180000,
                'date_souhaitee': date.today() + timedelta(days=10),
                'statut': 'EN_ATTENTE',
            },
        )

        demande3, _ = DemandeService.objects.get_or_create(
            titre='Confection robe traditionnelle pour bapteme',
            defaults={
                'client': clients_map['awa.traore@example.com'],
                'metier': metiers_map['Couture'],
                'description': 'Confection ensemble 3 pieces pour ceremonie familiale avec broderies delicates.',
                'ville': 'Abidjan',
                'quartier': 'Yopougon',
                'adresse': 'Quartier Maroc',
                'budget_indicatif': 50000,
                'date_souhaitee': date.today() + timedelta(days=14),
                'statut': 'EN_ATTENTE',
            },
        )

        # 7. Devis pour demande 1
        devis1, _ = Devis.objects.get_or_create(
            demande=demande1,
            artisan=artisans_map['ibrahim.diop@example.com'],
            defaults={
                'montant': 30000,
                'description': 'Remplacement du siphon, pose de joints neufs et verification d etancheite.',
                'duree_estimee': '3 heures',
                'validite': date.today() + timedelta(days=7),
                'statut': 'ACCEPTE',
            },
        )

        # 8. Commande pour devis 1
        commande1, _ = Commande.objects.get_or_create(
            devis=devis1,
            defaults={
                'client': clients_map['fatou.kone@example.com'],
                'artisan': artisans_map['ibrahim.diop@example.com'],
                'statut': 'CONFIRMEE',
                'date_debut': timezone.now() - timedelta(days=3),
                'date_fin_reelle': timezone.now() - timedelta(days=2),
                'commentaires': 'Intervention impeccable, aucune fuite restante.',
            },
        )

        # 9. Avis pour commande 1
        Avis.objects.get_or_create(
            commande=commande1,
            defaults={
                'client': clients_map['fatou.kone@example.com'],
                'artisan': artisans_map['ibrahim.diop@example.com'],
                'note': 5,
                'commentaire': 'Monsieur Diop est tres ponctuel et professionnel. Travail soigne et propre !',
            },
        )

        # 10. Devis en attente pour demande 2
        Devis.objects.get_or_create(
            demande=demande2,
            artisan=artisans_map['moussa.traore@example.com'],
            defaults={
                'montant': 165000,
                'description': 'Bois d iroko traite, etageres renforcies et vernis de protection satin.',
                'duree_estimee': '7 jours ouvrables',
                'validite': date.today() + timedelta(days=15),
                'statut': 'EN_ATTENTE',
            },
        )

        self.stdout.write(self.style.SUCCESS('Base de donnees initialisee avec succes !'))
        self.stdout.write(self.style.NOTICE("""
Comptes de test disponibles :
- Administrateur : admin@artisanconnect.ci / Admin1234!
- Client 1       : fatou.kone@example.com / Client1234!
- Client 2       : jean.kouassi@example.com / Client1234!
- Artisan Plombier : ibrahim.diop@example.com / Artisan1234!
- Artisan Menuisier: moussa.traore@example.com / Artisan1234!
- Artisan Couturiere: aminata.toure@example.com / Artisan1234!
"""))
