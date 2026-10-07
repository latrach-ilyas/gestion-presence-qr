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

# Le point d'entree
if __name__ == "__main__":
    init_db()
