-- Schéma initial de la base de données
CREATE TABLE IF NOT EXISTS tasks (
    id         SERIAL PRIMARY KEY,
    title      VARCHAR(200) NOT NULL,
    done       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO tasks (title, done) VALUES
    ('Créer le dépôt GitHub', TRUE),
    ('Conteneuriser l''application', FALSE);
