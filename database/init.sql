-- Schéma initial : exécuté automatiquement au premier démarrage de la base
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(100) NOT NULL DEFAULT '',
    bio           VARCHAR(500) NOT NULL DEFAULT '',
    created_at    TIMESTAMP NOT NULL DEFAULT NOW()
);
