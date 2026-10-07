# Cahier des Charges Fonctionnel
## Projet : Système de Gestion de Présence par QR Code Dynamique
**Ticket :** T-01 (Analyse du besoin & Règles de gestion)  
**Rôles :** Enseignant (Professeur) & Étudiant  
**Date :** Octobre 2026  

---

## 1. Contexte et Objectifs
L'objectif est de remplacer la feuille d'émargement papier traditionnelle par une solution web automatisée, rapide et traçable en classe. 

Le système permet à l'enseignant de générer un QR Code temporaire affiché via vidéoprojecteur. Les étudiants scannent ce code avec leur propre smartphone pour valider leur présence dans un intervalle de temps strictement limité, réduisant les risques d'absentéisme dissimulé ou de transmission de lien hors de la salle.

---

## 2. Acteurs du Système

### 2.1. L'Enseignant (Professeur)
- Initialise une séance de cours pour un module donné.
- Spécifie la durée limite de validation (ex. : 5 ou 10 minutes).
- Projette le QR Code généré au tableau.
- Visualise en temps réel la liste des présences validées.
- Peut clôturer manuellement la séance à tout moment.

### 2.2. L'Étudiant
- Scanne le QR Code projeté à l'aide de l'appareil photo de son smartphone.
- Est redirigé vers une interface web légère et accessible sans application tierce.
- Renseigne son identifiant unique étudiant (CNE / Code Apogée).
- Reçoit un message de confirmation immédiat (succès ou motif d'erreur).

---

## 3. Scénario d'Utilisation (Workflow Nominal)

```text
[ Enseignant ]                           [ Étudiant ]
      |                                       |
  1. Crée la séance                           |
     (Module + Durée)                         |
      |                                       |
  2. Affiche QR Code (avec Token)             |
      |                                       |
      | <------------ 3. Scanne le QR --------|
      |                                       |
      |               4. Saisit son CNE ----->|
      |                                       |
  5. Système vérifie :                        |
     - Validité du token                      |
     - Date limite non dépassée               |
     - CNE valide en base                     |
     - Absence de doublon                     |
      |                                       |
      | ------------ 6. Confirmation -------->|
      |                                       |
  7. Mise à jour                               |
     du tableau de bord                       |
```

---

## 4. Règles de Gestion (Business Rules)

| Règle | Intitulé | Description |
| :--- | :--- | :--- |
| **RG-01** | **Authenticité Étudiant** | L'étudiant doit préalablement figurer dans la base de données. Un identifiant inconnu entraîne un rejet direct (`404 / Non inscrit`). |
| **RG-02** | **Unicité du Pointage** | Un étudiant ne peut émarger qu'une seule fois par séance. Tout doublon est rejeté (`409 / Présence déjà enregistrée`). |
| **RG-03** | **Fenêtre Temporelle Stricte** | Le pointage n'est autorisé qu'entre l'heure de début $T_{\text{début}}$ et $T_{\text{fin}} = T_{\text{début}} + \text{durée}$. Tout pointage postérieur est refusé (`403 / Séance expirée`). |
| **RG-04** | **Sécurité par Jeton (Token)** | L'URL associée au QR Code utilise un jeton cryptographique aléatoire unique (UUID ou chaîne hexadécimale) et non un identifiant incrémental pour empêcher la devinette d'URLs. |
| **RG-05** | **Clôture Manuelle Prioritaire** | Si l'enseignant clôture manuellement la séance avant la fin du compte à rebours, la séance passe immédiatement à l'état inactif. |
| **RG-06** | **Horodatage d'Émargement** | Chaque présence validée conserve l'horodatage exact (`timestamp`) de la validation pour garantir la traçabilité. |

---

## 5. Données Minimales Requises

- **Entité Étudiant :** Identifiant unique (CNE/Apogée), Nom, Prénom.
- **Entité Séance :** Identifiant, Nom du module, Horodatage de création, Durée de validité, Jeton d'accès (Token), Statut actif/clos.
- **Entité Présence :** Référence étudiant, Référence séance, Horodatage de validation.

---

## 6. Critères d'Acceptation de Ticket 1
- [x] Rôles et flux de travail définis.
- [x] Règles anti-triche de premier niveau (durée limitée + token unique) actées.
- [x] Données nécessaires identifiées pour la phase de modélisation SQL (Ticket 2).