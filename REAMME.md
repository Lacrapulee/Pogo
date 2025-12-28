POGO - README

Lancement de l'application

- Démarrer en ligne de commande : `python main.py`
- Dans le menu, choisir l'option `4` pour lancer l'interface graphique.

Raccourcis GUI

- `u` : Annuler (Undo)
- `Ctrl+N` : Nouvelle partie

Règles rapides

- But : contrôler le sommet des piles (avoir au moins une des vos pièces visible au sommet des cases). Le joueur qui couvre toutes les piles adverses gagne.
- À votre tour : sélectionnez une pile dont la couleur au sommet est la vôtre, choisissez le nombre de pièces (1–3 selon hauteur), puis cliquez sur une des cases mises en évidence en vert.
- Le nombre de cases parcourues doit être exactement égal au nombre de pièces déplacées (déplacements orthogonaux uniquement). Pas de demi-tour (180°) dans un même mouvement.

Notes

- L'interface utilise Tkinter, pas de dépendances externes.
- Le slider "Vitesse" dans la barre d'outils contrôle la vitesse des animations.
- Si un déplacement ne fonctionne pas, vérifiez que la case cliquée est bien surlignée en vert et que le nombre de pièces choisi est supporté.
