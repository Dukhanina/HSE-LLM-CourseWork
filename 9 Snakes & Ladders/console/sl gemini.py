import random

class SnakesLaddersGame:
    def __init__(self, num_players=2):
        self.BOARD_SIZE = 100
        self.LADDERS = {
            2: 38, 7: 14, 8: 31, 15: 26, 21: 42,
            28: 84, 36: 44, 51: 67, 71: 91, 78: 98
        }
        self.SNAKES = {
            16: 6, 46: 25, 49: 11, 62: 19, 64: 60,
            74: 53, 89: 68, 92: 88, 95: 75, 99: 80
        }
        
        self.num_players = num_players
        self.player_positions = [1] * num_players
        self.current_player_idx = 0
        self.game_over = False

    def roll_dice(self):
        return random.randint(1, 6)

    def _get_initial_player_order(self):
        roll_results = []
        for i in range(self.num_players):
            while True:
                input(f"Player {i+1}, press Enter to roll for turn order...")
                roll = self.roll_dice()
                print(f"Player {i+1} rolled a {roll}.")
                roll_results.append({'player_idx': i, 'roll': roll})
                
                # Check for ties among the highest rollers
                highest_roll_so_far = max(r['roll'] for r in roll_results)
                tied_players = [r for r in roll_results if r['roll'] == highest_roll_so_far]
                if len(tied_players) == 1:
                    break # No ties for the highest roll
                elif len(tied_players) == len(roll_results): # All players tied, re-roll all
                    print("All players tied for the highest roll, re-rolling for all tied players.")
                    roll_results = []
                    continue
                else: # Some tied, others not, only highest tied re-roll (simplified: everyone rolls until one clear winner)
                    break 

        roll_results.sort(key=lambda x: x['roll'], reverse=True)
        self.current_player_idx = roll_results[0]['player_idx']
        print(f"Player {self.current_player_idx+1} goes first!")

    def move_player(self, player_idx, steps):
        current_pos = self.player_positions[player_idx]
        new_pos = current_pos + steps

        if new_pos > self.BOARD_SIZE:
            new_pos = self.BOARD_SIZE - (new_pos - self.BOARD_SIZE)
            print(f"Bounced back to {new_pos}.")
        
        print(f"Player {player_idx+1} moved from {current_pos} to {new_pos}.")

        if new_pos in self.LADDERS:
            print(f"Wow! Player {player_idx+1} found a ladder from {new_pos} to {self.LADDERS[new_pos]}!")
            new_pos = self.LADDERS[new_pos]
        elif new_pos in self.SNAKES:
            print(f"Oh no! Player {player_idx+1} hit a snake from {new_pos} to {self.SNAKES[new_pos]}!")
            new_pos = self.SNAKES[new_pos]
        
        self.player_positions[player_idx] = new_pos
        print(f"Player {player_idx+1} is now at square {new_pos}.")
        
        if new_pos == self.BOARD_SIZE:
            self.game_over = True
            print(f"Player {player_idx+1} reached square {self.BOARD_SIZE}!")

    def display_board(self):
        print("\n--- Current Board State ---")
        for i, pos in enumerate(self.player_positions):
            print(f"Player {i+1}: Position {pos}")
        print("--------------------------")

    def run_game(self):
        print("Welcome to Snakes and Ladders!")
        self._get_initial_player_order()

        while not self.game_over:
            self.display_board()
            player_id = self.current_player_idx + 1
            print(f"\nPlayer {player_id}'s turn.")
            
            input("Press Enter to roll the dice...")
            roll = self.roll_dice()
            print(f"Player {player_id} rolled a {roll}.")

            self.move_player(self.current_player_idx, roll)
            
            if self.game_over:
                print(f"Player {player_id} wins the game!")
                break
            
            if roll != 6:
                self.current_player_idx = (self.current_player_idx + 1) % self.num_players
            else:
                print(f"Player {player_id} rolled a 6! Extra turn!")

def main():
    while True:
        try:
            num_players_input = input("Enter number of players (minimum 2): ")
            num_players = int(num_players_input)
            if num_players >= 2:
                break
            else:
                print("Invalid number of players. Please enter 2 or more.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    game = SnakesLaddersGame(num_players)
    game.run_game()

if __name__ == "__main__":
    main()
