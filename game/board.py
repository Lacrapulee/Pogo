class Board:

    def __init__(self):
        # 9 piles vides
        self.grille = [[] for _ in range(9)]

    def place_piece(self, i, piece):
        """Place une pièce sur la pile à l'index i."""
        if not 0 <= i < 9:
            raise ValueError("Index hors limites")

        if len(self.grille[i]) >= 3:
            raise ValueError("Colonne pleine")

        self.grille[i].append(piece)

    def place_paquet(self, i, paquet):
        """Place un paquet de pions sur la pile à l'index i."""
        if not 0 <= i < 9:
            raise ValueError("Index hors limites")

        pile = self.grille[i]

        if len(pile) + len(paquet) > 3:
            raise ValueError("Pas assez d'espace dans la pile")

        pile.extend(paquet)

    def retire_paquet(self, i, nombre):
        """Retire `nombre` pions du sommet de la pile i et les renvoie sous forme de liste."""
        if not 0 <= i < 9:
            raise ValueError("Index hors limites")

        pile = self.grille[i]

        if len(pile) < nombre:
            raise ValueError("Pas assez de pions dans la pile")

        paquet = pile[-nombre:]   
        del pile[-nombre:]        

        return paquet

    def get_piece(self, i):
        """Retourne la pile de pions à l'index i."""
        if not 0 <= i < 9:
            raise ValueError("Index hors limites")

        return self.grille[i]

    def get_plateau(self):
        """Retourne la grille entière."""
        return self.grille
