# nsiflix
# Projet NSI — Système de notation de vidéos

**Ilaï** (Python Flask + JavaScript) · **Jules** (HTML + CSS)

L'objectif : un site web où l'utilisateur regarde un extrait de série, note l'épisode avec des étoiles, et propose des idées pour la suite. Le serveur enregistre les votes, calcule la moyenne automatiquement et empêche les doubles votes. Le design s'inspire volontairement de Netflix : fond noir, accents rouges, interface simple.

---

## Structure du projet

```
project/
├── app.py
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

Cette structure est obligatoire avec Flask :
- `templates/` contient les fichiers HTML utilisés par `render_template()`
- `static/` contient les fichiers CSS, JavaScript et images

**Problème rencontré :** `index.html` doit absolument être dans `templates/`, sinon Flask plante avec :
```python
jinja2.exceptions.TemplateNotFound
```
C'est l'un des premiers bugs du projet — on avait mis le fichier au mauvais endroit.

---

## Répartition des tâches

**Jules** : structure HTML, affichage vidéo, formulaire de vote, thème graphique noir/rouge, mise en page responsive.

**Ilaï** : serveur Flask, routes `/`, `/vote`, `/resultats`, système d'étoiles interactif, calcul de la moyenne cumulative, sauvegarde des votes dans `votes.json`, anti-double vote par cookie.

---

## Méthode de travail

L'objectif principal était de rester autonomes et de vraiment maîtriser notre propre code du début à la fin. On voulait pouvoir expliquer chaque ligne, pas juste avoir quelque chose qui fonctionne sans savoir pourquoi.

Le processus pour chaque fonctionnalité :

1. **Se mettre d'accord sur l'idée** — qu'est-ce qu'on veut exactement ?
2. **Écrire le code "en français"** — décrire la logique en langage naturel avant de toucher au clavier. Par exemple, pour le système d'étoiles :
   > *"Quand la souris passe sur une étoile, toutes les étoiles avant elle s'allument. Quand on clique, la note est enregistrée et les étoiles restent allumées même si on bouge la souris. Quand on envoie le formulaire, la note part au serveur et on ne peut plus modifier."*
3. **Coder avec nos propres connaissances** — sans aide extérieure dans un premier temps.
4. **Chercher des ressources en ligne** — documentation MDN, Flask, exemples concrets.
5. **Demander à l'IA seulement en dernier recours** — et uniquement pour des pistes, pas des solutions complètes.

### Sur l'utilisation des IA

On a utilisé ChatGPT, Claude et Gemini (mode raisonnement) pendant le projet, mais leur aide a été bien moins utile qu'espéré.

Le problème principal : **l'IA propose vite, mais propose souvent faux.** Elle suggère des solutions qui ont l'air logiques, qu'on essaie, qui ne marchent pas, et on se retrouve à déboguer du code qu'on n'a pas écrit et qu'on ne comprend pas vraiment. C'est une perte de temps double — on n'a ni résolu le problème, ni appris quelque chose.

Le pire épisode : après 5 heures de débogage en solo sur un bug persistant, on a décidé de laisser l'IA prendre en main la correction pour aller plus vite. Résultat : elle a réécrit une partie du code, le bug n'était toujours pas corrigé, et le code était devenu tellement différent qu'on ne le comprenait plus. Il a fallu revenir à l'ancienne version et tout reprendre manuellement — ce qui a finalement fonctionné, mais après encore beaucoup de temps.

L'IA a été utile pour des questions précises et isolées — comprendre une notion, ajouter des détails d'animation, comparer deux approches, avoir une explication rapide. Pas pour déboguer ou générer du code fonctionnel directement intégrable.

Pour avoir déjà fait des projets codés quasi entièrement par l'IA, ce projet-ci a été bien plus satisfaisant et bien plus formateur. On comprend ce qu'on a fait, et pourquoi ça marche.

---

## Système d'étoiles (JavaScript)

**C'est la partie qui a pris le plus de temps — plus de 10 heures au total.** Le comportement semblait simple à décrire, mais les cas limites s'accumulaient : étoiles qui ne restaient pas allumées après le clic, prévisualisation au survol qui écrasait la sélection, note qui se réinitialisait à zéro au moindre mouvement de souris. Chaque correction en introduisait une nouvelle.

L'IA n'a pas vraiment aidé ici. Les suggestions proposées ne correspondaient pas exactement à notre structure de code, et les intégrer créait de nouveaux bugs. On a fini par tout régler manuellement, en lisant la documentation et en testant méthodiquement.

Le principe final : survol = prévisualisation, clic = sélection, envoi = vote définitif.

### Fonction principale (on l'a peut être modifié dans la version finale)

```

