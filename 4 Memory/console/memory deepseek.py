import random
import time

class MemoryGame:
    def __init__(self, num_pairs=8):
        self.num_pairs = num_pairs
        self.board = []
        self.state = []  # 'hidden', 'visible', 'matched'
        self.current_player = 0
        self.scores = []
        self.first_card = None
        self.second_card = None
        self.game_over = False
        self.players = 1
        
    def setup_game(self, players=1):
        self.players = players
        self.scores = [0] * players
        symbols = list(range(self.num_pairs)) * 2
        random.shuffle(symbols)
        self.board = symbols
        self.state = ['hidden'] * len(self.board)
        self.current_player = 0
        self.first_card = None
        self.second_card = None
        self.game_over = False

    def display_board(self):
        display = []
        for i, status in enumerate(self.state):
            if status == 'hidden':
                display.append('*')
            elif status == 'visible':
                display.append(str(self.board[i]))
            else:  # matched
                display.append(' ')
        return display

    def flip_card(self, index):
        if self.game_over or index < 0 or index >= len(self.board):
            return False
        if self.state[index] != 'hidden':
            return False
        if self.first_card is None:
            self.first_card = index
            self.state[index] = 'visible'
        elif self.second_card is None:
            self.second_card = index
            self.state[index] = 'visible'
            return True
        return False

    def check_match(self):
        if self.first_card is None or self.second_card is None:
            return False
            
        if self.board[self.first_card] == self.board[self.second_card]:
            self.state[self.first_card] = 'matched'
            self.state[self.second_card] = 'matched'
            self.scores[self.current_player] += 1
            self.first_card = None
            self.second_card = None
            
            if all(status == 'matched' for status in self.state):
                self.game_over = True
            return True
        return False

    def next_turn(self):
        self.first_card = None
        self.second_card = None
        self.current_player = (self.current_player + 1) % self.players

def main():
    game = MemoryGame()
    players = int(input("Enter number of players (1-4): ") or "1")
    game.setup_game(players)
    
    while not game.game_over:
        print(f"\nPlayer {game.current_player + 1}'s turn")
        print("Board:", " ".join(game.display_board()))
        print(f"Scores: {', '.join(f'P{i+1}: {s}' for i, s in enumerate(game.scores))}")
        
        try:
            move = int(input("Select a card (0-15): "))
            if not game.flip_card(move):
                print("Invalid move! Card is already visible or matched")
                continue
                
            print("Board:", " ".join(game.display_board()))
            
            if game.second_card is not None:
                if game.check_match():
                    print("Match found!")
                    if game.game_over:
                        print("Game Over!")
                    else:
                        print("You get another turn!")
                        continue
                else:
                    print("No match. Cards will flip back.")
                    time.sleep(2)
                    game.state[game.first_card] = 'hidden'
                    game.state[game.second_card] = 'hidden'
                game.next_turn()
        except ValueError:
            print("Invalid input! Enter a number between 0-15")
    
    print("\nFinal Scores:")
    max_score = max(game.scores)
    for i, score in enumerate(game.scores):
        print(f"Player {i+1}: {score} {'(Winner!)' if score == max_score else ''}")

if __name__ == "__main__":
    main()
