import sys
from game.board import Board
from ia.ai_player import AIPlayer

# SI MODE IA : Décommenter les lignes suivantes quand la classe sera prête
# from game.ai import AIPlayer

def print_menu():
    print("\n" + "="*30)
    print("       JEU POGO")
    print("="*30)
    print("1. Mode Solo (Humain vs Humain)")
    print("2. Mode IA (Humain vs Ordinateur)")
    print("3. Quitter")
    print("="*30)

def get_human_move(board, current_player):
    """Demande à l'utilisateur de jouer un coup valide."""
    valid_moves = board.get_valid_moves(current_player)
    
    if not valid_moves:
        print(f"Aucun mouvement possible pour {current_player}. Tour passé.")
        return None

    while True:
        try:
            print(f"\nC'est aux {current_player} ('W'=Blanc, 'B'=Noir) de jouer.")
            user_input = input("Entrez votre coup (Départ NbPièces Arrivée) ex: '0 2 4' : ")
            parts = list(map(int, user_input.split()))
            
            if len(parts) != 3:
                print("Format invalide. Utilisez : Départ NbPièces Arrivée")
                continue
            
            start, n, end = parts[0], parts[1], parts[2]
            
            # Vérification dans la liste des coups pré-calculés
            move = (start, n, end)
            if move in valid_moves:
                return move
            else:
                print("Coup invalide ou impossible selon les règles.")
                print("Coups possibles depuis cette case :")
                possible_dest = [m[2] for m in valid_moves if m[0] == start and m[1] == n]
                if possible_dest:
                    print(f"  Avec {n} pièce(s) depuis {start} -> {possible_dest}")
                else:
                    print("  Aucun coup avec ce nombre de pièces depuis cette case.")
                    
        except ValueError:
            print("Entrée invalide. Veuillez entrer des nombres.")

def play_solo():
    board = Board()
    current_player = 'W' # Les Blancs commencent
    
    while True:
        board.display()
        
        winner = board.is_game_over()
        if winner:
            print(f"\nBRAVO ! Le joueur {winner} a gagné la partie !")
            break
        
        move = get_human_move(board, current_player)
        
        if move:
            start, n, end = move
            paquet = board.retire_paquet(start, n)
            board.place_paquet(end, paquet)
            print(f"> Joueur {current_player} déplace {n} pions de {start} vers {end}.")
        
        # Changement de joueur
        current_player = 'B' if current_player == 'W' else 'W'

def play_ia():
    print("\n[INFO] Le mode IA n'est pas encore activé.")
    print("Pour l'activer, veuillez charger la classe IA dans le code.")
    
    # Structure prévue pour l'IA :
    board = Board()
    ai = AIPlayer("B")  # L'IA joue les Noirs
    current_player = 'W' # Humain commence

    # ... boucle de jeu similaire au solo ...
    while True:
        board.display()
        
        winner = board.is_game_over()
        if winner:
            print(f"\nBRAVO ! Le joueur {winner} a gagné la partie !")
            break
        
        if current_player == "W":
            move = get_human_move(board, current_player)
        
            if move:
                start, n, end = move
                paquet = board.retire_paquet(start, n)
                board.place_paquet(end, paquet)
                print(f"> Joueur {current_player} déplace {n} pions de {start} vers {end}.")
        else:
            move = ai.get_best_move(board)
            if move:
                start, n, end = move
                paquet = board.retire_paquet(start, n)
                board.place_paquet(end, paquet)
                print(f"> IA ({current_player}) déplace {n} pions de {start} vers {end}.")
        
        
        # Changement de joueur
        current_player = 'B' if current_player == 'W' else 'W'


def main():
    while True:
        print_menu()
        choice = input("Votre choix : ")
        
        if choice == '1':
            play_solo()
        elif choice == '2':
            play_ia()
        elif choice == '3':
            print("Au revoir !")
            sys.exit()
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    main()