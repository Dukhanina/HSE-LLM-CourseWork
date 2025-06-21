import random

class Player:
    __slots__ = ('id', 'position')
    def __init__(self, player_id):
        self.id = player_id
        self.position = 0

class SnakesAndLadders:
    def __init__(self, num_players=2, exact_win=True):
        self.num_players = num_players
        self.players = [Player(i) for i in range(num_players)]
        self.current_player = 0
        self.game_over = False
        self.exact_win = exact_win
        self.snakes = {
            16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 
            64: 60, 87: 24, 93: 73, 95: 75, 98: 78
        }
        self.ladders = {
            1: 38, 4: 14, 9: 31, 21: 42, 28: 84, 
            36: 44, 51: 67, 71: 91, 80: 100
        }
        self.consecutive_sixes = 0
    
    def roll_dice(self):
        return random.randint(1, 6)
    
    def move_player(self, player, dice):
        start_pos = player.position
        new_pos = start_pos + dice
        
        # Handle bounce-back for exact win rule
        if self.exact_win and new_pos > 100:
            bounce = new_pos - 100
            new_pos = 100 - bounce
        
        # Handle fast win rule
        if not self.exact_win and new_pos >= 100:
            new_pos = 100
            player.position = new_pos
            return True, f"Player {player.id} wins the game!"
        
        player.position = new_pos
        
        # Check for snakes or ladders
        action = None
        if new_pos in self.snakes:
            action = f"snake from {new_pos} to {self.snakes[new_pos]}"
            player.position = self.snakes[new_pos]
        elif new_pos in self.ladders:
            action = f"ladder from {new_pos} to {self.ladders[new_pos]}"
            player.position = self.ladders[new_pos]
        
        # Check for win
        if player.position == 100:
            return True, f"Player {player.id} wins the game!"
        
        # Build move description
        move_desc = f"Player {player.id} rolled {dice}: {start_pos} → {new_pos}"
        if action:
            move_desc += f" (Hit {action}) → {player.position}"
        
        return False, move_desc
    
    def play_turn(self):
        if self.game_over:
            return
        
        player = self.players[self.current_player]
        dice = self.roll_dice()
        
        # Handle three consecutive sixes
        if dice == 6:
            self.consecutive_sixes += 1
            if self.consecutive_sixes == 3:
                self.consecutive_sixes = 0
                self.next_player()
                return False, f"Player {player.id} rolled three sixes! Turn skipped."
        else:
            self.consecutive_sixes = 0
        
        # Move player and check for win
        win, message = self.move_player(player, dice)
        
        if win:
            self.game_over = True
            return True, message
        
        # Handle extra turn for rolling a six
        if dice == 6 and not win:
            return False, message + " - Extra turn!"
        
        self.next_player()
        return False, message
    
    def next_player(self):
        self.current_player = (self.current_player + 1) % self.num_players

def determine_first_player(num_players):
    players = list(range(num_players))
    rolls = {}
    
    while len(players) > 1:
        print("Rolling to determine first player:")
        max_roll = 0
        next_round = []
        
        for player_id in players:
            roll = random.randint(1, 6)
            rolls[player_id] = roll
            print(f"Player {player_id} rolled: {roll}")
            if roll > max_roll:
                max_roll = roll
                next_round = [player_id]
            elif roll == max_roll:
                next_round.append(player_id)
        
        if len(next_round) == 1:
            return next_round[0]
        
        print(f"Tie between players: {', '.join(str(p) for p in next_round)}")
        players = next_round
    
    return players[0]

def main():
    print("Welcome to Snakes and Ladders!")
    print("Rules:")
    print("- Roll dice to move forward")
    print("- Land on a ladder to climb up")
    print("- Land on a snake to slide down")
    print("- Roll 6 for extra turn (but three 6s skip turn)")
    print("- First to reach exactly 100 wins\n")
    
    # Get number of players
    while True:
        try:
            num_players = int(input("Number of players (2-4): "))
            if 2 <= num_players <= 4:
                break
            print("Please enter 2, 3, or 4")
        except ValueError:
            print("Invalid input! Please enter a number.")
    
    # Choose win condition
    win_choice = input("Win condition (exact/fast): ").strip().lower()
    exact_win = win_choice != "fast"
    
    # Set up game
    game = SnakesAndLadders(num_players, exact_win)
    first_player = determine_first_player(num_players)
    game.current_player = first_player
    print(f"\nPlayer {first_player} goes first!")
    
    # Game loop
    while not game.game_over:
        player = game.players[game.current_player]
        print(f"\nPlayer {player.id}'s turn (Position: {player.position})")
        input("Press Enter to roll the dice...")
        
        win, message = game.play_turn()
        print(message)
        
        if win:
            break
        
        # Handle extra turn for six
        if "Extra turn" in message:
            print(f"Player {player.id} gets another turn!")
            continue
    
    print("\nGame over!")

if __name__ == "__main__":
    main()
