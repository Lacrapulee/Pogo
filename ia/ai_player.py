from game.board import Board
class AIPlayer:
    def __init__(self, player_color):
        self.player_color = player_color  # 'W' ou 'B'

    def minimax(self, board, depth, is_maximizing):
        """Algorithme Minimax pour choisir le meilleur coup."""
        winner = board.is_game_over()
        if winner == self.player_color:
            return 10 - depth
        elif winner is not None:
            return depth - 10
        
        if is_maximizing:
            best_score = float('-inf')
            for move in board.get_valid_moves(self.player_color):
                start, n, end = move
                paquet = board.retire_paquet(start, n)
                board.place_paquet(end, paquet)
                
                score = self.minimax(board, depth + 1, False)
                
                board.retire_paquet(end, n)
                board.place_paquet(start, paquet)
                
                best_score = max(score, best_score)
            return best_score
        else:
            opponent_color = 'B' if self.player_color == 'W' else 'W'
            best_score = float('inf')
            for move in board.get_valid_moves(opponent_color):
                start, n, end = move
                paquet = board.retire_paquet(start, n)
                board.place_paquet(end, paquet)
                
                score = self.minimax(board, depth + 1, True)
                
                board.retire_paquet(end, n)
                board.place_paquet(start, paquet)
                
                best_score = min(score, best_score)
            return best_score

    def get_possible_destinations(self, board, start, n):
        """Retourne une liste des indices de piles où `n` pièces peuvent être déplacées depuis `start`."""
        destinations = []
        for end in range(9):
            if end != start:
                # Règle simple : on peut déplacer vers une pile vide ou une pile avec moins de 3 pièces
                if len(board.get_pile(end)) < 3:
                    destinations.append(end)
        return destinations