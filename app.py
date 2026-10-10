import csv
import io
from flask import Flask, Response, render_template, request, redirect, url_for, session
import database

app = Flask(__name__)
app.secret_key = 'une_cle_tres_secrete_pour_ensam'

# --- 1. ACCUEIL ---
@app.route('/')
def accueil():
    session.clear()
    return render_template('index.html')

# --- 2. CONNEXION PROFESSEUR ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    erreur = None
    if request.method == 'POST':
        email_saisi = request.form['email']
        mdp_saisi = request.form['mot_de_passe']
        
        prof = database.verifier_professeur(email_saisi, mdp_saisi)
        if prof is not None:
            session['prof_id'] = prof['id']
            return redirect(url_for('dashboard'))
        else:
            erreur = "Email ou mot de passe incorrect."
            
    return render_template('login.html', erreur=erreur)

# --- 3. DÉCONNEXION ---
@app.route('/logout')
def logout():
    session.pop('prof_id', None)
    return redirect(url_for('login'))

# --- 4. TABLEAU DE BORD (TICKET 10) ---
@app.route('/dashboard')
def dashboard():
    if 'prof_id' not in session:
        return redirect(url_for('login'))
    
    seances = database.lister_seances_professeur(session['prof_id'])
    return render_template('dashboard.html', seances=seances)

# --- 5. CRÉATION D'UNE SÉANCE (TICKETS 4 & 5) ---
@app.route('/creer_seance', methods=['POST'])
def creer_seance():
    if 'prof_id' not in session:
        return redirect(url_for('login'))
        
    module_nom = request.form['module']
    # Création avec durée par défaut (5 min) et token sécurisé
    duree = int(request.form.get('duree', 5))
    seance = database.creer_seance(module_nom, session['prof_id'], duree_minutes=duree)
    # Génération du QR Code physique dans static/qrcodes/
    database.generer_qr_code(seance['token'])
    
    return redirect(url_for('dashboard'))

# --- 6. AFFICHAGE DU QR CODE ---
@app.route('/qr/<int:seance_id>')
def afficher_qr(seance_id):
    if 'prof_id' not in session:
        return redirect(url_for('login'))
    
    seance = database.get_seance_par_id(seance_id)
    if seance is None:
        return "Séance introuvable", 404
        
    lien_scan = url_for('scan_etudiant', token=seance['token'], _external=True)
    return render_template('qr_code.html', seance=seance, lien_scan=lien_scan)

# --- 7. ESPACE ÉTUDIANT & POINTAGE (TICKET 6 & 8) ---
@app.route('/scan/<token>', methods=['GET', 'POST'])
def scan_etudiant(token):
    seance = database.get_seance_par_token(token)
    if seance is None:
        return "Ce QR Code est invalide.", 404
        
    erreur = None
    succes = None
    
    if request.method == 'POST':
        appoge_saisi = request.form['appoge']
        reussi, message, _ = database.enregistrer_presence(token, appoge_saisi)
        if reussi:
            succes = message
        else:
            erreur = message
                
    return render_template('scan.html', seance=seance, erreur=erreur, succes=succes)

# --- 8. LISTE PRÉSENCES & STATISTIQUES (TICKETS 11 & 12) ---
@app.route('/presences/<int:seance_id>')
def voir_presences(seance_id):
    if 'prof_id' not in session:
        return redirect(url_for('login'))

    seance = database.get_seance_par_id(seance_id)
    if seance is None:
        return "Séance introuvable", 404

    presents, absents = database.get_presences_details(seance_id)
    nb_presents = len(presents)
    nb_absents = len(absents)
    total_inscrits = nb_presents + nb_absents
    taux_presence = round((nb_presents / total_inscrits) * 100, 1) if total_inscrits > 0 else 0.0

    return render_template(
        'liste_presences.html',
        seance=seance,
        presents=presents,
        absents=absents,
        total_inscrits=total_inscrits,
        taux_presence=taux_presence
    )

# --- 9. EXPORT CSV (TICKET 12) ---
@app.route('/exporter_csv/<int:seance_id>')
def exporter_csv(seance_id):
    if 'prof_id' not in session:
        return redirect(url_for('login'))

    seance = database.get_seance_par_id(seance_id)
    if seance is None:
        return "Séance introuvable", 404

    presents, absents = database.get_presences_details(seance_id)

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(['Code Apogee', 'Nom', 'Prenom', 'Classe', 'Statut', 'Date/Heure Pointage'])

    for etudiant in presents:
        writer.writerow([etudiant['appoge'], etudiant['nom'], etudiant['prenom'], etudiant['classe'], 'Present', etudiant['date_pointage']])

    for etudiant in absents:
        writer.writerow([etudiant['appoge'], etudiant['nom'], etudiant['prenom'], etudiant['classe'], 'Absent', 'N/A'])

    nom_fichier = f"presences_seance_{seance_id}_{seance['module'].replace(' ', '_')}.csv"
    return Response(
        '\ufeff' + output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={nom_fichier}"}
    )


@app.route('/fermer_seance/<int:seance_id>')
def fermer(seance_id):
    database.fermer_seance(seance_id)
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)