import sqlite3
import secrets
import os
import qrcode
from datetime import datetime, timedelta

DATABASE_NAME = "presence.db"

# --- Connexion ---
def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# --- Initialisation ---
def init_db():
    conn = get_db()
    with open("schema.sql", mode="r", encoding="utf-8") as f:
        conn.cursor().executescript(f.read())
    cursor = conn.cursor()

    # Professeur de test
    cursor.execute("""
        INSERT INTO professeurs (nom, prenom, email, mot_de_pass)
        VALUES (?, ?, ?, ?)
    """, ("Alami Kamouri", "Sophia", "prof@ecole.ma", "admin123"))

    # Étudiants de test
    etudiants_demo = [
        ("APG1001", "Benali", "Amine", "INDIA"),
        ("APG1002", "Idrissi", "Sarah", "INDIA"),
        ("APG1003", "Zahraoui", "Mehdi", "INDIA"),
        ("APG1004", "Tazi", "Kenza", "INDIA")
    ]
    cursor.executemany("""
        INSERT INTO etudiants (appoge, nom, prenom, classe)
        VALUES (?, ?, ?, ?)
    """, etudiants_demo)
    
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée avec succès.")

# =======================================================
# AUTHENTIFICATION PROFESSEUR
# =======================================================
def verifier_professeur(email, mot_de_passe):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM professeurs 
        WHERE email = ? AND mot_de_pass = ?
    """, (email.strip(), mot_de_passe.strip()))
    prof = cursor.fetchone()
    conn.close()
    return prof

# =======================================================
# TICKET 3 : GESTION DES ÉTUDIANTS (CRUD)
# =======================================================
def ajouter_etudiant(appoge, nom, prenom, classe):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO etudiants (appoge, nom, prenom, classe)
            VALUES (?, ?, ?, ?)
        """, (appoge.strip().upper(), nom.strip(), prenom.strip(), classe.strip()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_etudiant_par_appoge(appoge):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM etudiants WHERE appoge = ?", (appoge.strip().upper(),))
    etudiant = cursor.fetchone()
    conn.close()
    return etudiant

def lister_etudiants(classe=None):
    conn = get_db()
    cursor = conn.cursor()
    if classe:
        cursor.execute("SELECT * FROM etudiants WHERE classe = ? ORDER BY nom ASC, prenom ASC", (classe,))
    else:
        cursor.execute("SELECT * FROM etudiants ORDER BY nom ASC, prenom ASC")
    etudiants = cursor.fetchall()
    conn.close()
    return etudiants

# =======================================================
# TICKET 4 : GESTION DES SÉANCES
# =======================================================
def creer_seance(module, professeur_id, duree_minutes=5):
    token = secrets.token_urlsafe(8)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO seances (module, professeur_id, duree_minutes, token)
        VALUES (?, ?, ?, ?)
    """, (module.strip(), professeur_id, duree_minutes, token))
    conn.commit()
    conn.close()
    return get_seance_par_token(token)

def get_seance_par_id(seance_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM seances WHERE id = ?", (seance_id,))
    seance = cursor.fetchone()
    conn.close()
    return seance

def get_seance_par_token(token):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM seances WHERE token = ?", (token,))
    seance = cursor.fetchone()
    conn.close()
    return seance

def lister_seances_professeur(professeur_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM seances 
        WHERE professeur_id = ? 
        ORDER BY date_debut DESC
    """, (professeur_id,))
    lignes = cursor.fetchall()
    conn.close()
    seances = []
    maintenant = datetime.utcnow()
    for row in lignes:
        s = dict(row)
        # Parse date_debut
        try:
            date_debut = datetime.strptime(s["date_debut"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            date_debut = datetime.fromisoformat(s["date_debut"])

        date_expiration = date_debut + timedelta(minutes=s["duree_minutes"])

        # Séance active ghir ila kant est_active == 1 W baqi ma fat l'weqt
        if s["est_active"] == 1 and maintenant <= date_expiration:
            s["statut_reel"] = "Active"
        else:
            s["statut_reel"] = "Terminée"
            
        seances.append(s)

    return seances

def seance_est_valide(seance):
    if not seance:
        return False, "Séance introuvable."
    if seance["est_active"] == 0:
        return False, "Cette séance a été fermée par le professeur."
    # SQLite DEFAULT CURRENT_TIMESTAMP kay-koun b format 'YYYY-MM-DD HH:MM:SS'
    try:
        date_debut = datetime.strptime(seance["date_debut"], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        date_debut = datetime.fromisoformat(seance["date_debut"])

    date_expiration = date_debut + timedelta(minutes=seance["duree_minutes"])
    if datetime.utcnow() > date_expiration:
        return False, "Le temps alloué au pointage est écoulé."

    return True, "Séance ouverte."

def fermer_seance(seance_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE seances SET est_active = 0 WHERE id = ?", (seance_id,))
    conn.commit()
    conn.close()
    return True

# =======================================================
# TICKET 5 : GÉNÉRATION DU QR CODE
# =======================================================
def generer_qr_code(token, base_url="http://127.0.0.1:5000"):
    url_presence = f"{base_url}/scan/{token}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )
    qr.add_data(url_presence)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    dossier_destination = os.path.join("static", "qrcodes")
    os.makedirs(dossier_destination, exist_ok=True)

    nom_fichier = f"{token}.png"
    chemin_fichier = os.path.join(dossier_destination, nom_fichier)
    img.save(chemin_fichier)
    return f"qrcodes/{nom_fichier}"

# =======================================================
# TICKET 6 : ENREGISTREMENT DE LA PRÉSENCE & STATS
# =======================================================
def enregistrer_presence(token, appoge):
    """
    Validation complète :
    1. Vérifie si la séance existe et si elle est valide (Ticket 4).
    2. Vérifie si l'étudiant existe via son code Apogée (Ticket 3).
    3. Tente l'insertion (gère le doublon automatiquement).
    """
    seance = get_seance_par_token(token)
    valide, msg = seance_est_valide(seance)
    if not valide:
        return False, msg, None

    etudiant = get_etudiant_par_appoge(appoge)
    if not etudiant:
        return False, "Étudiant introuvable. Vérifiez votre code Apogée.", None

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO presences (etudiant_id, seance_id)
            VALUES (?, ?)
        """, (etudiant["id"], seance["id"]))
        conn.commit()
        return True, f"Présence validée pour {etudiant['prenom']} {etudiant['nom']} !", etudiant
    except sqlite3.IntegrityError:
        return False, "Votre présence a déjà été validée pour cette séance.", etudiant
    finally:
        conn.close()

def get_presences_details(seance_id):
    """Récupère les étudiants présents et absents pour une séance."""
    conn = get_db()
    cursor = conn.cursor()

    presents = cursor.execute('''
        SELECT etudiants.appoge, etudiants.nom, etudiants.prenom, etudiants.classe, presences.date_pointage
        FROM presences
        JOIN etudiants ON presences.etudiant_id = etudiants.id
        WHERE presences.seance_id = ?
        ORDER BY presences.date_pointage ASC
    ''', (seance_id,)).fetchall()

    absents = cursor.execute('''
        SELECT id, appoge, nom, prenom, classe
        FROM etudiants
        WHERE id NOT IN (
            SELECT etudiant_id FROM presences WHERE seance_id = ?
        )
        ORDER BY nom ASC
    ''', (seance_id,)).fetchall()

    conn.close()
    return presents, absents