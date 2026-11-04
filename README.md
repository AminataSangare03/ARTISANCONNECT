# ArtisanConnect

Plateforme web complete (Full Python / Django) et API REST destinee a la mise en relation entre particuliers/entreprises et artisans professionnels qualifies.

Devise : **Le savoir-faire a portee de main**

---

## 1. Contexte et Problematique

Dans le domaine des services et de l'entrepreneuriat, les particuliers et les entreprises eprouvent souvent des difficultes a identifier un artisan disponible, competent et situe a proximite.

**ArtisanConnect** apporte une reponse structuree et numerique en permettant :
- De creer et gerer des profils d'artisans avec leurs metiers (couture, menuiserie, plomberie, soudure, electricite, maconnerie, peinture, etc.).
- De presenter les realisations des artisans avec photos a l'appui (portfolio).
- De rechercher un artisan par metier et par localisation (ville, quartier).
- De permettre a un client de publier une demande de service detaillee.
- De permettre a l'artisan d'y repondre par un devis chiffre et personnalise.
- De suivre les commandes du lancement a l'achevement.
- De recueillir des avis et notes verifies apres chaque prestation confirmee.

---

## 2. Architecture Technique

Le projet est concu en **Full Python** avec Django, proposant une double interface :
1. **Application Web responsive (Templates Django)** : navigation complete, recherche multicritere, fiches artisans avec portfolio, publication de demandes, tableau de bord client et tableau de bord artisan, gestion des devis et recueil des avis.
2. **API REST complete (Django REST Framework)** : endpoints securises par JWT pour integrations mobiles ou front-ends decouples, avec documentation interactive Swagger et ReDoc.

### Organisation modulaire (apps) :
- `apps.accounts` : gestion des utilisateurs personnalises (User sans username, avec email unique), profils Clients et gestion des droits.
- `apps.metiers` : catalogue des corps de metiers actifs.
- `apps.artisans` : profils d'artisans, disponibilite, tarifs indicatifs et portfolio de realisations photos.
- `apps.demandes` : publication et suivi des demandes de service par les clients.
- `apps.devis` : emission de devis par les artisans, acceptation ou refus par les clients.
- `apps.commandes` : gestion du cycle de vie des commandes (En attente, En cours, Terminee, Confirmee, Annulee).
- `apps.avis` : notation de 1 a 5 et commentaires apres confirmation de la prestation.
- `apps.web` : vues web Django, formulaires, templates et session authentication.

---

## 3. Logique des Donnees & Modeles

| Modele / Table | Informations et relations cles |
|---|---|
| **Utilisateur (User)** | Email (identifiant unique), nom, prenom, telephone, photo de profil, role (CLIENT, ARTISAN, ADMIN). |
| **Client** | Utilisateur (OneToOne), ville, quartier, adresse. |
| **Metier** | Nom unique, description, statut actif. |
| **Artisan** | Utilisateur (OneToOne), metier (ForeignKey), description, experience (annees), zone (ville, quartier, adresse), disponibilite, tarif indicatif, telephone pro. |
| **Realisation** | Artisan (ForeignKey), titre, description, image, date de realisation. |
| **DemandeService** | Client (ForeignKey), metier (ForeignKey), titre, description, localisation, budget indicatif, date souhaitee, statut. |
| **Devis** | Demande (ForeignKey), artisan (ForeignKey), montant (FCFA), duree estimee, validite, description, statut. |
| **Commande** | Devis accepte (OneToOne), client, artisan, dates (debut, fin prevue, fin reelle), statut (EN_ATTENTE, EN_COURS, TERMINEE, CONFIRMEE, ANNULEE). |
| **Avis** | Commande (OneToOne), client, artisan, note (1 a 5), commentaire. |

---

## 4. Prise en Main Rapide

### 4.1. Pre-requis
- Python 3.12+
- Git

### 4.2. Installation locale
Dans le repertoire du projet :

```powershell
# 1. Creer l'environnement virtuel
python -m venv .venv

# 2. Activer l'environnement virtuel
.\.venv\Scripts\Activate.ps1

# 3. Installer les dependances
pip install -r requirements.txt

# 4. Appliquer les migrations
python manage.py migrate

# 5. Peupler la base avec des donnees de demonstration realistes
python manage.py seed_data

# 6. Lancer le serveur de developpement
python manage.py runserver
```

L'application web est alors accessible sur : **http://127.0.0.1:8000/**

---

## 5. Comptes de Test & Demonstration

Apres avoir execute `python manage.py seed_data`, les comptes suivants sont immediatement operationnels :

| Profil | Identifiant (Email) | Mot de passe | Description |
|---|---|---|---|
| **Administrateur** | `admin@artisanconnect.ci` | `Admin1234!` | Acces complet au panneau d'administration (`/admin/`) |
| **Client 1** | `fatou.kone@example.com` | `Client1234!` | Client a Cocody avec demandes et commandes |
| **Client 2** | `jean.kouassi@example.com` | `Client1234!` | Client au Plateau avec demande de menuiserie |
| **Artisan Plombier** | `ibrahim.diop@example.com` | `Artisan1234!` | 8 ans d'exp., realisations & avis positifs |
| **Artisan Menuisier** | `moussa.traore@example.com` | `Artisan1234!` | 12 ans d'exp., specialiste bois massif |
| **Artisan Couturiere** | `aminata.toure@example.com` | `Artisan1234!` | 10 ans d'exp., styliste modeliste |

---

## 6. Endpoints & Documentation API

- **Documentation Swagger OpenAPI** : `http://127.0.0.1:8000/api/docs/`
- **Documentation ReDoc** : `http://127.0.0.1:8000/api/redoc/`
- **Schema OpenAPI Brut (JSON/YAML)** : `http://127.0.0.1:8000/api/schema/`

### Principaux points d'entree REST (v1) :
- `POST /api/v1/accounts/register/` : inscription de compte client ou artisan.
- `POST /api/v1/accounts/login/` : obtention de tokens JWT (access & refresh).
- `GET /api/v1/artisans/` : liste et recherche multicritere d'artisans.
- `GET /api/v1/artisans/<id>/` : detail d'un artisan avec realisations et notation moyenne.
- `GET /api/v1/artisans/<id>/avis/` : avis recus par un artisan.
- `GET /api/v1/artisans/<id>/note/` : note moyenne calculee d'un artisan.
- `GET /api/v1/demandes/` : consultation des demandes de service.
- `GET /api/v1/demandes/mes-demandes/` : demandes filtrees pour l'utilisateur connecte.
- `POST /api/v1/devis/` : emission d'un devis par un artisan du metier concerne.
- `POST /api/v1/devis/<id>/accepter/` : acceptation du devis par le client et creation automatique de la commande.
- `POST /api/v1/commandes/<id>/demarrer/` : passage de la commande au statut 'EN_COURS'.
- `POST /api/v1/commandes/<id>/terminer/` : declaration de fin de chantier par l'artisan.
- `POST /api/v1/commandes/<id>/confirmer/` : confirmation de livraison par le client.
- `POST /api/v1/avis/` : publication d'une note (1-5) et commentaire pour une commande confirmee.

---

## 7. Tests & Verification Qualite

L'ensemble des fonctionnalites (metiers, artisans, demandes, devis, commandes, avis et interface web) est valide par 24 tests automatises :

```powershell
python manage.py test
```

Tous les tests s'executent avec succes sans aucun avertissement.
