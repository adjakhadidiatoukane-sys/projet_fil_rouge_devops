# Projet fil rouge DevOps

Application web de **liste de tâches (To-Do)** utilisée comme fil rouge du cours DevOps.
Elle sert de support pour mettre en pratique le versionnement (Git/GitHub), la conteneurisation (Docker), puis l'intégration et le déploiement continus.

## Architecture

| Composant | Technologie | Rôle |
|---|---|---|
| Frontend | HTML, CSS, JavaScript servis par Nginx | Interface utilisateur, relaie les appels `/api/` vers le backend |
| Backend | Python, Flask, Gunicorn | API REST pour gérer les tâches |
| Base de données | PostgreSQL 16 | Stockage des tâches |

```
Navigateur --> Nginx (frontend, port 8080) --> Flask (backend, port 5000) --> PostgreSQL (db)
```

Seul le frontend est exposé sur la machine hôte. Le backend et la base ne sont joignables que par le réseau Docker interne (`reseau_app`, pilote bridge).

## API

| Méthode | Route | Description |
|---|---|---|
| GET | `/api/health` | Vérifie que le backend fonctionne |
| GET | `/api/tasks` | Liste les tâches |
| POST | `/api/tasks` | Crée une tâche (`{"title": "..."}`) |
| PATCH | `/api/tasks/<id>` | Inverse l'état terminé / non terminé |
| DELETE | `/api/tasks/<id>` | Supprime une tâche |

## Lancer le projet

Prérequis : Docker et Docker Compose.

```bash
git clone https://github.com/<utilisateur>/projet_fil_rouge_devops.git
cd projet_fil_rouge_devops
cp .env.example .env        # puis modifier les valeurs si besoin
docker compose up --build
```

L'application est disponible sur http://localhost:8080.

Pour arrêter : `docker compose down` (ajouter `-v` pour supprimer aussi les données).

## Structure

```
projet_fil_rouge_devops/
├── backend/         API Flask (app.py, requirements.txt, Dockerfile)
├── frontend/        Page web et configuration Nginx (Dockerfile)
├── database/        Script SQL d'initialisation
├── docker-compose.yml
├── .env.example     Modèle des variables d'environnement
└── README.md
```

## Variables d'environnement

Définies dans le fichier `.env` (non versionné). Voir `.env.example`.
