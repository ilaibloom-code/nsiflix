/* ============================================================
   script.js — NSIFlix
   Réalisé par Ilaï
   ============================================================ */


// [ILAÏ] querySelectorAll('.etoile') : récupère TOUS les éléments avec la classe "etoile"
// dans un tableau (NodeList). On peut ensuite parcourir ce tableau avec forEach().
// Contrairement à getElementById() qui ne retourne qu'un seul élément.
const stars = document.querySelectorAll('.etoile');

// [ILAÏ] noteChoisie : variable qui mémorise la note actuellement sélectionnée.
// Elle commence à 5 (la valeur par défaut du champ caché dans le HTML).
// Elle est mise à jour à chaque clic sur une étoile.
let noteChoisie = 5;

// [ILAÏ] aVote : booléen (vrai/faux) qui indique si l'utilisateur a déjà voté.
// Sert à empêcher de changer la note après avoir soumis le formulaire,
// et à conserver la sélection visuelle après un survol.
let aVote = false;


// ============================================================
// FONCTION setActive(n) — Ilaï
// ============================================================
// Allume les n premières étoiles et éteint les autres.
//
// Avant (version avec if, suggérée par ChatGPT pour comparer) :
//   function setActive(n) {
//       stars.forEach((s, i) => {
//           if (i < n) {
//               s.classList.add('active')
//           } else {
//               s.classList.remove('active')
//           }
//       })
//   }
//
// Version finale avec toggle (plus concise, même résultat) :
function setActive(n) {
    // [ILAÏ] forEach parcourt chaque étoile du tableau.
    // "s" = l'étoile courante, "i" = son index (0 à 4).
    stars.forEach((s, i) => {
        // [ILAÏ] classList.toggle('active', condition) :
        //   - AJOUTE la classe 'active' si la condition est vraie (i < n)
        //   - RETIRE la classe 'active' si la condition est fausse
        // C'est plus court qu'un if/else séparé.
        // En CSS, la classe 'active' change la couleur de l'étoile en rouge.
        s.classList.toggle('active', i < n);
    });
}


// ============================================================
// FONCTION regler(n) — Ilaï
// ============================================================
// Appelée par onclick="regler(X)" dans le HTML quand on clique sur une étoile.
// Met à jour la note sélectionnée visuellement ET dans le champ caché du formulaire.
function regler(n) {
    // [ILAÏ] Mémorise la note choisie dans la variable globale.
    noteChoisie = n;

    // [ILAÏ] Met à jour le champ caché <input type="hidden" id="la_note">.
    // C'est ce champ que le formulaire HTML va envoyer au serveur Flask.
    // Sans cette ligne, Flask recevrait toujours la valeur par défaut (5).
    document.getElementById('la_note').value = n;

    // [ILAÏ] Met à jour l'affichage visuel des étoiles.
    setActive(n);
}


// ============================================================
// SURVOL DES ÉTOILES — Ilaï
// ============================================================
// On ajoute des écouteurs d'événements sur chaque étoile pour gérer
// la prévisualisation au survol (avant que l'utilisateur clique).
stars.forEach((s, i) => {

    // [ILAÏ] 'mouseenter' : déclenché quand la souris entre sur l'étoile.
    // On affiche une prévisualisation : toutes les étoiles jusqu'à celle survolée s'allument.
    // +s.dataset.n : récupère la valeur de data-n="X" dans le HTML et la convertit en nombre.
    //   Le "+" devant convertit la chaîne "3" en nombre entier 3.
    //   C'est nécessaire car les attributs HTML sont toujours des chaînes de caractères,
    //   et setActive() a besoin d'un nombre pour comparer avec i.
    s.addEventListener('mouseenter', () => {
        setActive(+s.dataset.n);
    });

    // [ILAÏ] 'mouseleave' : déclenché quand la souris quitte l'étoile.
    // Si l'utilisateur a déjà voté, on ne fait rien (return).
    // Sinon, on revient à la note réellement choisie (noteChoisie),
    // pas à zéro — sinon l'utilisateur perdrait visuellement sa sélection.
    s.addEventListener('mouseleave', () => {
        if (aVote) return;
        setActive(noteChoisie);
    });
});


// ============================================================
// NOTE PAR DÉFAUT — Ilaï
// ============================================================
// Au chargement de la page, on allume 5 étoiles (note par défaut).
// Cohérent avec value="5" dans le champ caché du HTML.
regler(5);


// ============================================================
// NOTE : ce projet utilise un formulaire HTML classique (method="POST")
// pour envoyer les votes, pas fetch().
//
// La version avec fetch() aurait permis d'envoyer le vote sans 
// recharger la page (asynchrone), comme ceci :
//
//   fetch('/vote', {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({ note: noteChoisie, prenom: prenom, commentaire: commentaire })
//   })
//   .then(r => r.json())       // r => r.json() = fonction fléchée, équivalent à function(r) { return r.json() }
//   .then(data => {
//       console.log(data);     // utilise la réponse JSON de Flask
//   });
//
// Différence :
//   - Formulaire HTML → la page se recharge après le vote (plus simple à coder)
//   - fetch() → pas de rechargement, mise à jour dynamique (plus complexe, plus fluide)
//
// Les fonctions fléchées () => {} remplacent function() {}.
// C'est une syntaxe plus courte, conseillée pour les callbacks courts.
// ============================================================
