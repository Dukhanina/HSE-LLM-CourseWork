import random
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog

class MemoryGame:
    def __init__(self, pairs=8, gui_app=None):
        self.gui_app = gui_app
        self.cards = self._create_cards(pairs)
        self.board = ['*' for _ in range(len(self.cards))]
        self.matched_pairs = 0
        self.player_scores = {}
        self.current_player_index = 0
        self.players = []
        self.flipped_cards = []

    def _create_cards(self, pairs):
        values = [str(i) for i in range(1, pairs + 1)]
        cards = (values * 2)
        random.shuffle(cards)
        return cards

    def add_player(self, player_name):
        self.players.append(player_name)
        self.player_scores[player_name] = 0

    def display_board(self):
        self.gui_app.update_board_display(self.board)

    def is_game_over(self):
        return self.matched_pairs == len(self.cards) // 2

    def get_current_player(self):
        return self.players[self.current_player_index]

    def switch_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def flip_card(self, index):
        if not (0 <= index < len(self.cards)):
            self.gui_app.show_error("Invalid index. Please enter a number within the board range.")
            return False
        if self.board[index] != '*':
            self.gui_app.show_error("This card is already matched or flipped. Choose another.")
            return False
        if index in self.flipped_cards:
            self.gui_app.show_error("You already selected this card. Choose a different one.")
            return False

        self.board[index] = self.cards[index]
        self.flipped_cards.append(index)
        self.display_board()

        if len(self.flipped_cards) == 2:
            self.gui_app.master.after(1000, self.check_match)
        return True

    def check_match(self):
        index1, index2 = self.flipped_cards[0], self.flipped_cards[1]
        player_name = self.get_current_player()

        if self.cards[index1] == self.cards[index2]:
            self.gui_app.log_message("Match found!")
            self.matched_pairs += 1
            self.player_scores[player_name] += 1
            self.gui_app.update_game_state()
            if self.is_game_over():
                self.gui_app.end_game()
            else:
                self.gui_app.log_message(f"{player_name} gets another turn.")
                self.gui_app.current_player_label.config(text=f"Current Player: {player_name}")
        else:
            self.gui_app.log_message("No match. Cards will be flipped back.")
            self.board[index1] = '*'
            self.board[index2] = '*'
            self.switch_player()
            self.gui_app.current_player_label.config(text=f"Current Player: {self.get_current_player()}")
            self.display_board()
        self.flipped_cards = []
        self.gui_app.enable_player_input()
        self.gui_app.log_message(f"Current Player: {self.get_current_player()}")


    def determine_winner(self):
        if not self.player_scores:
            self.gui_app.log_message("No players in the game.")
            return

        highest_score = -1
        winners = []

        for player, score in self.player_scores.items():
            if score > highest_score:
                highest_score = score
                winners = [player]
            elif score == highest_score:
                winners.append(player)

        if highest_score == 0:
            self.gui_app.log_message("No pairs were matched. It's a draw!")
        elif len(winners) > 1:
            self.gui_app.log_message(f"It's a tie! Winners: {', '.join(winners)} with {highest_score} pairs.")
        else:
            self.gui_app.log_message(f"The winner is {winners[0]} with {highest_score} pairs!")

