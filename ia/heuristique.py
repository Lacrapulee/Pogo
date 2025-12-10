from game.board import Board


def heuristique(board):
    """Évalue le plateau pour déterminer l'avantage du joueur IA."""
    score = 0

    for i in range(9):
        pile = board.get_pile(i)
        if not pile:
            continue
        
        top_owner = board.get_top_owner(i)
        height = len(pile)

        if top_owner == 'W':
            score += height  # Les pions blancs ajoutent au score
        elif top_owner == 'B':
            score -= height  # Les pions noirs soustraient du score
            
    return score