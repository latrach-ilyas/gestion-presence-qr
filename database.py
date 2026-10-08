import sqlite3

DATABASE_NAME = "presence.db"

#Fonction de connexion
def get_db() :
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

#Fonction d'initialisation
def init_db():
    conn = get_db()
    with open("schema.sql",mode="r",encoding="utf-8") as f:
        conn.cursor().executescript(f.read())
    cursor = conn.cursor()

    #Insertion d'un professeur de test
    cursor.execute("""
        INSERT INTO professeurs (nom, prenom, email, mot_de_pass)
        VALUES (?, ?, ?, ?)
    """, ("Alami Kamouri", "Sophia", "prof@ecole.ma", "admin123"))
    prof_id = cursor.lastrowid

    ##Insertion d'une liste d'étudiants de test
    etudiants_demo = [
        ("APG1001", "Benali", "Amine", "INDIA"),
        ("APG1002", "Idrissi", "Sarah", "INDIA"),
        ("APG1003", "Zahraoui", "Mehdi", "INDIA"),
        ("APG1004", "Tazi", "Kenza", "INDIA")
    ]

    # au lieu de faire une boucle for pour inserer chaque etudiant en utilise executemany pour inserer la liste dans une seule requete
    cursor.executemany("""
        INSERT INTO etudiants (appoge, nom, prenom, classe)
        VALUES (?, ?, ?, ?)
    """, etudiants_demo)
    conn.commit() # Enregistrer les modifications
    conn.close()
    print("Base de donnees initialisee avec succes")

# Fcts CRUD pour etudiants
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
    cursor.execute("""
        SELECT * FROM etudiants 
        WHERE appoge = ?
    """, (appoge.strip().upper(),))
    etudiant = cursor.fetchone()
    conn.close()
    return etudiant

def lister_etudiants(classe=None):
    conn = get_db()
    cursor = conn.cursor()
    if classe:
        cursor.execute("""
            SELECT * FROM etudiants 
            WHERE classe = ? 
            ORDER BY nom ASC, prenom ASC
        """, (classe,))
    else:
        cursor.execute("""
            SELECT * FROM etudiants 
            ORDER BY nom ASC, prenom ASC
        """)
    etudiants = cursor.fetchall()
    conn.close()
    return etudiants

def supprimer_etudiant(etudiant_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM etudiants 
        WHERE id = ?
    """, (etudiant_id,))
    conn.commit()
    conn.close()
    return True

# Le point d'entree
if __name__ == "__main__":
    init_db()

    # Petit test pour la gestion des etudiants
    print("\n--- TEST CRUD etudiants ---")

    #Recherche d un etudiant existant par code appoge
    etu = get_etudiant_par_appoge("APG1001")
    if etu is not None:
        print(f"Trouve : {etu['nom']} {etu['prenom']}")
    else:
        print("Etudiant non trouve")
    
    #ajouter un etudiant
    ok =  ajouter_etudiant("APG2000", "Hakimi", "Achraf", "INDIA")
    print(f"Ajout nouvel etudiant : {ok}")

    #Tentative d ajouter un doublon
    doublon = ajouter_etudiant("APG2000", "Autre", "Personne", "INDIA")
    print(f"Blocage doublon reussi : {not doublon}")

    #lister les etu
    tous = lister_etudiants()
    print(f"Nombre total d'etudiants enregistres : {len(tous)}")
