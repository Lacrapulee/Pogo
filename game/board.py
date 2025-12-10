class Board:
    def __init__(self):
        # Le plateau est une liste de 9 listes (piles), indices 0 à 8.
        # 0 1 2
        # 3 4 5
        # 6 7 8
        self.grille = [[] for _ in range(9)]
        self.setup_board()

    def setup_board(self):
        """Initialise le plateau selon les règles :
           Ligne du haut (0,1,2) : 2 pions Blancs par case
           Ligne du bas (6,7,8) : 2 pions Noirs par case
        """
        # Nettoyage
        self.grille = [[] for _ in range(9)]
        
        # Blancs (White - 'W') en haut
        for i in range(3):
            self.grille[i] = ['W', 'W']
            
        # Noirs (Black - 'B') en bas
        for i in range(6, 9):
            self.grille[i] = ['B', 'B']

    def place_piece(self, i, piece):
        """Place une pièce sur la pile à l'index i (utilisé pour setup ou debug)."""
        if not 0 <= i < 9:
            raise ValueError("Index hors limites")
        self.grille[i].append(piece)

    def place_paquet(self, i, paquet):
        """Place un paquet de pions sur la pile à l'index i."""
        if not 0 <= i < 9:
            raise ValueError("Index hors limites")
        
        # Note : La règle officielle dit "La hauteur des piles n'est pas limitée".
        # Donc on retire la vérification de taille > 3 ici.
        self.grille[i].extend(paquet)

    def retire_paquet(self, i, nombre):
        """Retire `nombre` pions du sommet de la pile i."""
        if not 0 <= i < 9:
            raise ValueError("Index hors limites")

        pile = self.grille[i]
        if len(pile) < nombre:
            raise ValueError("Pas assez de pions dans la pile")

        paquet = pile[-nombre:]
        del pile[-nombre:]
        return paquet

    def get_pile(self, i):
        return self.grille[i]
    
    def get_top_owner(self, i):
        """Retourne le propriétaire de la pile i ('W', 'B' ou None)."""
        if self.grille[i]:
            return self.grille[i][-1]
        return None

    def get_valid_moves(self, player_color):
        """
        Génère tous les coups possibles pour un joueur donné.
        Retourne une liste de tuples : (start_index, num_pieces, dest_index)
        """
        moves = []
        for i in range(9):
            top_owner = self.get_top_owner(i)
            if top_owner == player_color:
                # On peut déplacer 1, 2 ou 3 pièces, limité par la hauteur de la pile
                stack_height = len(self.grille[i])
                max_move = min(3, stack_height)
                
                for n in range(1, max_move + 1):
                    # Trouver les destinations atteignables en n étapes
                    destinations = self._get_reachable_squares(i, n)
                    for dest in destinations:
                        moves.append((i, n, dest))
        return moves

    def _get_reachable_squares(self, start_idx, steps):
        """
        Trouve les cases atteignables depuis start_idx en exactement `steps` déplacements.
        Règles : Orthogonal, pas de diagonale.
        Le nombre de pièces détermine la distance exacte.
        On interdit le demi-tour immédiat (180°) pour respecter la notion de "coude".
        """
        destinations = set()
        
        # Directions : (delta_row, delta_col)
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)] # N, S, W, E
        
        row_s, col_s = divmod(start_idx, 3)

        # DFS pour trouver les chemins
        # stack : (r, c, steps_left, last_move_direction_index)
        stack = [(row_s, col_s, steps, -1)]
        
        while stack:
            r, c, s, last_dir = stack.pop()
            
            if s == 0:
                destinations.add(r * 3 + c)
                continue
            
            for d_idx, (dr, dc) in enumerate(dirs):
                # Interdiction de faire demi-tour (N <-> S, E <-> W)
                # 0(N) vs 1(S), 2(W) vs 3(E). Si somme paire et indices adjacents? 
                # Simple check: si on vient de 0, on ne va pas vers 1.
                if last_dir != -1:
                    if (last_dir == 0 and d_idx == 1) or (last_dir == 1 and d_idx == 0): continue
                    if (last_dir == 2 and d_idx == 3) or (last_dir == 3 and d_idx == 2): continue

                nr, nc = r + dr, c + dc
                if 0 <= nr < 3 and 0 <= nc < 3:
                    stack.append((nr, nc, s - 1, d_idx))
                    
        # On ne peut pas rester sur place (normalement impossible avec la logique sans 180° sauf boucle, 
        # mais la distance graph est stricte)
        if start_idx in destinations:
            destinations.remove(start_idx)
            
        return list(destinations)

    def is_game_over(self):
        """
        Vérifie si un joueur a gagné.
        Condition: Contrôler toutes les piles (non vides) du plateau ? 
        Ou avoir une pièce à soi au sommet de toutes les piles.
        Si l'adversaire n'a plus aucune pièce visible au sommet, on a gagné.
        """
        # On compte les piles contrôlées par chaque joueur
        w_piles = 0
        b_piles = 0
        total_piles = 0
        
        for i in range(9):
            owner = self.get_top_owner(i)
            if owner == 'W': w_piles += 1
            elif owner == 'B': b_piles += 1
            
            if self.grille[i]:
                total_piles += 1
        
        # Si un joueur ne contrôle aucune pile, il a perdu (l'autre a tout recouvert)
        if w_piles > 0 and b_piles == 0:
            return 'W'
        if b_piles > 0 and w_piles == 0:
            return 'B'
            
        return None

    def display(self):
        print("\n=== PLATEAU ===")
        for r in range(3):
            line_str = ""
            for c in range(3):
                idx = r * 3 + c
                pile = self.grille[idx]
                if not pile:
                    content = "."
                else:
                    # Affiche la pile, ex: W,W,B
                    content = "".join(pile)
                line_str += f" [{idx}: {content:^5}] "
            print(line_str)
            print("-" * 30)