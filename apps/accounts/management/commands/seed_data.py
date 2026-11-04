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
    help = 'Initialise des donnees realistes du Mali (Bamako) pour ArtisanConnect.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Initialisation des donnees ArtisanConnect Mali (Bamako)...'))

        # 1. Metiers
        metiers_data = [
            (
                'Menuiserie',
                'Fabrication de mobilier en bois massif (teck, iroko), cuisines modernes, portes sculptees et parquets.',
                'metiers/menuiserie.jpg',
            ),
            (
                'Plomberie',
                'Installation sanitaire, surpresseurs, forages, chauffe-eau solaires et depannage de fuites.',
                'metiers/plomberie.jpg',
            ),
            (
                'Electricite',
                'Installations domestiques et industrielles, systemes solaires photovoltaiques et armoires de distribution.',
                'metiers/electricite.jpg',
            ),
            (
                'Couture',
                'Stylisme sur mesure, grands boubous brodes, basin riche, tenues contemporaines en bogolan.',
                'metiers/couture.jpg',
            ),
            (
                'Soudure',
                'Ferronnerie d art, portails blindes coulissants, antivols ouvrages, rampes et charpentes metalliques.',
                'metiers/soudure.jpg',
            ),
            (
                'Maconnerie',
                'Gros oeuvre, clotures armees, briques vibrées, dallages, finitions et renovations de villas.',
                'metiers/maconnerie.jpg',
            ),
            (
                'Peinture',
                'Peintures lessivables interieures, stucco, ravalement de facades anti-intemperies et enduits decoratifs.',
                'metiers/peinture.jpg',
            ),
            (
                'Climatisation',
                'Installation de splits inverter, entretien frigorifique, tirage au vide et recharges en gaz ecologique.',
                'metiers/climatisation.jpg',
            ),
            (
                'Mecanique',
                'Entretien et revision 4x4, diagnostic valise electronique, refection suspension, boite et freinage.',
                'metiers/mecanique.jpg',
            ),
            (
                'Coiffure & Esthetique',
                'Tresses africaines, locks, coiffure de ceremonie, soins capillaires aux huiles et beurres de karite.',
                'metiers/coiffure.jpg',
            ),
        ]

        metiers_map = {}
        for nom, desc, img in metiers_data:
            metier, _ = Metier.objects.get_or_create(
                nom=nom,
                defaults={'description': desc, 'is_active': True, 'image': img},
            )
            if img and not metier.image:
                metier.image = img
                metier.save()
            metiers_map[nom] = metier
        self.stdout.write(self.style.SUCCESS(f'{len(metiers_map)} metiers crees ou mis a jour.'))

        # 2. Superadmin
        admin, _ = User.objects.get_or_create(
            email='admin@artisanconnect.ml',
            defaults={
                'first_name': 'Aminata',
                'last_name': 'Sangare',
                'phone_number': '+223 70 00 11 22',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        admin.set_password('Admin1234!')
        admin.save()

        # 3. Clients bamakois (12 profils realistes repartis sur les 6 communes de Bamako)
        clients_data = [
            ('fatoumata.diallo@example.com', 'Fatoumata', 'Diallo', '+223 76 12 34 56', 'Bamako', 'Badalabougou', 'Rue 105, Porte 24 (pres du fleuve)'),
            ('modibo.coulibaly@example.com', 'Modibo', 'Coulibaly', '+223 66 45 67 89', 'Bamako', 'Hamdallaye ACI 2000', 'Boulevard 22 Octobre, Immeuble Albaraka'),
            ('kadidia.traore@example.com', 'Kadidia', 'Traore', '+223 70 89 12 34', 'Bamako', 'Hippodrome', 'Rue Princesse, pres de la Clinique Pasteur'),
            ('amadou.sanogo@example.com', 'Amadou', 'Sanogo', '+223 75 23 45 67', 'Bamako', 'Faladie SEMA', 'Rue 812, Porte 18'),
            ('fanta.keita@example.com', 'Fanta', 'Keita', '+223 72 34 56 78', 'Bamako', 'Korofina Nord', 'Rue 118, Porte 33'),
            ('bakary.traore@example.com', 'Bakary', 'Traore', '+223 68 90 12 34', 'Bamako', 'Bagadadji', 'Grand Marche, Rue 22'),
            ('mariam.toure@example.com', 'Mariam', 'Toure', '+223 77 11 22 33', 'Bamako', 'Dravela', 'Avenue du 20 Janvier, Porte 45'),
            ('ousmane.diarra@example.com', 'Ousmane', 'Diarra', '+223 73 44 55 66', 'Bamako', 'Lafiabougou', 'Rue 340, pres de l Ecole Maternelle'),
            ('aissata.samake@example.com', 'Aissata', 'Samake', '+223 67 88 99 00', 'Bamako', 'Daoudabougou', 'Rue 210, Villa Mandingue'),
            ('ibrahim.kante@example.com', 'Ibrahim', 'Kante', '+223 79 01 23 45', 'Bamako', 'Yirimadio', 'Zone Residentielle Stade du 26 Mars'),
            ('rokia.sidibe@example.com', 'Rokia', 'Sidibe', '+223 71 66 77 88', 'Bamako', 'Hamdallaye', 'Rue 14, Porte 09'),
            ('seydou.dembele@example.com', 'Seydou', 'Dembele', '+223 65 33 22 11', 'Bamako', 'Torokorobougou', 'Quartier Fleuve, Porte 112'),
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
        self.stdout.write(self.style.SUCCESS('Clients de demonstration bamakois crees.'))

        # 4. Artisans bamakois
        artisans_data = [
            (
                'seydou.coulibaly@example.com', 'Seydou', 'Coulibaly', '+223 76 54 32 10',
                'Menuiserie',
                'Maitre menuisier repute a Bamako avec 14 annees d experience. Specialiste du mobilier en bois massif d iroko et teck, cuisines modernes equipees, portes sculptees et parquets.',
                14, 'Bamako', 'Faladie SEMA', 'Rue 812, Cour des ebenistes', 35000,
                'artisans/portrait_seydou.jpg',
            ),
            (
                'mamadou.traore@example.com', 'Mamadou', 'Traore', '+223 66 78 90 12',
                'Plomberie',
                'Plombier chevronne agree. Depannage d urgence, installation de surpresseurs pour forages, ballons chauffe-eau solaires et renovation complete de canalisations et sanitaires.',
                9, 'Bamako', 'Badalabougou', 'Rue de l Ambassade, Porte 120', 25000,
                'artisans/portrait_mamadou.jpg',
            ),
            (
                'oumar.keita@example.com', 'Oumar', 'Keita', '+223 70 34 56 78',
                'Electricite',
                'Electricien diplome specialise en energie solaire photovoltaique et armoires tertiaires. Installation de convertisseurs hybrides, inverseurs de secours et securisation de circuits.',
                11, 'Bamako', 'Hamdallaye ACI 2000', 'Avenue du Mali, Immeuble Sahel', 30000,
                'artisans/portrait_oumar.jpg',
            ),
            (
                'aminata.diallo@example.com', 'Aminata', 'Diallo', '+223 75 67 89 01',
                'Couture',
                'Styliste-modeliste diplomee. Haute couture bamakaoise, grands boubous brodes fil d or sur basin riche, tailleurs contemporains en bogolan vegetal et tenues d apparat.',
                12, 'Bamako', 'Hippodrome', 'Rue Princesse, Atelier Amina Couture', 40000,
                'artisans/portrait_aminata.jpg',
            ),
            (
                'bakary.diarra@example.com', 'Bakary', 'Diarra', '+223 65 12 34 89',
                'Soudure',
                'Ferronnier d art et constructeur metallique. Fabrication sur mesure de portails blindes coulissants, grilles antivols de securite, escaliers en colimacon et pergolas.',
                15, 'Bamako', 'Niamakoro', 'Voie Express, Cour des Forgerons', 30000,
                'artisans/portrait_bakary.jpg',
            ),
            (
                'adama.kone@example.com', 'Adama', 'Kone', '+223 79 45 12 36',
                'Maconnerie',
                'Maitre macon et chef de chantier en batiment. Construction de clotures armees, dallettes de passage, elevation briques pleines, crepissage lissé et carrelage exterieur.',
                13, 'Bamako', 'Sotuba', 'Bord du fleuve Niger, Rue 402', 25000,
                'artisans/metier_maconnerie.jpg',
            ),
            (
                'souleymane.sidibe@example.com', 'Souleymane', 'Sidibe', '+223 74 33 22 11',
                'Peinture',
                'Artisan peintre decorateur batiment. Peintures interieures lessivables, faux marbre, enduits decoratifs et ravalement de facades residentielles resistant aux pluies du Sahel.',
                8, 'Bamako', 'Daoudabougou', 'Rue 310, pres du marche', 20000,
                'artisans/metier_peinture.jpg',
            ),
            (
                'drissa.dembele@example.com', 'Drissa', 'Dembele', '+223 69 88 77 66',
                'Climatisation',
                'Technicien frigoriste certifie. Pose, diagnostic et depannage de climatiseurs split inverter toutes marques, recharge gaz R410A/R32 et contrats d entretien bureau/maison.',
                7, 'Bamako', 'Korofina Nord', 'Rue 114, Porte 08', 22000,
                'artisans/metier_climatisation.jpg',
            ),
            (
                'cheick.camara@example.com', 'Cheick', 'Camara', '+223 71 55 44 33',
                'Mecanique',
                'Maitre mecanicien automobile specialiste tout-terrain et berlines. Diagnostic electronique multimarque, suspension robuste Sahel, freinage et refection moteur complete.',
                16, 'Bamako', 'Sabalibougou', 'Route de Sikasso, Garage de l Amitie', 25000,
                'artisans/metier_mecanique.jpg',
            ),
            (
                'mariam.kante@example.com', 'Mariam', 'Kante', '+223 78 22 33 44',
                'Coiffure & Esthetique',
                'Coiffeuse professionnelle et visagiste a domicile. Maitrise experte des nattes bamakaoises, tresses royales, coiffures de mariee et soins profonds au karite naturel du Mali.',
                9, 'Bamako', 'Golf Djicoroni', 'Avenue de l Hotel de Ville', 15000,
                'artisans/metier_coiffure.jpg',
            ),
        ]

        artisans_map = {}
        for email, fn, ln, tel, metier_nom, desc, exp, ville, quartier, adresse, tarif, photo in artisans_data:
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
                    'photo_profil': photo,
                },
            )
            if photo and not artisan.photo_profil:
                artisan.photo_profil = photo
                artisan.save()
            artisans_map[email] = artisan
        self.stdout.write(self.style.SUCCESS(f'{len(artisans_map)} artisans bamakois crees.'))

        # 5. Realisations
        realisations_data = [
            (
                'seydou.coulibaly@example.com',
                'Table a manger 8 places en teck massif',
                'Plateau de teck sculpte avec 8 chaises coordonnees et finition a la cire d abeille pour une villa a l ACI 2000.',
                'realisations/hero_atelier.jpg',
            ),
            (
                'seydou.coulibaly@example.com',
                'Dressing complet sur mesure avec eclairage LED',
                'Amenagement integral d une chambre parentale avec penderies modulaires, portes coulissantes a persiennes.',
                None,
            ),
            (
                'mamadou.traore@example.com',
                'Installation surpresseur et cuve d eau 2000L',
                'Pose d une pompe automatique avec filtre clarificateur et inverseur reseau pour securiser l approvisionnement.',
                'realisations/metier_plomberie.jpg',
            ),
            (
                'mamadou.traore@example.com',
                'Renovation complete plomberie villa duplex',
                'Tuyauterie PPR haute pression, colonnes de douche thermostatiques et pose d un chauffe-eau solaire.',
                'realisations/metier_plomberie.jpg',
            ),
            (
                'oumar.keita@example.com',
                'Kit solaire autonome 5kVA avec batteries lithium',
                '12 panneaux solaires monocristallins, onduleur hybride haute frequence et bascule automatique anti-coupure.',
                'realisations/metier_electricite.jpg',
            ),
            (
                'aminata.diallo@example.com',
                'Grand boubou de fete en basin riche brode',
                'Broderie fine au fil d or realisee a la main sur basin getzner teinte indigo pour une ceremonie de mariage.',
                'realisations/metier_couture.jpg',
            ),
            (
                'bakary.diarra@example.com',
                'Portail coulissant blinde avec motifs mandingues',
                'Structure en tubes d acier traite anticorrosion et thermolaque noir mat pour entree principale de residence.',
                'realisations/metier_soudure.jpg',
            ),
            (
                'adama.kone@example.com',
                'Cloture d enceinte 45m avec piliers en beton arme',
                'Elevation en parpaings vibres de 15, chainage haut solide et crepissage soigne resistante aux fortes chaleurs.',
                'realisations/metier_maconnerie.jpg',
            ),
            (
                'souleymane.sidibe@example.com',
                'Ravalement facade et peinture satin salon',
                'Application d une peinture siloxane protectrice anti-poussiere et finition satin veloute dans le sejour.',
                'realisations/metier_peinture.jpg',
            ),
            (
                'drissa.dembele@example.com',
                'Installation de 3 climatiseurs split inverter 12000 BTU',
                'Fixations antivibratiles, tirage au vide soigné et goulottes decoratives pour bureaux d entreprise a l ACI 2000.',
                'realisations/metier_climatisation.jpg',
            ),
            (
                'cheick.camara@example.com',
                'Refection suspension et transmission 4x4',
                'Changement amortisseurs renforcés, biellettes, rotules de direction et vidange complete des ponts.',
                'realisations/metier_mecanique.jpg',
            ),
            (
                'mariam.kante@example.com',
                'Parure de coiffure traditionnelle pour mariage civil',
                'Nattes elaborees et tresses royales avec ornements en perles d ambre et soins nourrissants au karite.',
                'realisations/metier_coiffure.jpg',
            ),
        ]

        for email, titre, desc, img in realisations_data:
            artisan = artisans_map.get(email)
            if artisan:
                real, _ = Realisation.objects.get_or_create(
                    artisan=artisan,
                    titre=titre,
                    defaults={'description': desc, 'image': img},
                )
                if img and not real.image:
                    real.image = img
                    real.save()
        self.stdout.write(self.style.SUCCESS('Realisations bamakaoises avec photos creees.'))

        # 6. Demandes de service
        demande1, _ = DemandeService.objects.get_or_create(
            titre='Fuite sous l evier et baisse de pression du surpresseur',
            defaults={
                'client': clients_map['fatoumata.diallo@example.com'],
                'metier': metiers_map['Plomberie'],
                'description': 'Ecoulement permanent sous le meuble d evier et bruit anormal au niveau de la pompe du surpresseur dans la cour.',
                'ville': 'Bamako',
                'quartier': 'Badalabougou',
                'adresse': 'Rue 105, Porte 24',
                'budget_indicatif': 40000,
                'date_souhaitee': date.today() + timedelta(days=2),
                'statut': 'ACCEPTEE',
            },
        )

        demande2, _ = DemandeService.objects.get_or_create(
            titre='Fabrication d une bibliotheque sur-mesure en bois d iroko',
            defaults={
                'client': clients_map['modibo.coulibaly@example.com'],
                'metier': metiers_map['Menuiserie'],
                'description': 'Grande bibliotheque murale en bois d iroko traite, longueur 3m20 par 2m40 de haut avec compartiments de lecture et rangements bas.',
                'ville': 'Bamako',
                'quartier': 'Hamdallaye ACI 2000',
                'adresse': 'Boulevard 22 Octobre, Residence Albaraka',
                'budget_indicatif': 250000,
                'date_souhaitee': date.today() + timedelta(days=12),
                'statut': 'EN_ATTENTE',
            },
        )

        demande3, _ = DemandeService.objects.get_or_create(
            titre='Installation panneau solaire secours coupures d electricite',
            defaults={
                'client': clients_map['kadidia.traore@example.com'],
                'metier': metiers_map['Electricite'],
                'description': 'Besoin d un onduleur solaire hybride de 3kVA avec batterie pour maintenir ventilateurs, eclairage et refrigerateur pendant les delestages.',
                'ville': 'Bamako',
                'quartier': 'Hippodrome',
                'adresse': 'Rue Princesse',
                'budget_indicatif': 350000,
                'date_souhaitee': date.today() + timedelta(days=7),
                'statut': 'ACCEPTEE',
            },
        )

        demande4, _ = DemandeService.objects.get_or_create(
            titre='Confection d une tenue d apparat pour fete de Tabaski',
            defaults={
                'client': clients_map['amadou.sanogo@example.com'],
                'metier': metiers_map['Couture'],
                'description': 'Confection d un complet 3 pieces en basin riche vert emeraude avec broderies artisanales au col et manches.',
                'ville': 'Bamako',
                'quartier': 'Faladie SEMA',
                'adresse': 'Rue 812, Porte 18',
                'budget_indicatif': 60000,
                'date_souhaitee': date.today() + timedelta(days=15),
                'statut': 'ACCEPTEE',
            },
        )

        demande5, _ = DemandeService.objects.get_or_create(
            titre='Fabrication et pose de portail coulissant blinde et antivols',
            defaults={
                'client': clients_map['ousmane.diarra@example.com'],
                'metier': metiers_map['Soudure'],
                'description': 'Conception d un portail metallique coulissant de 4m sur 2m20 avec decor mandingue et 6 grilles antivols pour fenetres.',
                'ville': 'Bamako',
                'quartier': 'Lafiabougou',
                'adresse': 'Rue 340, pres de l Ecole Maternelle',
                'budget_indicatif': 320000,
                'date_souhaitee': date.today() + timedelta(days=10),
                'statut': 'ACCEPTEE',
            },
        )

        demande6, _ = DemandeService.objects.get_or_create(
            titre='Installation onduleur solaire hybride et inverseur de source',
            defaults={
                'client': clients_map['fanta.keita@example.com'],
                'metier': metiers_map['Electricite'],
                'description': 'Alimentation electrique de secours avec inverseur automatique pour maintenir ventilateurs et congelateur lors des coupures.',
                'ville': 'Bamako',
                'quartier': 'Korofina Nord',
                'adresse': 'Rue 118, Porte 33',
                'budget_indicatif': 280000,
                'date_souhaitee': date.today() + timedelta(days=5),
                'statut': 'ACCEPTEE',
            },
        )

        demande7, _ = DemandeService.objects.get_or_create(
            titre='Pose de 2 climatiseurs split inverter 18000 BTU',
            defaults={
                'client': clients_map['mariam.toure@example.com'],
                'metier': metiers_map['Climatisation'],
                'description': 'Installation soignee de deux splits basse consommation dans le sejour et la chambre parentale.',
                'ville': 'Bamako',
                'quartier': 'Dravela',
                'adresse': 'Avenue du 20 Janvier, Porte 45',
                'budget_indicatif': 65000,
                'date_souhaitee': date.today() + timedelta(days=4),
                'statut': 'ACCEPTEE',
            },
        )

        demande8, _ = DemandeService.objects.get_or_create(
            titre='Surelevation mur de cloture et dallettes exterieures',
            defaults={
                'client': clients_map['seydou.dembele@example.com'],
                'metier': metiers_map['Maconnerie'],
                'description': 'Elevation de 3 rangees de parpaings vibres sur 35m avec chainage arme, crepissage ciment et dallage de cour.',
                'ville': 'Bamako',
                'quartier': 'Torokorobougou',
                'adresse': 'Quartier Fleuve, Porte 112',
                'budget_indicatif': 160000,
                'date_souhaitee': date.today() + timedelta(days=8),
                'statut': 'ACCEPTEE',
            },
        )

        demande9, _ = DemandeService.objects.get_or_create(
            titre='Ravalement facade et peinture satin lessivable interieure',
            defaults={
                'client': clients_map['aissata.samake@example.com'],
                'metier': metiers_map['Peinture'],
                'description': 'Application peinture thermo-resistante sur facade et peinture satin lavable ivoire pour salon et couloir.',
                'ville': 'Bamako',
                'quartier': 'Daoudabougou',
                'adresse': 'Rue 210, Villa Mandingue',
                'budget_indicatif': 110000,
                'date_souhaitee': date.today() + timedelta(days=6),
                'statut': 'ACCEPTEE',
            },
        )

        demande10, _ = DemandeService.objects.get_or_create(
            titre='Revision train avant, amortisseurs et freinage 4x4',
            defaults={
                'client': clients_map['ibrahim.kante@example.com'],
                'metier': metiers_map['Mecanique'],
                'description': 'Changement complet des amortisseurs renforcés, rotules de direction et purge du liquide de frein.',
                'ville': 'Bamako',
                'quartier': 'Yirimadio',
                'adresse': 'Zone Residentielle Stade du 26 Mars',
                'budget_indicatif': 85000,
                'date_souhaitee': date.today() + timedelta(days=3),
                'statut': 'ACCEPTEE',
            },
        )

        demande11, _ = DemandeService.objects.get_or_create(
            titre='Nattes traditionnelles d apparat et soins capillaires au karite',
            defaults={
                'client': clients_map['rokia.sidibe@example.com'],
                'metier': metiers_map['Coiffure & Esthetique'],
                'description': 'Coiffure de mariee mandingue ornee de perles et bain d huiles chaudes de karite a domicile.',
                'ville': 'Bamako',
                'quartier': 'Hamdallaye',
                'adresse': 'Rue 14, Porte 09',
                'budget_indicatif': 25000,
                'date_souhaitee': date.today() + timedelta(days=2),
                'statut': 'ACCEPTEE',
            },
        )

        # 7. Devis
        devis1, _ = Devis.objects.get_or_create(
            demande=demande1,
            artisan=artisans_map['mamadou.traore@example.com'],
            defaults={
                'montant': 35000,
                'description': 'Remplacement de la tuyauterie souple d alimentation, joint d etancheite torique et recalibrage du pressostat surpresseur.',
                'duree_estimee': '3 heures',
                'validite': date.today() + timedelta(days=7),
                'statut': 'ACCEPTE',
            },
        )

        devis2, _ = Devis.objects.get_or_create(
            demande=demande2,
            artisan=artisans_map['seydou.coulibaly@example.com'],
            defaults={
                'montant': 235000,
                'description': 'Fourniture de bois massif d iroko etudie, debitage, poncage fin, assemblage tenon-mortaise et vernis de protection satin.',
                'duree_estimee': '8 jours ouvrables',
                'validite': date.today() + timedelta(days=14),
                'statut': 'EN_ATTENTE',
            },
        )

        devis3, _ = Devis.objects.get_or_create(
            demande=demande3,
            artisan=artisans_map['oumar.keita@example.com'],
            defaults={
                'montant': 320000,
                'description': 'Onduleur hybride 3kVA, 2 panneaux 400W, batterie gel 200Ah, coffret de protection parafoudre et raccordement au tableau.',
                'duree_estimee': '2 jours',
                'validite': date.today() + timedelta(days=10),
                'statut': 'ACCEPTE',
            },
        )

        devis4, _ = Devis.objects.get_or_create(
            demande=demande4,
            artisan=artisans_map['aminata.diallo@example.com'],
            defaults={
                'montant': 55000,
                'description': 'Decoupe stylisee, confection doublée, broderie fil soyeux et boutonniere main. Deux essayages prevus a l atelier.',
                'duree_estimee': '6 jours',
                'validite': date.today() + timedelta(days=10),
                'statut': 'ACCEPTE',
            },
        )

        devis5, _ = Devis.objects.get_or_create(
            demande=demande5,
            artisan=artisans_map['bakary.diarra@example.com'],
            defaults={
                'montant': 310000,
                'description': 'Fabrication en fer plein forge, roulements a billes de precision, serrure de securite 3 points et peinture antirouille thermolaquee.',
                'duree_estimee': '7 jours',
                'validite': date.today() + timedelta(days=15),
                'statut': 'ACCEPTE',
            },
        )

        devis6, _ = Devis.objects.get_or_create(
            demande=demande6,
            artisan=artisans_map['oumar.keita@example.com'],
            defaults={
                'montant': 275000,
                'description': 'Inverseur motorise automatique, protection parafoudre classe II, cablage cuivre haute section et mise a la terre.',
                'duree_estimee': '2 jours',
                'validite': date.today() + timedelta(days=10),
                'statut': 'ACCEPTE',
            },
        )

        devis7, _ = Devis.objects.get_or_create(
            demande=demande7,
            artisan=artisans_map['drissa.dembele@example.com'],
            defaults={
                'montant': 60000,
                'description': 'Pose sur supports amortisseurs, liaison cuivre frigorifique isolee, tirage au vide de 45 minutes et test de pression au mano.',
                'duree_estimee': '1 jour',
                'validite': date.today() + timedelta(days=7),
                'statut': 'ACCEPTE',
            },
        )

        devis8, _ = Devis.objects.get_or_create(
            demande=demande8,
            artisan=artisans_map['adama.kone@example.com'],
            defaults={
                'montant': 150000,
                'description': 'Approvisionnement parpaings vibres 15cm, fer a beton de 8, ciment hydrofuge, main d oeuvre maconnerie et crepissage lisse.',
                'duree_estimee': '5 jours',
                'validite': date.today() + timedelta(days=12),
                'statut': 'ACCEPTE',
            },
        )

        devis9, _ = Devis.objects.get_or_create(
            demande=demande9,
            artisan=artisans_map['souleymane.sidibe@example.com'],
            defaults={
                'montant': 105000,
                'description': 'Rebouchage des micro-fissures, couche d impression primaire, deux couches peinture satin lavable et nettoyage complet apres travaux.',
                'duree_estimee': '3 jours',
                'validite': date.today() + timedelta(days=10),
                'statut': 'ACCEPTE',
            },
        )

        devis10, _ = Devis.objects.get_or_create(
            demande=demande10,
            artisan=artisans_map['cheick.camara@example.com'],
            defaults={
                'montant': 80000,
                'description': 'Remplacement jeu complet amortisseurs a gaz renforcés Sahel, rotules inferieures, purge et essai sur route.',
                'duree_estimee': '1 jour',
                'validite': date.today() + timedelta(days=7),
                'statut': 'ACCEPTE',
            },
        )

        devis11, _ = Devis.objects.get_or_create(
            demande=demande11,
            artisan=artisans_map['mariam.kante@example.com'],
            defaults={
                'montant': 25000,
                'description': 'Confection nattes fines royales ornees de perles fines, gommage et bain nutritif au beurre de karite frais de Segou.',
                'duree_estimee': '4 heures',
                'validite': date.today() + timedelta(days=5),
                'statut': 'ACCEPTE',
            },
        )

        # 8. Commandes
        commande1, _ = Commande.objects.get_or_create(
            devis=devis1,
            defaults={
                'client': clients_map['fatoumata.diallo@example.com'],
                'artisan': artisans_map['mamadou.traore@example.com'],
                'statut': 'CONFIRMEE',
                'date_debut': timezone.now() - timedelta(days=5),
                'date_fin_reelle': timezone.now() - timedelta(days=4),
                'commentaires': 'Intervention rapide et propre. La pression d eau est revenue a la normale.',
            },
        )

        commande3, _ = Commande.objects.get_or_create(
            devis=devis3,
            defaults={
                'client': clients_map['kadidia.traore@example.com'],
                'artisan': artisans_map['oumar.keita@example.com'],
                'statut': 'EN_COURS',
                'date_debut': timezone.now() - timedelta(days=1),
                'commentaires': 'Pose des panneaux sur le toit effectuee, raccordement onduleur en cours.',
            },
        )

        commande4, _ = Commande.objects.get_or_create(
            devis=devis4,
            defaults={
                'client': clients_map['amadou.sanogo@example.com'],
                'artisan': artisans_map['aminata.diallo@example.com'],
                'statut': 'CONFIRMEE',
                'date_debut': timezone.now() - timedelta(days=8),
                'date_fin_reelle': timezone.now() - timedelta(days=2),
                'commentaires': 'Tenue livree a temps, coupe impeccable.',
            },
        )

        commande5, _ = Commande.objects.get_or_create(
            devis=devis5,
            defaults={
                'client': clients_map['ousmane.diarra@example.com'],
                'artisan': artisans_map['bakary.diarra@example.com'],
                'statut': 'CONFIRMEE',
                'date_debut': timezone.now() - timedelta(days=12),
                'date_fin_reelle': timezone.now() - timedelta(days=5),
                'commentaires': 'Portail installe avec succes, securite maximale.',
            },
        )

        commande6, _ = Commande.objects.get_or_create(
            devis=devis6,
            defaults={
                'client': clients_map['fanta.keita@example.com'],
                'artisan': artisans_map['oumar.keita@example.com'],
                'statut': 'CONFIRMEE',
                'date_debut': timezone.now() - timedelta(days=7),
                'date_fin_reelle': timezone.now() - timedelta(days=5),
                'commentaires': 'Inverseur automatique parfaitement operationnel.',
            },
        )

        commande7, _ = Commande.objects.get_or_create(
            devis=devis7,
            defaults={
                'client': clients_map['mariam.toure@example.com'],
                'artisan': artisans_map['drissa.dembele@example.com'],
                'statut': 'CONFIRMEE',
                'date_debut': timezone.now() - timedelta(days=6),
                'date_fin_reelle': timezone.now() - timedelta(days=5),
                'commentaires': 'Climatisation tres performante et silencieuse.',
            },
        )

        commande8, _ = Commande.objects.get_or_create(
            devis=devis8,
            defaults={
                'client': clients_map['seydou.dembele@example.com'],
                'artisan': artisans_map['adama.kone@example.com'],
                'statut': 'CONFIRMEE',
                'date_debut': timezone.now() - timedelta(days=10),
                'date_fin_reelle': timezone.now() - timedelta(days=4),
                'commentaires': 'Maconnerie tres solide et propre.',
            },
        )

        commande9, _ = Commande.objects.get_or_create(
            devis=devis9,
            defaults={
                'client': clients_map['aissata.samake@example.com'],
                'artisan': artisans_map['souleymane.sidibe@example.com'],
                'statut': 'CONFIRMEE',
                'date_debut': timezone.now() - timedelta(days=4),
                'date_fin_reelle': timezone.now() - timedelta(days=1),
                'commentaires': 'Peinture eclatante, aucun defaut.',
            },
        )

        commande10, _ = Commande.objects.get_or_create(
            devis=devis10,
            defaults={
                'client': clients_map['ibrahim.kante@example.com'],
                'artisan': artisans_map['cheick.camara@example.com'],
                'statut': 'CONFIRMEE',
                'date_debut': timezone.now() - timedelta(days=3),
                'date_fin_reelle': timezone.now() - timedelta(days=2),
                'commentaires': 'Vehicule parfaitement teste sur piste.',
            },
        )

        commande11, _ = Commande.objects.get_or_create(
            devis=devis11,
            defaults={
                'client': clients_map['rokia.sidibe@example.com'],
                'artisan': artisans_map['mariam.kante@example.com'],
                'statut': 'CONFIRMEE',
                'date_debut': timezone.now() - timedelta(days=2),
                'date_fin_reelle': timezone.now() - timedelta(days=1),
                'commentaires': 'Coiffure de fete admiree de tous.',
            },
        )

        # 9. Avis
        Avis.objects.get_or_create(
            commande=commande1,
            defaults={
                'client': clients_map['fatoumata.diallo@example.com'],
                'artisan': artisans_map['mamadou.traore@example.com'],
                'note': 5,
                'commentaire': 'Mamadou est un plombier extremement rigoureux. Il a regle la panne en moins de deux heures avec le sourire et professionnalisme. Je recommande chaleureusement a Badalabougou !',
            },
        )

        Avis.objects.get_or_create(
            commande=commande4,
            defaults={
                'client': clients_map['amadou.sanogo@example.com'],
                'artisan': artisans_map['aminata.diallo@example.com'],
                'note': 5,
                'commentaire': 'Aminata a un don remarquable pour la couture. Les finitions du basin et les broderies sont du niveau haute couture. Tout le monde a complimente la tenue lors de la fete.',
            },
        )

        Avis.objects.get_or_create(
            commande=commande5,
            defaults={
                'client': clients_map['ousmane.diarra@example.com'],
                'artisan': artisans_map['bakary.diarra@example.com'],
                'note': 5,
                'commentaire': 'Bakary Diarra a realise un chef-d oeuvre de ferronnerie. Notre portail coulissant blinde est solide, silencieux et magnifique. Le travail de soudure est d une finition exemplaire a Lafiabougou.',
            },
        )

        Avis.objects.get_or_create(
            commande=commande6,
            defaults={
                'client': clients_map['fanta.keita@example.com'],
                'artisan': artisans_map['oumar.keita@example.com'],
                'note': 5,
                'commentaire': 'Oumar Keita a resolu nos soucis de coupures a Korofina. L inverseur et le coffret solaire fonctionnent a merveille. Grand sens du devoir et conseils avisés.',
            },
        )

        Avis.objects.get_or_create(
            commande=commande7,
            defaults={
                'client': clients_map['mariam.toure@example.com'],
                'artisan': artisans_map['drissa.dembele@example.com'],
                'note': 5,
                'commentaire': 'Drissa est un vrai professionnel de la climatisation. Installation tres soignee a Dravela, gaines propres et froid instantane dans toute la maison.',
            },
        )

        Avis.objects.get_or_create(
            commande=commande8,
            defaults={
                'client': clients_map['seydou.dembele@example.com'],
                'artisan': artisans_map['adama.kone@example.com'],
                'note': 5,
                'commentaire': 'Adama Kone est un maitre macon de confiance. Cloture terminee a Torokorobougou avec une solidite remarquable et un respect scrupuleux du devis.',
            },
        )

        Avis.objects.get_or_create(
            commande=commande9,
            defaults={
                'client': clients_map['aissata.samake@example.com'],
                'artisan': artisans_map['souleymane.sidibe@example.com'],
                'note': 5,
                'commentaire': 'Souleymane Sidibe a transforme nos murs a Daoudabougou. La peinture satin est veloutee, lessivable et les lignes sont nettes. Travail d artiste !',
            },
        )

        Avis.objects.get_or_create(
            commande=commande10,
            defaults={
                'client': clients_map['ibrahim.kante@example.com'],
                'artisan': artisans_map['cheick.camara@example.com'],
                'note': 5,
                'commentaire': 'Cheick Camara est le meilleur mecanicien 4x4 de Bamako. Diagnostic precis, amortisseurs montes aux normes et vehicule pret a affronter toutes les pistes.',
            },
        )

        Avis.objects.get_or_create(
            commande=commande11,
            defaults={
                'client': clients_map['rokia.sidibe@example.com'],
                'artisan': artisans_map['mariam.kante@example.com'],
                'note': 5,
                'commentaire': 'Mariam Kante est d une douceur et d un talent remarquables. Mes nattes pour le bapteme a Hamdallaye etaient sublimes. Soin capillaire au karite parfait.',
            },
        )

        # Avis supplementaire pour Seydou Coulibaly (Menuiserie) via une ancienne commande
        demande_seydou_old, _ = DemandeService.objects.get_or_create(
            titre='Table en teck 8 places pour salle a manger',
            defaults={
                'client': clients_map['fatoumata.diallo@example.com'],
                'metier': metiers_map['Menuiserie'],
                'description': 'Commande de table de reception en bois de teck.',
                'ville': 'Bamako',
                'quartier': 'Badalabougou',
                'statut': 'ACCEPTEE',
            },
        )
        devis_seydou_old, _ = Devis.objects.get_or_create(
            demande=demande_seydou_old,
            artisan=artisans_map['seydou.coulibaly@example.com'],
            defaults={
                'montant': 180000,
                'description': 'Confection artisanale de table en bois massif de teck.',
                'statut': 'ACCEPTE',
            },
        )
        cmd_seydou_old, _ = Commande.objects.get_or_create(
            devis=devis_seydou_old,
            defaults={
                'client': clients_map['fatoumata.diallo@example.com'],
                'artisan': artisans_map['seydou.coulibaly@example.com'],
                'statut': 'CONFIRMEE',
            },
        )
        Avis.objects.get_or_create(
            commande=cmd_seydou_old,
            defaults={
                'client': clients_map['fatoumata.diallo@example.com'],
                'artisan': artisans_map['seydou.coulibaly@example.com'],
                'note': 5,
                'commentaire': 'Seydou est le meilleur ebeniste de Bamako. La table en teck trone magnifiquement dans notre salon. Le bois est splendide et la finition exemplaire.',
            },
        )

        self.stdout.write(self.style.SUCCESS('Base de donnees initialisee avec succes pour le Mali (Bamako) !'))
        self.stdout.write(self.style.NOTICE("""
Comptes de test disponibles :
- Administrateur   : admin@artisanconnect.ml / Admin1234!
- Clients (mot de passe unique : Client1234!) :
  * Fatoumata Diallo    : fatoumata.diallo@example.com (Badalabougou, Commune V)
  * Modibo Coulibaly    : modibo.coulibaly@example.com (Hamdallaye ACI 2000, Commune IV)
  * Kadidia Traore      : kadidia.traore@example.com (Hippodrome, Commune II)
  * Amadou Sanogo       : amadou.sanogo@example.com (Faladie SEMA, Commune VI)
  * Fanta Keita         : fanta.keita@example.com (Korofina Nord, Commune I)
  * Bakary Traore       : bakary.traore@example.com (Bagadadji, Commune II)
  * Mariam Toure        : mariam.toure@example.com (Dravela, Commune III)
  * Ousmane Diarra      : ousmane.diarra@example.com (Lafiabougou, Commune IV)
  * Aissata Samake      : aissata.samake@example.com (Daoudabougou, Commune V)
  * Ibrahim Kante       : ibrahim.kante@example.com (Yirimadio, Commune VI)
  * Rokia Sidibe        : rokia.sidibe@example.com (Hamdallaye, Commune IV)
  * Seydou Dembele      : seydou.dembele@example.com (Torokorobougou, Commune V)
- Artisans (mot de passe unique : Artisan1234!) :
  * Menuiserie          : seydou.coulibaly@example.com (Faladie SEMA)
  * Plomberie           : mamadou.traore@example.com (Badalabougou)
  * Electricite         : oumar.keita@example.com (ACI 2000)
  * Couture             : aminata.diallo@example.com (Hippodrome)
  * Soudure             : bakary.diarra@example.com (Niamakoro)
  * Maconnerie          : adama.kone@example.com (Sotuba)
  * Peinture            : souleymane.sidibe@example.com (Daoudabougou)
  * Climatisation       : drissa.dembele@example.com (Korofina Nord)
  * Mecanique           : cheick.camara@example.com (Sabalibougou)
  * Coiffure/Esthetique : mariam.kante@example.com (Golf Djicoroni)
"""))
