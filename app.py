# [ILAÏ] Importation des outils Flask nécessaires.
# Flask     → crée le serveur web
# render_template → charge un fichier HTML depuis le dossier templates/
# request   → permet de lire les données envoyées par le formulaire HTML
# redirect  → redirige l'utilisateur vers une autre page après une action
from flask import Flask, render_template, request, redirect

# [ILAÏ] json → permet de lire et écrire des fichiers .json (sauvegarde des votes)
# os   → permet de vérifier si un fichier existe sur le disque
import json
import os

# [ILAÏ] Création de l'application Flask.
# __name__ est une variable interne à Python : elle vaut "__main__" quand ce fichier
# est exécuté directement. Flask en a besoin pour savoir où chercher
# les dossiers templates/ et static/.
app = Flask(__name__)

# [ILAÏ] Nom du fichier où les votes sont sauvegardés.
# Écrit en majuscules par convention (d'apres gemini) : c'est une constante, elle ne change jamais.
FICHIER = "donnees.json"


# ==============================================================
# LECTURE DES DONNÉES
# ==============================================================

# [ILAÏ] Fonction qui charge les données depuis le fichier JSON.
# Appelée à chaque fois qu'on a besoin des votes (affichage, calcul).
def charger():

    # [ILAÏ] On vérifie d'abord que le fichier existe.
    # Au premier lancement, il n'existe pas encore — sans cette vérification
    # Python planterait avec une erreur FileNotFoundError.
    # On retourne donc une structure vide par défaut.
    if not os.path.exists(FICHIER):
        return {"total": 0, "nb_votes": 0, "moyenne": 0, "commentaires": []}

    # [ILAÏ] "r" = mode lecture seule.
    # encoding="utf-8" = pour lire correctement les accents (é, à, ç) pareil qu'en html.
    # "with open(...) as f" : ouvre le fichier proprement et le referme, f=fichier
    # automatiquement à la fin du bloc, même en cas d'erreur.
    with open(FICHIER, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            # [ILAÏ] Si le fichier est corrompu ou vide, json.load() plante.
            # On retourne la structure vide plutôt que de laisser le serveur crasher.
            return {"total": 0, "nb_votes": 0, "moyenne": 0, "commentaires": []}


# ==============================================================
# SAUVEGARDE DES DONNÉES
# ==============================================================

# [ILAÏ] Fonction qui écrit les données dans le fichier JSON.
# Appelée après chaque vote pour ne pas perdre les données.
def sauver(d):

    # [ILAÏ] "w" = mode écriture (écrase le contenu existant) donc d sauvegarde ce qu'on avait écrtit avant.
    # encoding="utf-8" = pour écrire correctement les accents.
    # indent=2 → rend le fichier lisible (chaque clé sur sa propre ligne).
    # ensure_ascii=False → conserve les accents dans le fichier, les vieux PC mettaient ensure_ascii=True pour economiser des donnés
    #  (sans ça, "é" serait remplacé par "\u00e9" (src:gemini)).
    with open(FICHIER, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)


# ==============================================================
# ROUTES FLASK
# ==============================================================

# [ILAÏ] Le "@" est un décorateur : il relie l'URL "/" à la fonction index().
# Quand un utilisateur ouvre le site, Flask exécute cette fonction (dans ce cas c'est index).
@app.route("/")
def index():
    # [ILAÏ] render_template() va chercher index.html dans le dossier templates/.
    # On lui passe data=charger() pour que Jinja2 puisse afficher
    # la moyenne et les commentaires via {{ data.moyenne }}, {{ data.nb_votes }}, etc.
    return render_template("index.html", data=charger())


# [ILAÏ] Cette route ne répond qu'aux requêtes POST.
# POST = envoi de données (ici le formulaire de vote).
# Si quelqu'un essaie d'ouvrir /voter directement dans le navigateur (GET),
# Flask renvoie une erreur 405 Method Not Allowed.
@app.route("/voter", methods=["POST"])
def voter():

    # [ILAÏ] request.form.get() récupère la valeur d'un champ du formulaire HTML.
    # Le nom correspond à l'attribut name="..." dans le HTML.
    # Le "or" gère le cas où le champ est vide :
    #   - si prenom est vide → on met "Anonyme", ca marche pas vu qu'on a mit 
    # <input type="text" name="prenom" placeholder="Ton prénom" required> dans notre html
    #   - si note est vide   → on met 5 par défaut
    #   - si commentaire est vide → on met une chaîne vide ""
    nom   = request.form.get("prenom")      or "Anonyme"
    note  = int(request.form.get("note")    or 5)
    texte = request.form.get("commentaire") or ""

    # [ILAÏ] On charge les données existantes pour les mettre à jour.
    d = charger()

    # [ILAÏ] Moyenne mobile cumulative : au lieu de stocker toutes les notes
    # et recalculer à chaque fois, on garde juste le total et le nombre de votes.
    # Plus simple et plus rapide.
    #   Exemple : notes [5, 4, 1, 5]
    #   total = 15, nb_votes = 4, moyenne = 15/4 = 3.75
    d["total"]    += note
    d["nb_votes"] += 1
    d["moyenne"]   = round(d["total"] / d["nb_votes"], 2)

    # [ILAÏ] On ajoute le commentaire à la liste existante.
    # append() ajoute un élément à la fin d'une liste Python.
    d["commentaires"].append({"nom": nom, "note": note, "texte": texte})

    # [ILAÏ] On sauvegarde les données mises à jour dans le fichier JSON.
    sauver(d)

    # [ILAÏ] redirect("/") renvoie l'utilisateur vers la page d'accueil.
    # Sans ça, si l'utilisateur appuie sur F5 après avoir voté,
    # le navigateur renverrait le formulaire et le vote serait compté deux fois.
    return redirect("/")


# ==============================================================
# LANCEMENT DU SERVEUR
# ==============================================================

# [ILAÏ] Cette condition empêche le serveur de se lancer automatiquement
# si ce fichier est importé depuis un autre fichier Python.
# Il ne démarre que si on exécute directement : python app.py
if __name__ == "__main__":
    # [ILAÏ] debug=True : mode développement.
    # Si le code plante, Flask affiche l'erreur dans le navigateur
    # au lieu d'une page blanche. 
    app.run(debug=True)
