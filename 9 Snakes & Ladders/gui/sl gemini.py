import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter.simpledialog import askinteger
import random

class SnakesLaddersGame:
    def __init__(self, num_players=2, logger=None):
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
        self.logger = logger if logger else print
        self.player_positions = [1] * num_players
        self.current_player_idx = 0
        self.game_over = False

    def reset_game(self, num_players):
        self.num_players = num_players
        self.player_positions = [1] * num_players
        self.current_player_idx = 0
        self.game_over = False
        self.logger("Game reset.")

    def roll_dice(self):
        return random.randint(1, 6)

    def _get_initial_player_order(self):
        roll_results = []
        self.logger("Rolling to determine turn order...")
        for i in range(self.num_players):
            roll = self.roll_dice()
            self.logger(f"Player {i+1} rolled a {roll}.")
            roll_results.append({'player_idx': i, 'roll': roll})
        
        # Simple tie-breaking: highest roll wins, first among ties
        roll_results.sort(key=lambda x: x['roll'], reverse=True)
        self.current_player_idx = roll_results[0]['player_idx']
        self.logger(f"Player {self.current_player_idx+1} goes first!")
        return True # Indicates initial roll-off is done

    def move_player(self, player_idx, steps):
        current_pos = self.player_positions[player_idx]
        new_pos = current_pos + steps

        if new_pos > self.BOARD_SIZE:
            new_pos = self.BOARD_SIZE - (new_pos - self.BOARD_SIZE)
            self.logger(f"Bounced back to {new_pos}.")
        
        self.logger(f"Player {player_idx+1} moved from {current_pos} to {new_pos}.")

        if new_pos in self.LADDERS:
            self.logger(f"Wow! Player {player_idx+1} found a ladder from {new_pos} to {self.LADDERS[new_pos]}!")
            new_pos = self.LADDERS[new_pos]
        elif new_pos in self.SNAKES:
            self.logger(f"Oh no! Player {player_idx+1} hit a snake from {new_pos} to {self.SNAKES[new_pos]}!")
            new_pos = self.SNAKES[new_pos]
        
        self.player_positions[player_idx] = new_pos
        self.logger(f"Player {player_idx+1} is now at square {new_pos}.")
        
        if new_pos == self.BOARD_SIZE:
            self.game_over = True
            self.logger(f"Player {player_idx+1} reached square {self.BOARD_SIZE}!")
            return True # Player won
        return False # Player did not win

    def _next_player_turn(self):
        self.current_player_idx = (self.current_player_idx + 1) % self.num_players


class SnakesLaddersGUI:
    def __init__(self, master):
        self.master = master
        master.title("Snakes & Ladders")

        self.game = None
        self.current_roll = 0
        self.initial_turn_determination_phase = True

        self.log_area = scrolledtext.ScrolledText(master, width=80, height=15, state='disabled')
        self.log_area.pack(pady=10)

        self.board_display_label = tk.Label(master, text="Board State:")
        self.board_display_label.pack()
        self.board_value_label = tk.Label(master, text="", font=("Arial", 12))
        self.board_value_label.pack(pady=5)

        self.current_player_label = tk.Label(master, text="Current Player: -")
        self.current_player_label.pack(pady=5)
        self.dice_roll_label = tk.Label(master, text="Last Roll: -")
        self.dice_roll_label.pack(pady=5)

        self.controls_frame = tk.Frame(master)
        self.controls_frame.pack(pady=10)

        self.roll_button = tk.Button(self.controls_frame, text="Roll Dice", command=self.on_roll_dice)
        self.roll_button.pack(side=tk.LEFT, padx=5)
        
        self.new_game_button = tk.Button(master, text="New Game", command=self.start_new_game_dialog)
        self.new_game_button.pack(pady=10)
        
        self.set_controls_state(False)
        self.start_new_game_dialog()

    def _log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def start_new_game_dialog(self):
        num_players = askinteger("New Game", "Enter number of players (minimum 2):", parent=self.master, minvalue=2, maxvalue=6) # Max 6 for practical purposes
        if num_players is not None:
            if self.game:
                self.game.reset_game(num_players)
            else:
                self.game = SnakesLaddersGame(num_players=num_players, logger=self._log)
            self.initial_turn_determination_phase = True
            self.update_gui_display()
            self.set_controls_state(True)
            self._log(f"New game started with {num_players} players.")
            self._determine_first_player_gui()

    def _determine_first_player_gui(self):
        if not self.game: return

        self.master.after(100, self._roll_for_initial_turn)

    def _roll_for_initial_turn(self):
        if not self.initial_turn_determination_phase:
            return

        # Simplified initial roll-off for GUI: each player rolls once, highest takes first turn.
        # No re-rolls for ties for simplicity, first among ties gets turn.
        roll = self.game.roll_dice()
        player_id = self.game.current_player_idx + 1
        self._log(f"Player {player_id} rolled {roll} for turn order.")

        if not hasattr(self, '_initial_rolls'):
            self._initial_rolls = []
        self._initial_rolls.append({'player_idx': self.game.current_player_idx, 'roll': roll})

        self.game._next_player_turn()

        if len(self._initial_rolls) < self.game.num_players:
            self.master.after(1000, self._roll_for_initial_turn) # Wait a bit then roll for next player
        else:
            self._initial_rolls.sort(key=lambda x: x['roll'], reverse=True)
            self.game.current_player_idx = self._initial_rolls[0]['player_idx']
            self._log(f"Player {self.game.current_player_idx+1} goes first!")
            self.initial_turn_determination_phase = False
            del self._initial_rolls
            self.process_current_turn()

    def update_gui_display(self):
        if not self.game: return

        board_state_text = ""
        for i, pos in enumerate(self.game.player_positions):
            board_state_text += f"P{i+1}: {pos} "
        self.board_value_label.config(text=board_state_text.strip())

        player_id = self.game.current_player_idx + 1
        self.current_player_label.config(text=f"Current Player: {player_id}")
        self.dice_roll_label.config(text=f"Last Roll: {self.current_roll}")
        
        if self.game.game_over:
            self.set_controls_state(False)
            messagebox.showinfo("Game Over", f"Player {player_id} wins!")

    def set_controls_state(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.roll_button.config(state=state)

    def process_current_turn(self):
        if self.game.game_over: return
        self.update_gui_display()
        self.set_controls_state(True)
        player_id = self.game.current_player_idx + 1
        self._log(f"\nPlayer {player_id}'s turn. Roll the dice.")

    def on_roll_dice(self):
        if self.game.game_over: return
        
        self.current_roll = self.game.roll_dice()
        player_id = self.game.current_player_idx + 1
        self._log(f"Player {player_id} rolled a {self.current_roll}.")
        self.dice_roll_label.config(text=f"Last Roll: {self.current_roll}")

        player_won = self.game.move_player(self.game.current_player_idx, self.current_roll)
        
        self.update_gui_display()

        if player_won:
            self.set_controls_state(False)
        elif self.current_roll != 6:
            self.game._next_player_turn()
            self.master.after(1000, self.process_current_turn) # Schedule next turn after a delay
        else:
            self._log(f"Player {player_id} rolled a 6! Extra turn!")
            self.master.after(1000, self.process_current_turn) # Schedule current player's next turn

def main():
    root = tk.Tk()
    app = SnakesLaddersGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
