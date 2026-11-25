# Projet fil rouge DevOps

Application web permettant à un utilisateur de **créer un compte**, de **se connecter** et de **modifier son profil**.
Elle s'exécute entièrement avec **Docker Compose** : aucune dépendance (Python, PostgreSQL, Nginx) n'est à installer sur la machine.

## Architecture

|Service|Technologie|Rôle|
|-|-|-|
|`frontend`|HTML / CSS / JavaScript servis par Nginx|Interface web, accessible depuis le navigateur. Transmet les appels `/api/` au backend|
|`backend`|Python 3.12, Flask, Gunicorn|API REST : inscription, connexion (jeton signé), lecture et modification du profil|
|`db`|PostgreSQL 16|Stockage des utilisateurs, avec un volume Docker pour la persistance|

```
Navigateur --> frontend (Nginx, port 8080) --> backend (Flask, port 5000) --> db (PostgreSQL, port 5432)
```

Les trois services sont sur le réseau Docker `reseau\_app`. Seul le frontend est publié sur la machine hôte ; le backend et la base ne sont joignables que depuis ce réseau.

## Prérequis

* **Docker** avec **Docker Compose v2** (inclus dans Docker Desktop). Vérification : `docker --version` et `docker compose version`.
* **Git** pour cloner le dépôt.
* Le port **8080** doit être libre (modifiable avec `FRONTEND\_PORT`, voir plus bas).

## Récupération et configuration

```bash
git clone https://github.com/<utilisateur>/projet\_fil\_rouge\_devops.git
cd projet\_fil\_rouge\_devops
cp .env.example .env
```

Ouvrir ensuite le fichier `.env` et remplacer les valeurs `changeme` par de vraies valeurs.
Le fichier `.env` contient des secrets : il est ignoré par Git (`.gitignore`) et ne doit jamais être publié.

### Variables d'environnement

|Variable|Rôle|Valeur par défaut dans `.env.example`|
|-|-|-|
|`DB\_NAME`|Nom de la base PostgreSQL|`appdb`|
|`DB\_USER`|Utilisateur de la base|`appuser`|
|`DB\_PASSWORD`|Mot de passe de la base (**obligatoire**)|`changeme`|
|`SECRET\_KEY`|Clé servant à signer les jetons de connexion (**obligatoire**)|`changeme-cle-secrete`|
|`FRONTEND\_PORT`|Port du frontend sur la machine|`8080`|

Pour générer une clé secrète aléatoire : `openssl rand -hex 32`.
Si `DB\_PASSWORD` ou `SECRET\_KEY` est absent, `docker compose` s'arrête avec un message d'erreur explicite.

## Lancement et arrêt

```bash
# Construire les images et démarrer les trois services
docker compose up --build

# (ou en arrière-plan)
docker compose up --build -d

# Voir l'état des services et les journaux
docker compose ps
docker compose logs -f

# Arrêter et supprimer les conteneurs (les données de la base sont conservées)
docker compose down

# Arrêter ET supprimer les données (volume db\_data)
docker compose down -v
```

Au premier démarrage, la base est initialisée avec le script `database/init.sql` (création de la table `users`).

## Vérifier que l'application fonctionne

1. `docker compose ps` : les trois services `db`, `backend` et `frontend` sont à l'état *running* (la base est *healthy*).
2. Le backend répond :

```bash
   curl http://localhost:8080/api/health
   # {"status":"ok"}
   ```

3. Dans le navigateur, ouvrir **http://localhost:8080** puis :

   1. remplir « Créer un compte » (e-mail, mot de passe de 8 caractères minimum) : le message « Compte créé » s'affiche ;
   2. se connecter avec ces identifiants : la page « Mon profil » s'affiche ;
   3. modifier le nom et la biographie, cliquer sur « Enregistrer » : le message « Profil mis à jour » s'affiche ;
   4. se déconnecter, se reconnecter : les modifications sont toujours là.
4. Vérifier la persistance : `docker compose down` puis `docker compose up -d`. Se reconnecter avec le même compte : il existe toujours (volume `db\_data`).

## Choix de configuration

* **Secrets hors du dépôt** : mot de passe et clé secrète sont dans `.env` (ignoré par Git). Seul `.env.example`, sans secret réel, est publié.
* **`.dockerignore`** dans `backend/` et `frontend/` : `.env`, `.git` et les fichiers locaux ne sont jamais envoyés dans le contexte de construction des images.
* **Build multi-stage** pour le backend : l'image finale ne contient pas les outils de construction. Le backend s'exécute avec un utilisateur non-root.
* **Nginx en proxy** : le navigateur ne parle qu'au frontend ; les appels `/api/` sont relayés vers `backend:5000`. Aucun problème de CORS et le backend n'est pas exposé.
* **`healthcheck` sur la base** : le backend ne démarre qu'une fois PostgreSQL prêt (`depends\_on` avec `service\_healthy`).
* **Volume nommé `db\_data`** : persistance des données entre deux exécutions.
* **Mots de passe hachés** (Werkzeug) : jamais stockés en clair.

## Test effectué

*Test réalisé en local sur Windows 11 avec Docker Desktop.*



*| Élément | Valeur |*

*|---|---|*

*| Date du test | 25 novembre 2026 |*

*| Système et version de Docker | Windows (Docker Desktop, WSL 2), Docker 29.9.3 |*

*| Commande lancée | `docker compose up --build -d` |*

*| Résultat de `docker compose ps` | 3 services `Up` : `db` (healthy), `backend`, `frontend` (port 8080) |*

*| Résultat de `curl http://localhost:8080/api/health` | `{"status":"ok"}` |*

*| Création de compte, connexion, modification du profil | OK |*

*| Persistance après `down` puis `up` | OK (compte et profil retrouvés grâce au volume `db\_data`) |*

*| Remarques ou problèmes rencontrés | Docker Desktop installé en mode « All-users » (la fonctionnalité Virtual Machine Platform de Windows demandait les droits administrateur). Aucun autre problème. |*Dépannage

* *« DB\_PASSWORD manquant »* : le fichier `.env` n'existe pas, lancer `cp .env.example .env`.
* *Port 8080 déjà utilisé* : changer `FRONTEND\_PORT` dans `.env` (par exemple `8081`).
* *Le mot de passe de la base a été changé dans `.env` mais la connexion échoue* : la base garde l'ancien mot de passe dans le volume. Lancer `docker compose down -v` pour la recréer.

## Structure du dépôt

```
projet\_fil\_rouge\_devops/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   ├── nginx.conf
│   ├── Dockerfile
│   └── .dockerignore
├── database/
│   └── init.sql
├── compose.yaml
├── .env.example
├── .gitignore
└── README.md
```