`classList.toggle('active', i < n)` fait deux actions en une ligne : ajoute la classe `active` si `i < n`, la retire sinon. Donc `setActive(3)` allume les 3 premières étoiles et éteint toutes les autres automatiquement.

La version équivalente avec `if`, pour comparaison :
```javascript
function setActive(n) {
    stars.forEach((s, i) => {
        if (i < n) {
            s.classList.add('active')
        } else {
            s.classList.remove('active')
        }
    })
}
```
Les deux fonctionnent, mais `toggle` est plus concis. C'est Claude qui a signalé cette alternative — c'est le genre de question précise où l'IA est utile.

### Gestion du survol

```javascript
s.addEventListener('mouseleave', () => {
    if (aVote) return;
    setActive(noteChoisie);
});
```

Quand la souris quitte une étoile, on revient à la note réellement choisie (`noteChoisie`) et pas à zéro. Sans ça, l'utilisateur perd visuellement sa sélection à chaque mouvement — c'était l'un des bugs les plus longs à identifier et corriger.

### Fonctions fléchées

```javascript
() => {}   // remplace   function() {}
```

Par exemple `.then(r => r.json())` est équivalent à :
```javascript
.then(function(r) {
    return r.json();
})
```
Plus court et plus lisible.

---

## Envoi des votes avec `fetch()`

```javascript
fetch('/vote', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ note: noteChoisie, prenom: prenom, commentaire: commentaire })
})
.then(r => r.json())
.then(data => { console.log(data); });
```

- **`fetch()`** : envoie une requête HTTP sans recharger la page. C'est asynchrone — ça ne bloque pas le reste du programme pendant l'exécution.
- **`Content-Type: application/json`** : indique à Flask que ce qui arrive est du JSON.
- **`JSON.stringify()`** : convertit l'objet JS `{ note: 5 }` en texte `{"note":5}`, car HTTP ne transmet que du texte.
- **`.then(r => r.json())`** : convertit la réponse brute en objet JavaScript utilisable.
- **`.then(data => {...})`** : permet d'utiliser les données renvoyées par Flask.

---

## Validation côté serveur

Le serveur ne fait jamais confiance au JavaScript — il revérifie tout :
```python
if not note or not isinstance(note, int) or not (1 <= note <= 5):
    return jsonify({"erreur": "Note invalide"}), 400
```

### Pourquoi `isinstance(note, int)` ?

