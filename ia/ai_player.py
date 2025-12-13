from game.board import Board
from ia.heuristique import heuristique
class AIPlayer:
    def __init__(self, player_color):
        self.player_color = player_color  # 'W' ou 'B'

    def minimax(self, board, depth, is_maximizing):
        """Algorithme Minimax pour choisir le meilleur coup."""
        winner = board.is_game_over()
        if depth == 0 or winner is not None:
            return heuristique(board)
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in board.get_valid_moves(self.player_color):
                new_board = board.clone()
                new_board.make_move(move)
                eval = self.minimax(new_board, depth - 1, False)
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            opponent_color = 'B' if self.player_color == 'W' else 'W'
            for move in board.get_valid_moves(opponent_color):
                new_board = board.clone()
                new_board.make_move(move)
                eval = self.minimax(new_board, depth - 1, True)
                min_eval = min(min_eval, eval)
            return min_eval
        

    def get_best_move(self, board):
        """Évalue le plateau pour déterminer l'avantage du joueur IA."""
        best_move = None
        best_value = float('-inf')

        for move in board.get_valid_moves(self.player_color):
            new_board = board.clone()
            new_board.make_move(move)
            move_value = self.minimax(new_board, 3, False)  # Profondeur 3

            if move_value > best_value:
                best_value = move_value
                best_move = move

        return best_move