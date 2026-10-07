DROP TABLE IF EXISTS presences;
DROP TABLE IF EXISTS seances;
DROP TABLE IF EXISTS professeurs;
DROP TABLE IF EXISTS etudiants;

PRAGMA foreign_keys = ON;

-- Table des professeurs
CREATE TABLE professeurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    mot_de_pass TEXT NOT NULL
);

-- Table des etudiants
CREATE TABLE etudiants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    appoge TEXT UNIQUE NOT NULL, -- identifiant unique de l'etudiant
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    classe TEXT NOT NULL
);

-- Table des seances
CREATE TABLE seances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module TEXT NOT NULL,
    professeur_id INTEGER NOT NULL,
    date_debut TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duree_minutes INTEGER NOT NULL  DEFAULT 5,
    est_active INTEGER NOT NULL DEFAULT 1,
    token TEXT UNIQUE NOT NULL,
    FOREIGN KEY (professeur_id) REFERENCES professeurs (id) ON DELETE CASCADE
);

-- Table des presences
CREATE TABLE presences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    seance_id INTEGER NOT NULL,
    date_pointage TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES etudiants (id) ON DELETE CASCADE,
    FOREIGN KEY (seance_id) REFERENCES seances (id) ON DELETE CASCADE,
    UNIQUE (etudiant_id, seance_id) -- le couple (etudiant_id, seance_id) est unique
);
