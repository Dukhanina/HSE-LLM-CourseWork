import random

class Domino:
    __slots__ = ('a', 'b')
    def __init__(self, a, b):
        self.a = a
        self.b = b
    
    def is_double(self):
        return self.a == self.b
    
    def matches(self, number):
        return self.a == number or self.b == number
    
    def get_other_end(self, number):
        if self.a == number:
            return self.b
        return self.a
    
    def total(self):
        return self.a + self.b
    
    def __str__(self):
        return f"[{self.a}|{self.b}]"
    
    def __repr__(self):
        return str(self)

class Player:
    __slots__ = ('name', 'hand')
    def __init__(self, name):
        self.name = name
        self.hand = []
    
    def draw(self, domino):
        self.hand.append(domino)
    
    def play_domino(self, index):
        return self.hand.pop(index)
    
    def hand_total(self):
        return sum(d.total() for d in self.hand)
    
    def has_playable(self, left_end, right_end):
        for d in self.hand:
            if d.matches(left_end) or d.matches(right_end):
                return True
        return False
    
    def __str__(self):
        return f"{self.name}: " + " ".join(str(d) for d in self.hand)

class DominoGame:
    def __init__(self, num_players, game_type="block", target_score=100):
        player_names = [f"Player {i+1}" for i in range(num_players)]
        self.players = [Player(name) for name in player_names]
        self.game_type = game_type
        self.target_score = target_score
        self.scores = {player: 0 for player in self.players}
        self.current_player_index = 0
        self.chain = []
        self.left_end = None
        self.right_end = None
        self.boneyard = []
        self.setup_complete = False
    
    def create_domino_set(self):
        return [Domino(i, j) for i in range(7) for j in range(i, 7)]
    
    def shuffle_and_draw_first(self):
        shuffled = self.create_domino_set()
        random.shuffle(shuffled)
        highest = -1
        first_player = None
        for player in self.players:
            if not shuffled:
                break
            domino = shuffled.pop()
            player.draw(domino)
            if domino.total() > highest:
                highest = domino.total()
                first_player = player
        for player in self.players:
            if player.hand:
                shuffled.append(player.hand.pop())
        random.shuffle(shuffled)
        return shuffled, first_player
    
    def deal_dominoes(self, domino_set):
        num_players = len(self.players)
        hand_size = 7 if num_players == 2 else 5
        for player in self.players:
            for _ in range(hand_size):
                if domino_set:
                    player.draw(domino_set.pop())
        self.boneyard = domino_set
    
    def setup_game(self):
        domino_set, first_player = self.shuffle_and_draw_first()
        self.deal_dominoes(domino_set)
        idx = self.players.index(first_player)
        self.players = self.players[idx:] + self.players[:idx]
        self.setup_complete = True
    
    def display_board(self):
        if not self.chain:
            print("Board is empty")
            return
        board_str = " ".join(str(domino) for domino in self.chain)
        print(f"Board: {board_str} (Ends: {self.left_end}/{self.right_end})")
    
    def play_first_domino(self, player):
        print(f"\n{player.name}'s turn to set first domino")
        print(player)
        while True:
            try:
                idx = int(input("Select domino index (0 to {}): ".format(len(player.hand)-1)))
                if 0 <= idx < len(player.hand):
                    domino = player.play_domino(idx)
                    self.chain.append(domino)
                    self.left_end = domino.a
                    self.right_end = domino.b
                    print(f"{player.name} plays {domino} as set")
                    return len(player.hand) == 0
                print("Invalid index! Please enter a number between 0 and", len(player.hand)-1)
            except ValueError:
                print("Invalid input! Please enter a number.")
    
    def play_domino_turn(self, player):
        print(f"\n{player.name}'s turn")
        print(player)
        self.display_board()
        
        if not player.has_playable(self.left_end, self.right_end):
            print(f"{player.name} has no playable domino")
            if self.game_type == "draw":
                return self.draw_from_boneyard(player)
            print("Skipping turn")
            return False
        
        while True:
            try:
                idx = int(input("Select domino index (0 to {}): ".format(len(player.hand)-1)))
                if not (0 <= idx < len(player.hand)):
                    print("Invalid index! Please enter a number between 0 and", len(player.hand)-1)
                    continue
                
                domino = player.hand[idx]
                print(f"Selected domino: {domino}")
                
                end_choice = input("Play on which end? (L for left [{}], R for right [{}]): ".format(self.left_end, self.right_end)).strip().upper()
                if end_choice not in ('L', 'R'):
                    print("Invalid choice! Please enter 'L' or 'R'.")
                    continue
                
                target = self.left_end if end_choice == 'L' else self.right_end
                
                if not domino.matches(target):
                    print(f"{domino} doesn't match {target}! Please choose another domino or end.")
                    continue
                
                # Valid play
                player.play_domino(idx)
                if domino.a == target:
                    new_end = domino.b
                else:
                    new_end = domino.a
                
                if end_choice == 'L':
                    self.left_end = new_end
                else:
                    self.right_end = new_end
                
                self.chain.append(domino)
                print(f"{player.name} plays {domino} on {'left' if end_choice == 'L' else 'right'} end")
                return True
                
            except Exception as e:
                print(f"Error: {e}. Please try again.")
    
    def draw_from_boneyard(self, player):
        draw_limit = 1 if len(self.players) > 2 else 2
        if len(self.boneyard) <= draw_limit:
            print("Boneyard exhausted, no draw possible")
            return False
        
        domino = self.boneyard.pop()
        player.draw(domino)
        print(f"{player.name} draws {domino}")
        
        if player.hand[-1].matches(self.left_end) or player.hand[-1].matches(self.right_end):
            print("Drawn domino is playable")
            return self.play_domino_turn(player)
        return False
    
    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        return self.players[self.current_player_index]
    
    def is_blocked(self):
        return all(not p.has_playable(self.left_end, self.right_end) for p in self.players)
    
    def calculate_round_winner(self):
        # Find if any player is out of dominoes
        for player in self.players:
            if len(player.hand) == 0:
                score = sum(p.hand_total() for p in self.players if p != player)
                return player, score
        
        # Blocked game - find player with lowest score
        min_score = min(p.hand_total() for p in self.players)
        potential_winners = [p for p in self.players if p.hand_total() == min_score]
        
        if len(potential_winners) == 1:
            winner = potential_winners[0]
        else:
            # Break tie: player with the lowest single domino
            min_single = 100
            winner = potential_winners[0]
            for p in potential_winners:
                for d in p.hand:
                    if not d.is_double() and d.total() < min_single:
                        min_single = d.total()
                        winner = p
        
        score = sum(p.hand_total() for p in self.players if p != winner)
        return winner, score
    
    def reset_round(self):
        self.chain = []
        self.left_end = None
        self.right_end = None
        self.boneyard = []
        for player in self.players:
            player.hand = []
        self.setup_complete = False
    
    def play_round(self):
        if not self.setup_complete:
            self.setup_game()
        
        print("\n=== Starting new round ===")
        first_winner = self.play_first_domino(self.players[0])
        if first_winner:
            winner = self.players[0]
            score = sum(p.hand_total() for p in self.players[1:])
            self.scores[winner] += score
            print(f"\n{winner.name} wins round with score {score}")
            return
        
        self.current_player_index = 0
        next_player = self.next_player()
        
        while True:
            current_player = self.players[self.current_player_index]
            played = self.play_domino_turn(current_player)
            
            if len(current_player.hand) == 0:
                winner = current_player
                score = sum(p.hand_total() for p in self.players if p != winner)
                self.scores[winner] += score
                print(f"\n{winner.name} wins round with score {score}")
                break
            
            if self.is_blocked():
                winner, score = self.calculate_round_winner()
                self.scores[winner] += score
                print(f"\nGame blocked! {winner.name} wins with score {score}")
                break
            
            next_player = self.next_player()
    
    def play_game(self):
        round_num = 1
        while max(score for score in self.scores.values()) < self.target_score:
            print(f"\n=== Round {round_num} ===")
            self.play_round()
            
            print("\nCurrent Scores:")
            for player, score in self.scores.items():
                print(f"  {player.name}: {score}")
            
            max_score = max(score for score in self.scores.values())
            if max_score >= self.target_score:
                winner = max(self.scores, key=self.scores.get)
                print(f"\n{winner.name} wins the game with {self.scores[winner]} points!")
                return
            
            self.reset_round()
            round_num += 1
            input("\nPress Enter to start next round...")

def main():
    print("Welcome to CLI Dominoes!")
    print("Rules: Match domino ends to play. L/R chooses end to play on.")
    
    while True:
        try:
            num_players = int(input("Number of players (2-4): "))
            if 2 <= num_players <= 4:
                break
            print("Please enter 2, 3, or 4")
        except ValueError:
            print("Invalid input! Please enter a number.")
    
    game_type = input("Game type (block/draw): ").strip().lower()
    while game_type not in ("block", "draw"):
        game_type = input("Enter 'block' or 'draw': ").strip().lower()
    
    game = DominoGame(num_players, game_type, target_score=100)
    game.play_game()

if __name__ == "__main__":
    main()
