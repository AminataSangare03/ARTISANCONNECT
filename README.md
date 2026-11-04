# ArtisanConnect

Plateforme web complete (Full Python / Django) et API REST destinee a la mise en relation securisee et certifiee entre particuliers/entreprises et artisans professionnels qualifies a Bamako, Mali.

Devise officielle : **Le savoir-faire a portee de main**

---

## Sommaire

1. [Contexte et Problematique](#1-contexte-et-problematique)
2. [Fonctionnalites Cles](#2-fonctionnalites-cles)
3. [Architecture Technique & Modules](#3-architecture-technique--modules)
4. [Design System & Motion Physics (Apple Fluid Design)](#4-design-system--motion-physics-apple-fluid-design)
5. [Modele de Donnees & Relations](#5-modele-de-donnees--relations)
6. [Prise en Main Rapide & Installation](#6-prise-en-main-rapide--installation)
7. [Comptes de Demonstration & Identifiants](#7-comptes-de-demonstration--identifiants)
8. [API REST & Documentation OpenAPI](#8-api-rest--documentation-openapi)
9. [Securite & Durcissement Technique](#9-securite--durcissement-technique)
10. [Tests Automatises & Verification Qualite](#10-tests-automatises--verification-qualite)
11. [Arborescence du Projet](#11-arborescence-du-projet)

---

## 1. Contexte et Problematique

Dans les centres urbains en forte expansion comme Bamako, les particuliers et les entreprises font face a une problematique recurrente : la difficulte a identifier rapidement un artisan de proximite a la fois competent, fiable, disponible et proposant des tarifs transparents.

**ArtisanConnect** apporte une reponse numerique structuree fondee sur l authenticite et la mise en confiance :
- Annuaire bamakois geolocalise couvrant l ensemble des 6 communes du district de Bamako.
- Portfolios authentiques de realisations avec photographies reelles des travaux.
- Devis formels et chiffres en Francs CFA (XOF) emis avant tout debut de chantier.
- Suivi rigoureux du cycle de vie des commandes de la reservation jusqu a la livraison.
- Recueil obligatoire d avis authentifies apres reception des travaux pour valoriser l excellence artisanale.

---

## 2. Fonctionnalites Cles

### Pour les Clients (Particuliers & Entreprises) :
- **Recherche multicritere** : filtrage instantane par corps de metier, par quartier (ACI 2000, Badalabougou, Hippodrome, Faladie, Sotuba, Korofina, etc.) et disponibilite.
- **Consultation de profils detailles** : fiches d artisans incluant biographie, annees d experience, tarif horaire ou forfaitaire indicatif en FCFA, galerie photos et notation moyenne.
- **Publication de demandes de service** : expression detaillee du besoin, date souhaitee d intervention, quartier specifique et budget indicatif.
- **Comparaison des devis** : reception de propositions detaillees et contractualisation en un clic.
- **Espace Client (Dashboard)** : suivi en temps reel des demandes en cours, devis recus, commandes actives et historique des prestations.
- **Evaluation certifiee** : attribution d une note (1 a 5 etoiles) et d un retour d experience detaille des la cloture du chantier.

### Pour les Artisans Partenaires :
- **Profil professionnel valorisant** : presentation complete de leur savoir-faire, specialites et coordonnees professionnelles.
- **Vitrine de realisations (Portfolio)** : televersement et gestion d images de chantiers acheves.
- **Fil d opportunites** : notification et consultation des demandes de service publiees dans leur corps de metier a Bamako.
- **Emission de devis chiffres** : envoi de devis personnalises comprenant montant en FCFA, delai estimatif de livraison et conditions de realisation.
- **Espace Artisan (Dashboard)** : gestion centralisee des devis emis, des chantiers a demarrer et a terminer.
- **Capital reputation** : aggregation automatique de la note moyenne et visibilite accrue pour les meilleurs artisans.

---

## 3. Architecture Technique & Modules

Le projet est developpe en **Full Python** reposant sur une architecture bi-couche robuste :
1. **Application Web responsive (Django Server-Side Rendering)** : templates modulaires, navigation securisee par session, composabilite responsive sans dependance lourde.
2. **API REST complete (Django REST Framework & SimpleJWT)** : points de terminaison proteges pour les applications mobiles ou front-ends decouples.

### Organisation modulaire des applications (`apps/`) :
- `apps.accounts` : gestion des utilisateurs personnalises (sans username, email unique), modeles de profils `Client`, permissions par role (`CLIENT`, `ARTISAN`, `ADMIN`) et flux d authentification JWT/Session.
- `apps.metiers` : catalogue des corps de metiers actifs avec visuels de demonstration et descriptions specialisees.
- `apps.artisans` : profils d artisans, portfolio de realisations photographiques, disponibilite et tarifs indicatifs.
- `apps.demandes` : soumission, filtrage et cycle de vie des demandes de service clients.
- `apps.devis` : emission de devis par les artisans du metier concerne, acceptation ou refus client avec transaction atomique.
- `apps.commandes` : gestion du cycle de vie des commandes (`EN_ATTENTE`, `CONFIRMEE`, `EN_COURS`, `TERMINEE`, `ANNULEE`).
- `apps.avis` : gestion de la notation verified-only apres livraison effective d une commande.
- `apps.web` : controleurs d interface web, gabarits HTML, filtres personnalises (`fcfa`, `stars`, `metier_image`, `artisan_avatar`) et logique de tableau de bord.

---

## 4. Design System & Motion Physics (Apple Fluid Design)

L interface utilisateur respecte rigoureusement les principes ergonomiques d Apple, de Vercel Geist et d Emil Kowalski :

### Moteur de Themes Dual (Clair & Sombre)
- **Synchronisation avec le systeme d exploitation** : detection automatique via `window.matchMedia('(prefers-color-scheme: dark)')` sans scintillement (script anti-FOUT inline), mise a jour en temps reel lors du changement de theme de l OS, et persistance manuelle dans `localStorage`.
- **Mode Sombre (Architecture OLED Obsidian)** :
  - Fond noir profond `#090A0D` et surfaces de cartes foncees `#14151B`.
  - Typographie principale blanc ardoise `#F8FAFC` et gris d appoint `#94A3B8` assurant un ratio de contraste depassant 16:1 (conforme WCAG AAA).
  - Lueur d ambiance terracotta subtile au survol des cartes interactives (`rgba(224, 122, 95, 0.18)`).
- **Mode Clair (Ivoire chaud & contraste Onyx)** :
  - Fond ivoire sable `#F8F6F0` limitant la fatigue visuelle.
  - Textes et titres a tres fort contraste en noir zinc `#111827` et ardoise `#475569`.
  - Champs de formulaire clairs garantissant une visibilite immediate des placeholders sans effet de grisaille.

### Motion Design & Principes Framer Motion
- **Vitrine rotative hero (2,5 secondes)** : carrousel multi-metiers automatique cadense a exactement 2,5 secondes, associe a un effet cinematique Ken Burns doux et a une jauge de progression animee continue sur la puce active.
- **Entrees echelonnees (Staggered Wave)** : observateur `IntersectionObserver` injectant un delai d apparition dynamique sur les cartes (`stagger: 70ms`).
- **Retour haptique tactile** : compression souple a l activation des boutons (`:active { transform: scale(0.96); }`).
- **Bouton retour en haut centre** : bouton circulaire flottant de 48px comprenant uniquement la fleche de navigation, centre horizontalement au bas de l ecran, se revelant a 45% de defilement avec effet d elevation spring.
- **Barre de progression de lecture** : jauge dynamique continue de 0% a 100% au sommet du viewport.
- **Typographie tabulaire** : alignement strict des montants et chiffres cles via `font-variant-numeric: tabular-nums`.

---

## 5. Modele de Donnees & Relations

| Modele | Table / Application | Attributs et relations cles |
|---|---|---|
| **User** | `apps.accounts` | Email (identifiant unique), `first_name`, `last_name`, `phone_number`, `photo_profil`, `role` (`CLIENT`, `ARTISAN`, `ADMIN`), `is_active`. |
| **Client** | `apps.accounts` | `user` (OneToOne), `ville`, `quartier`, `adresse`. |
| **Metier** | `apps.metiers` | `nom` (unique), `description`, `image`, `is_active`. |
| **Artisan** | `apps.artisans` | `user` (OneToOne), `metier` (ForeignKey), `description`, `experience` (annees), `ville`, `quartier`, `adresse`, `disponibilite`, `tarif_indicatif` (FCFA), `telephone_professionnel`. |
| **Realisation** | `apps.artisans` | `artisan` (ForeignKey), `titre`, `description`, `image`, `date_realisation`. |
| **DemandeService** | `apps.demandes` | `client` (ForeignKey), `metier` (ForeignKey), `titre`, `description`, `ville`, `quartier`, `adresse`, `budget_indicatif`, `date_souhaitee`, `statut` (`EN_ATTENTE`, `ACCEPTEE`, `EN_COURS`, `TERMINEE`, `ANNULEE`). |
| **Devis** | `apps.devis` | `demande` (ForeignKey), `artisan` (ForeignKey), `montant` (FCFA), `duree_estimee`, `date_validite`, `description`, `statut` (`EN_ATTENTE`, `ACCEPTE`, `REFUSE`, `EXPIRE`). |
| **Commande** | `apps.commandes` | `devis` (OneToOne), `client`, `artisan`, `date_debut`, `date_fin_prevue`, `date_fin_reelle`, `statut` (`EN_ATTENTE`, `CONFIRMEE`, `EN_COURS`, `TERMINEE`, `ANNULEE`). |
| **Avis** | `apps.avis` | `commande` (OneToOne), `client`, `artisan`, `note` (entier 1 a 5), `commentaire`, `created_at`. |

---

## 6. Prise en Main Rapide & Installation

### Pre-requis
- Python 3.12 ou version superieure
- Git

### Installation en environnement local

```powershell
# 1. Cloner le depot du projet
git clone https://github.com/AminataSangare03/ARTISANCONNECT.git
cd ARTISANCONNECT

# 2. Creer l environnement virtuel
python -m venv .venv

# 3. Activer l environnement virtuel
# Sur Windows (PowerShell) :
.\.venv\Scripts\Activate.ps1
# Sur Linux / macOS :
source .venv/bin/activate

# 4. Installer l ensemble des dependances
pip install -r requirements.txt

# 5. Appliquer les migrations de la base de donnees
python manage.py migrate

# 6. Peupler la base avec les 16 artisans, 12 clients, chantiers et avis certifies bamakois
python manage.py seed_data

# 7. Lancer le serveur de developpement
python manage.py runserver
```

L application web est desormais disponible sur : **http://127.0.0.1:8000/**

---

## 7. Comptes de Demonstration & Identifiants

Tous les comptes ci-dessous sont generes automatiquement par la commande `seed_data` et sont immediatement exploitables pour les tests fonctionnels et les evaluations :

### Administrateur Global
- **Email** : `admin@artisanconnect.ml`
- **Mot de passe** : `Admin1234!`
- **Role** : Acces superviseur complet (`/admin/`) et controle de tous les flux.

### Clients Particuliers (Bamako)
| Nom & Prenom | Email | Mot de passe | Quartier d intervention |
|---|---|---|---|
| Aissata Traore | `aissata.traore@example.com` | `Client1234!` | Hamdallaye ACI 2000 (Commune IV) |
| Ibrahim Maiga | `ibrahim.maiga@example.com` | `Client1234!` | Badalabougou (Commune V) |
| Fatoumata Diallo | `fatoumata.diallo@example.com` | `Client1234!` | Hippodrome (Commune II) |
| Modibo Coulibaly | `modibo.coulibaly@example.com` | `Client1234!` | Faladie SEMA (Commune VI) |
| Mariam Sidibe | `mariam.sidibe@example.com` | `Client1234!` | Korofina Nord (Commune I) |
| Ousmane Diakite | `ousmane.diakite@example.com` | `Client1234!` | Niamakoro (Commune VI) |

### Artisans Professionnels Certifies (Bamako)
| Artisan | Metier d excellence | Email | Mot de passe | Quartier & Commune | Tarif indicatif |
|---|---|---|---|---|---|
| Seydou Coulibaly | Menuiserie & Ebenisterie | `seydou.coulibaly@example.com` | `Artisan1234!` | Faladie SEMA | 35 000 FCFA |
| Mamadou Traore | Plomberie & Forages | `mamadou.traore@example.com` | `Artisan1234!` | Badalabougou | 25 000 FCFA |
| Oumar Keita | Electricite & Solaire | `oumar.keita@example.com` | `Artisan1234!` | Hamdallaye ACI 2000 | 30 000 FCFA |
| Aminata Diallo | Couture & Haute Mode | `aminata.diallo@example.com` | `Artisan1234!` | Hippodrome | 40 000 FCFA |
| Bakary Diarra | Soudure & Ferronnerie | `bakary.diarra@example.com` | `Artisan1234!` | Niamakoro | 30 000 FCFA |
| Drissa Dembele | Climatisation Inverter | `drissa.dembele@example.com` | `Artisan1234!` | Korofina Nord | 25 000 FCFA |
| Adama Kone | Maconnerie & Gros oeuvre | `adama.kone@example.com` | `Artisan1234!` | Sotuba | 25 000 FCFA |
| Souleymane Sidibe | Peinture & Enduits | `souleymane.sidibe@example.com` | `Artisan1234!` | Daoudabougou | 20 000 FCFA |

---

## 8. API REST & Documentation OpenAPI

Le backend expose une API REST complete et entierement documentee :

- **Portail interactif Swagger UI** : `http://127.0.0.1:8000/api/docs/`
- **Documentation ReDoc** : `http://127.0.0.1:8000/api/redoc/`
- **Schema OpenAPI Brut (JSON/YAML)** : `http://127.0.0.1:8000/api/schema/`

### Principaux Endpoints REST (v1) :
| Methode | Endpoint | Role autorise | Description |
|---|---|---|---|
| `POST` | `/api/v1/accounts/register/` | Public | Inscription client ou artisan |
| `POST` | `/api/v1/accounts/login/` | Public | Authentification et remise des jetons JWT |
| `POST` | `/api/v1/accounts/token/refresh/` | Authentifie | Rafraichissement du token d acces JWT |
| `GET/PATCH` | `/api/v1/accounts/me/` | Authentifie | Consultation et mise a jour du profil utilisateur |
| `GET` | `/api/v1/artisans/` | Public | Annuaire et recherche d artisans avec filtres |
| `GET` | `/api/v1/artisans/<id>/` | Public | Profil detaille d un artisan, realisations et avis |
| `GET` | `/api/v1/artisans/<id>/note/` | Public | Note moyenne calculee et volume total d avis |
| `GET/POST` | `/api/v1/demandes/` | Client / Artisan | Consultation ou publication d une demande de service |
| `GET` | `/api/v1/demandes/mes-demandes/` | Authentifie | Demandes rattachees au compte connecte |
| `POST` | `/api/v1/devis/` | Artisan | Emission d un devis pour une demande ciblée |
| `POST` | `/api/v1/devis/<id>/accepter/` | Client | Acceptation du devis et creation atomique de la commande |
| `POST` | `/api/v1/devis/<id>/refuser/` | Client | Rejet formel du devis propose |
| `POST` | `/api/v1/commandes/<id>/demarrer/`| Artisan | Passage de la commande au statut 'EN_COURS' |
| `POST` | `/api/v1/commandes/<id>/terminer/`| Artisan | Declaration d achevement des travaux |
| `POST` | `/api/v1/commandes/<id>/confirmer/`| Client | Reception conforme des travaux |
| `POST` | `/api/v1/avis/` | Client | Depot d un avis verified pour une commande confirmee |

---

## 9. Securite & Durcissement Technique

Le projet integre les recommandations du guide officiel de durcissement Django :
- **Protection des sessions et cookies** : `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = 'Lax'`, `CSRF_COOKIE_SAMESITE = 'Lax'`.
- **En-tetes de protection** : `SECURE_CONTENT_TYPE_NOSNIFF = True` et `X_FRAME_OPTIONS = 'DENY'` pour contrer le clickjacking et l interception MIME.
- **Parametres de production pre-configures** : activation conditionnelle de `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_BROWSER_XSS_FILTER` et `SECURE_HSTS_SECONDS` (31536000s) lorsque `DEBUG=False`.
- **Controle des permissions strict** : filtrage granulaire dans les vues DRF (`get_queryset`) interdisant a un utilisateur d acceder ou d agir sur des ressources privees d un tiers.
- **Transactions atomiques** : l acceptation d un devis, l invalidation des devis concurrents et la creation de la commande s executent dans un bloc atomique transactionnel pour prevenir toute incoherence en base.

---

## 10. Tests Automatises & Verification Qualite

L ensemble des regles metier, flux de commandes, autorisations d acces et interfaces web est couvert par **24 tests unitaires et d integration automatises** :

```powershell
# Execution de la suite de tests
python manage.py test
```

Resultat d execution :
```text
Ran 24 tests in 21.733s
OK
```

Toutes les verifications passent avec succes (0 echec, 0 regression, 0 avertissement bloquant).

---

## 11. Arborescence du Projet

```text
ARTISANCONNECT/
├── manage.py
├── requirements.txt
├── README.md
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/          # Authentification, Utilisateurs & Profils Clients
│   ├── metiers/           # Catalogue des corps de metiers
│   ├── artisans/          # Fiches artisans & Realisations photos
│   ├── demandes/          # Demandes de services publiees
│   ├── devis/             # Moteur d emission et validation de devis
│   ├── commandes/         # Cycle de vie et suivi des chantiers
│   ├── avis/              # Evaluations et notes certifiees
│   └── web/               # Controleurs Web, formulaires et filtres de gabarit
├── templates/
│   ├── base.html          # Gabarit socle, theme dual, navigation et animations
│   ├── home.html          # Accueil, vitrine hero 2.5s, chiffres et parcours
│   ├── login.html         # Connexion securisee
│   ├── register.html      # Inscription par role (Client / Artisan)
│   ├── client_dashboard.html
│   ├── artisan_dashboard.html
│   ├── artisan_list.html
│   ├── artisan_detail.html
│   ├── demande_list.html
│   ├── demande_detail.html
│   └── demande_create.html
└── static/
    ├── css/
    ├── js/
    └── images/
        ├── logo.png
        ├── logo_icon.png
        └── generated/     # Visuels metiers & portraits haute definition
```

---

## Licence & Droits

Tous droits reserves &copy; 2026 ArtisanConnect Mali. Concu et developpe conformement aux standards professionnels d architecture logicielle et d ingenierie full-stack Python.