*(Chatgpt a aidé à comprendre ce point — j'avais peur que les nombres ne soient pas perçus du même "type" par le code)*

En Python, `"3"` (string) et `3` (entier) sont deux types différents que Python refuse de comparer directement. Si JS envoie la note sous forme de texte, le serveur plante. `isinstance(note, int)` vérifie le type avant tout traitement.

Côté JS, `+s.dataset.n` convertit la chaîne en nombre avant l'envoi :
```
"4"  →  4
```

---

## Moyenne cumulative

```python
data["total"] += note
data["nb_votes"] += 1
data["moyenne"] = round(data["total"] / data["nb_votes"], 2)
```

Au lieu de stocker toutes les notes `[5, 4, 1, 5]` et recalculer à chaque fois, on ne garde que le total et le nombre de votes — plus simple et plus rapide.

| Vote | Note | Calcul        | Moyenne |
|------|------|---------------|---------|
| 1    | 5    | 5 / 1         | 5.00    |
| 2    | 4    | (5+4) / 2     | 4.50    |
| 3    | 1    | (5+4+1) / 3   | 3.33    |
| 4    | 5    | (5+4+1+5) / 4 | 3.75    |

---

## Anti-double vote (cookies) on l'a finallement enlevé car on voulait que tout le monde puisse envoyer plusieurs commentaires

```python
if request.cookies.get("a_deja_vote"):
    return jsonify({"erreur": "Vous avez déjà voté !"}), 403
```

Flask vérifie seulement **l'existence** du cookie, pas sa valeur. Que le cookie vaille `"1"` ou `"bonjour"`, le résultat est le même : vote refusé.

```python
reponse.set_cookie("a_deja_vote", "1", max_age=60*60*24*365)  # 1 an
```

**Limite connue (signalée par Claude) :** un utilisateur peut supprimer ses cookies et revoter. Une vraie protection nécessiterait une base de données avec identification. On n'a pas su implémenter ça dans le cadre du projet, et l'IA n'a pas proposé de solution simple et compréhensible — les pistes données étaient trop complexes à intégrer sans tout casser.

---

## Note sur `__name__`

Pendant le développement, une question s'est posée : pourquoi `__name__` et pas `_name_` ou `name` ?

Les doubles underscores (`__`) signalent des noms réservés au fonctionnement interne de Python — appelés "dunder" (double underscore). `__main__` est le nom donné automatiquement au fichier Python quand il est exécuté directement. Cette convention évite les conflits avec des variables normales.

---

## Lecture et sauvegarde JSON

```python
def lire_votes():
    if not os.path.exists(VOTES_FILE):
        return {"total": 0, "nb_votes": 0, "moyenne": 0, "historique": []}
    with open(VOTES_FILE, "r") as f:
        return json.load(f)
```

Au premier lancement, `votes.json` n'existe pas encore. Sans cette vérification, Python plante avec `FileNotFoundError`. ChatGPT a suggéré cette précaution — c'est un exemple où une question précise et isolée a reçu une réponse utile et directement applicable.

```python
def sauvegarder_votes(data):
    with open(VOTES_FILE, "w") as f:
        json.dump(data, f, indent=2)
```

`indent=2` ne change pas le fonctionnement, juste la lisibilité :

Sans indent : `{"total":15,"nb_votes":4}`

Avec indent :
```json
{
  "total": 15,
  "nb_votes": 4
}
```

---

## Jinja2 — Pourquoi ce choix ?

Jinja2 est le moteur de templates par défaut de Flask. Sa syntaxe est proche du Python, et il nettoie automatiquement les données pour éviter les attaques XSS.

**Alternatives considérées :**
- *Mako* : plus rapide, mais on peut écrire trop de Python directement dans le HTML, ce qui rend le code moins propre.
- *Django Templates* : très proche de Jinja2, mais lié au framework Django.
- *React / Vue.js* : le navigateur construit tout en JavaScript côté client — plus fluide, mais bien trop complexe pour ce projet.

Jinja2 reste le meilleur compromis pour apprendre à séparer les données (Python) de l'affichage (HTML).

---

## Problèmes rencontrés

| Problème | Cause | Solution |
|---|---|---|
| `TemplateNotFound` | HTML dans le mauvais dossier | Placer dans `templates/` |
| CSS non appliqué | Mauvais chemin | Corriger la route statique |
| Double vote possible | Aucune protection | Ajout des cookies |
| `TypeError` str/int | Note envoyée en string | Conversion JS avec `+` |
| Erreur GitHub release | Problème de déploiement | Réessayer plus tard |
| `templates/` renommé en `static/` | Bug GitHub inexpliqué | Réessayer plus tard |
| Étoiles instables | Multiples cas limites imbriqués | +10h de correction manuelle |
| Commentaires non sauvegardés | Erreur de syntaxe JS | Correction manuelle, problème non entièrement résolu |

---

## Bilan

Ce projet a été beaucoup plus difficile que prévu — et beaucoup plus formateur.

La partie Flask demande une vraie compréhension logique. Pas juste écrire du code qui a l'air correct, mais comprendre pourquoi ça marche, pourquoi ça casse, et comment corriger proprement.

**Sur l'IA :** on pensait qu'elle allait accélérer le développement. En pratique, elle a souvent ralenti. Pour des questions précises et isolées, elle est utile. Pour déboguer un vrai problème dans un vrai projet, elle génère du code qu'on ne comprend pas, qui ne fonctionne pas, et qui crée de nouveaux problèmes. Le pire n'est pas qu'elle se trompe — c'est qu'elle donne l'impression d'avoir raison, ce qui fait perdre du temps à essayer des solutions qui ne marchent pas.

La méthode qui a vraiment fonctionné : écrire la logique en français d'abord, coder avec ses propres connaissances, chercher dans la documentation, et ne demander de l'aide qu'en dernier recours sur des points très précis.

Les commentaires n'ont finalement pas pu être correctement sauvegardés — c'est le principal regret du projet. Mais sur tout le reste, on sait exactement ce qu'on a fait et pourquoi ça marche.

---

## Sources

MDN (HTML, CSS, JS, Fetch API, Cookies) · Flask docs · Jinja2 docs · GeeksforGeeks (json.dump) · javascript.info (Ninja code) · pytutorial.com (TypeError str/int) · dev.to (Template literals) · grafikart.fr · ChatGPT · Claude · Gemini (mode raisonnement)