class MemoryGUI:
    def __init__(self, master):
        self.master = master
        master.title("Memory Game")

        self.game = None
        self.player_names = ["Player 1", "Player 2"] # Default players

        # Widgets
        self.log_text = scrolledtext.ScrolledText(master, state='disabled', width=60, height=15)
        self.log_text.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

        self.board_frame = tk.Frame(master, borderwidth=2, relief="groove")
        self.board_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=5)
        self.card_buttons = []

        self.current_player_label = tk.Label(master, text="Current Player:")
        self.current_player_label.grid(row=2, column=0, columnspan=4)

        self.input_frame = tk.LabelFrame(master, text="Enter Card Index")
        self.input_frame.grid(row=3, column=0, columnspan=4, padx=5, pady=5)

        self.index_entry = tk.Entry(self.input_frame, width=10)
        self.index_entry.grid(row=0, column=0, padx=2, pady=2)
        self.flip_button = tk.Button(self.input_frame, text="Flip Card", command=self.process_flip)
        self.flip_button.grid(row=0, column=1, padx=2, pady=2)

        self.new_game_button = tk.Button(master, text="New Game", command=self.start_new_game)
        self.new_game_button.grid(row=4, column=0, columnspan=4, pady=5)

        self.disable_player_input()

    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def update_board_display(self, board):
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        cols = 4 # Or another suitable number for layout
        for i, card_value in enumerate(board):
            button = tk.Button(self.board_frame, text=card_value, width=5, height=2,
                               command=lambda idx=i: self.on_card_click(idx))
            button.grid(row=i // cols, column=i % cols, padx=2, pady=2)
            self.card_buttons.append(button)
            if card_value != '*': # If card is revealed (matched), disable button
                button.config(state=tk.DISABLED)

    def update_game_state(self):
        if self.game:
            self.log_text.config(state='normal')
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state='disabled')
            self.log_message("--- Game State ---")
            for player, score in self.game.player_scores.items():
                self.log_message(f"{player}: {score} pairs")
            self.log_message("------------------")
            self.update_board_display(self.game.board)

    def disable_player_input(self):
        self.index_entry.config(state=tk.DISABLED)
        self.flip_button.config(state=tk.DISABLED)

    def enable_player_input(self):
        self.index_entry.config(state=tk.NORMAL)
        self.flip_button.config(state=tk.NORMAL)

    def start_new_game(self):
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        self.log_message("Starting a new game...")

        num_pairs = 8 # Default number of pairs
        try:
            num_players_str = tk.simpledialog.askstring("Number of Players", "Enter number of players (1-5):")
            if num_players_str is None: # User cancelled
                self.log_message("Game setup cancelled.")
                return
            num_players = int(num_players_str)
            if not (1 <= num_players <= 5):
                raise ValueError("Number of players must be between 1 and 5.")
        except ValueError as e:
            self.show_error(f"Invalid number of players: {e}. Defaulting to 2 players.")
            num_players = 2

        self.player_names = [f"Player {i+1}" for i in range(num_players)] # Simple player names for GUI example

        self.game = MemoryGame(pairs=num_pairs, gui_app=self)
        for name in self.player_names:
            self.game.add_player(name)

        self.game.display_board()
        self.log_message("Instructions:")
        self.log_message("Flip two cards by entering their indices.")
        self.log_message("If they match, you score a point and get another turn.")
        self.log_message("If not, they flip back and it's the next player's turn.")
        self.log_message(f"Current Player: {self.game.get_current_player()}")
        
        self.new_game_button.config(state=tk.DISABLED)
        self.enable_player_input()
        self.update_game_state()

    def process_flip(self):
        try:
            index_str = self.index_entry.get()
            index = int(index_str)
            if self.game.flip_card(index):
                self.index_entry.delete(0, tk.END)
                # Disable input while cards are being checked for a match
                if len(self.game.flipped_cards) == 2:
                    self.disable_player_input()
            
        except ValueError:
            self.show_error("Invalid input. Please enter a number.")
        except Exception as e:
            self.show_error(f"An error occurred: {e}")

    def on_card_click(self, index):
        # This allows clicking on the card buttons directly
        if self.game and len(self.game.flipped_cards) < 2:
            if self.game.flip_card(index):
                if len(self.game.flipped_cards) == 2:
                    self.disable_player_input()

    def end_game(self):
        self.log_message("\nGame Over!")
        self.game.determine_winner()
        self.new_game_button.config(state=tk.NORMAL)
        self.disable_player_input()

def main():
    root = tk.Tk()
    gui = MemoryGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
