import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter.simpledialog import askinteger
import random

class Domino:
    def __init__(self, side1, side2):
        self.sides = tuple(sorted((side1, side2)))

    def __str__(self):
        return f"[{self.sides[0]}|{self.sides[1]}]"

    def __repr__(self):
        return self.__str__()

    def is_double(self):
        return self.sides[0] == self.sides[1]

    def get_ends(self):
        return self.sides[0], self.sides[1]

class DominoGame:
    def __init__(self, num_players=2, max_pips=6, logger=None):
        if not (2 <= num_players <= 4):
            raise ValueError("Number of players must be between 2 and 4.")
        self.num_players = num_players
        self.max_pips = max_pips
        self.logger = logger if logger else print

        self.boneyard = self._create_dominoes()
        self.players = [[] for _ in range(self.num_players)]
        self.table = []
        self.current_player_index = 0
        self.game_over = False
        self.consecutive_passes = 0

    def _create_dominoes(self):
        dominoes = []
        for i in range(self.max_pips + 1):
            for j in range(i, self.max_pips + 1):
                dominoes.append(Domino(i, j))
        random.shuffle(dominoes)
        return dominoes

    def _deal_dominoes(self):
        num_to_deal = 7 if self.num_players == 2 else 5
        for i in range(self.num_players):
            for _ in range(num_to_deal):
                if not self.boneyard:
                    self.logger("Warning: Boneyard empty during dealing, not all players received full hand.")
                    break
                self.players[i].append(self.boneyard.pop(0))

    def _determine_first_player(self):
        starting_tile = None
        player_with_starting_tile = -1
        highest_double_value = -1

        candidates = []
        for p_idx, hand in enumerate(self.players):
            for domino in hand:
                if domino.is_double():
                    if domino.sides[0] > highest_double_value:
                        highest_double_value = domino.sides[0]
                        starting_tile = domino
                        player_with_starting_tile = p_idx
                        candidates = [(p_idx, domino)]
                    elif domino.sides[0] == highest_double_value:
                        candidates.append((p_idx, domino))

        if candidates:
            best_player_idx, best_domino = sorted(candidates, key=lambda x: x[0])[0]
            starting_tile = best_domino
            player_with_starting_tile = best_player_idx

            self.logger(f"Player {player_with_starting_tile + 1} has the highest double ({starting_tile}) and plays first.")
            self.current_player_index = player_with_starting_tile
            self.players[player_with_starting_tile].remove(starting_tile)
            self.table.append(starting_tile)
        else:
            self.current_player_index = random.randint(0, self.num_players - 1)
            if not self.players[self.current_player_index]:
                self.logger("Error: Player hand empty during first player determination. Dealing might have failed.")
                self.game_over = True
                return

            starting_tile = self.players[self.current_player_index].pop(0)
            self.table.append(starting_tile)
            self.logger(f"No doubles among players. Player {self.current_player_index + 1} plays the first domino: {starting_tile}.")

    def start_game(self, num_players):
        self.game_over = False
        self.consecutive_passes = 0
        self.num_players = num_players # Update num_players if starting a new game
        self.boneyard = self._create_dominoes()
        self.players = [[] for _ in range(self.num_players)]
        self.table = []
        
        self._deal_dominoes()
        self._determine_first_player()
        if self.game_over:
            self.logger("Game could not start due to an error during first player determination.")
            return

        self.logger("\n--- Game Started ---")

    def _get_table_ends(self):
        if not self.table:
            return None, None
        
        left_end = self.table[0].sides[0]
        right_end = self.table[-1].sides[1]
        
        return left_end, right_end

    def get_playable_dominoes(self, player_hand):
        playable_moves = [] # (domino_index_in_hand, side_to_attach, pip_to_match)
        left_end, right_end = self._get_table_ends()

        if not self.table: # Should only happen for the very first tile played by _determine_first_player
            # This path is mainly for robustness if called early, but interactive play will be on existing table.
            for i, domino in enumerate(player_hand):
                playable_moves.append((i, 'start', None)) # 'start' signifies initial placement
            return playable_moves

        for i, domino in enumerate(player_hand):
            d_side1, d_side2 = domino.get_ends()
            
            if d_side1 == left_end:
                playable_moves.append((i, 'left', d_side1))
            if d_side2 == left_end:
                playable_moves.append((i, 'left', d_side2))
            
            if d_side1 == right_end:
                playable_moves.append((i, 'right', d_side1))
            if d_side2 == right_end:
                playable_moves.append((i, 'right', d_side2))
        
        return playable_moves

    def play_domino(self, player_index, domino_index_in_hand, side_to_attach):
        player_hand = self.players[player_index]
        
        if not (0 <= domino_index_in_hand < len(player_hand)):
            self.logger("Error: Invalid domino index received by play_domino function.")
            return False

        domino_to_play = player_hand[domino_index_in_hand]
        d1, d2 = domino_to_play.get_ends()

        if not self.table: # This branch is mostly handled by _determine_first_player
            self.table.append(domino_to_play)
            player_hand.pop(domino_index_in_hand)
            self.logger(f"Player {player_index + 1} played {domino_to_play} to start the game.")
            return True

        left_end, right_end = self._get_table_ends()
        valid_move = False
        
        if side_to_attach == 'left':
            if d1 == left_end:
                self.table.insert(0, domino_to_play)
                valid_move = True
            elif d2 == left_end:
                self.table.insert(0, Domino(d2, d1))
                valid_move = True
        elif side_to_attach == 'right':
            if d1 == right_end:
                self.table.append(domino_to_play)
                valid_move = True
            elif d2 == right_end:
                self.table.append(Domino(d2, d1))
                valid_move = True
        
        if valid_move:
            player_hand.pop(domino_index_in_hand)
            self.logger(f"Player {player_index + 1} played {domino_to_play} on the {side_to_attach} end.")
            self.consecutive_passes = 0
            return True
        else:
            self.logger(f"Internal Error: Failed to play {domino_to_play} on {side_to_attach} end. Does not match {left_end}/{right_end}.")
            return False

    def draw_from_boneyard(self, player_index):
        if not self.boneyard:
            self.logger("Boneyard is empty. Cannot draw.")
            return None
        drawn_domino = self.boneyard.pop(0)
        self.players[player_index].append(drawn_domino)
        self.logger(f"Player {player_index + 1} drew {drawn_domino} from the boneyard.")
        return drawn_domino

    def check_for_winner(self):
        if not self.players[self.current_player_index]:
            self.game_over = True
            self.logger(f"\n--- Player {self.current_player_index + 1} wins the round! ---")
            return True
        return False

    def _handle_blocked_game(self):
        self.logger("\n--- Game Blocked! No player can make a move. ---")
        min_pips = float('inf')
        winner_player_index = -1
        
        pip_counts = []
        for p_idx, hand in enumerate(self.players):
            current_pips = sum(d.sides[0] + d.sides[1] for d in hand)
            pip_counts.append((current_pips, p_idx))
            self.logger(f"Player {p_idx + 1} hand: {hand} (Total pips: {current_pips})")

        sorted_pip_counts = sorted(pip_counts, key=lambda x: x[0])
        min_pips = sorted_pip_counts[0][0]
        
        tied_players = [p_idx for pips, p_idx in sorted_pip_counts if pips == min_pips]

        if len(tied_players) > 1:
            tied_player_nums = [idx + 1 for idx in tied_players]
            self.logger(f"It's a tie among players {tied_player_nums} with {min_pips} pips.")
            winner_player_index = tied_players[0]
        else:
            winner_player_index = sorted_pip_counts[0][1]
            self.logger(f"Player {winner_player_index + 1} wins the round with the lowest pip count of {min_pips}!")
        
        self.game_over = True

    def _next_player_turn(self):
        self.current_player_index = (self.current_player_index + 1) % self.num_players

class DominoGUI:
    def __init__(self, master):
        self.master = master
        master.title("Domino Game")

        self.game = None # Game object will be initialized on new game start
        self.current_selected_domino_idx = None # Store index of selected domino in player's hand

        # --- GUI Elements ---
        # Log Text Area
        self.log_area = scrolledtext.ScrolledText(master, width=80, height=20, state='disabled')
        self.log_area.pack(pady=10)

        # Game State Labels
        self.table_label = tk.Label(master, text="Table: ")
        self.table_label.pack()
        self.ends_label = tk.Label(master, text="Open ends: ")
        self.ends_label.pack()
        self.boneyard_label = tk.Label(master, text="Boneyard: ")
        self.boneyard_label.pack()

        # Player Hand Display Frame
        self.hand_label = tk.Label(master, text="Your hand (Player X): ")
        self.hand_label.pack(pady=(10,0))
        self.domino_buttons_frame = tk.Frame(master)
        self.domino_buttons_frame.pack(pady=(0,5))

        # Play Controls Frame
        self.play_controls_frame = tk.Frame(master)
        self.play_controls_frame.pack(pady=5)
        self.side_buttons_frame = tk.Frame(self.play_controls_frame)
        self.side_buttons_frame.pack()
        
        self.pass_button = tk.Button(self.play_controls_frame, text="Pass Turn (No moves/Boneyard empty)", command=self.on_pass_turn, state=tk.DISABLED)
        self.pass_button.pack(pady=5)

        # New Game Button
        self.new_game_button = tk.Button(master, text="New Game", command=self.start_new_game_dialog)
        self.new_game_button.pack(pady=10)

        self.start_new_game_dialog() # Prompt for new game on startup

    def _log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def start_new_game_dialog(self):
        num_players = askinteger("New Game", "Enter number of players (2-4):", parent=self.master, minvalue=2, maxvalue=4)
        if num_players is not None:
            self.game = DominoGame(num_players=num_players, logger=self._log)
            self.game.start_game(num_players) # Pass num_players to start_game
            self.update_gui_display()
            self.master.after(100, self.process_current_turn) # Small delay before processing turn

    def update_gui_display(self):
        if not self.game: return # Game not started yet

        self.table_label.config(text=f"Table: {self.game.table}")
        left_end, right_end = self.game._get_table_ends()
        self.ends_label.config(text=f"Open ends: {left_end} | {right_end}")
        self.boneyard_label.config(text=f"Boneyard: {len(self.game.boneyard)} dominoes.")
        self.display_player_hand()

    def display_player_hand(self):
        for widget in self.domino_buttons_frame.winfo_children():
            widget.destroy()
        
        current_player_hand = self.game.players[self.game.current_player_index]
        self.hand_label.config(text=f"Your hand (Player {self.game.current_player_index + 1}): ")

        playable_moves = self.game.get_playable_dominoes(current_player_hand)
        playable_domino_indices = {move[0] for move in playable_moves}

        for i, domino in enumerate(current_player_hand):
            button_text = str(domino)
            button_state = tk.NORMAL if i in playable_domino_indices else tk.DISABLED
            
            button = tk.Button(self.domino_buttons_frame, text=button_text, 
                               command=lambda d_idx=i: self.on_domino_selected(d_idx),
                               state=button_state)
            button.pack(side=tk.LEFT, padx=2)
        
        self.clear_side_buttons()
        # Enable/disable pass button based on whether there are playable moves in hand
        self.pass_button.config(state=tk.NORMAL if not playable_moves and not self.game.boneyard else tk.DISABLED)


    def clear_side_buttons(self):
        for widget in self.side_buttons_frame.winfo_children():
            widget.destroy()

    def on_domino_selected(self, domino_index_in_hand):
        self.current_selected_domino_idx = domino_index_in_hand
        self.clear_side_buttons()

        selected_domino = self.game.players[self.game.current_player_index][domino_index_in_hand]
        left_end, right_end = self.game._get_table_ends()
        d_side1, d_side2 = selected_domino.get_ends()

        playable_on_left = (d_side1 == left_end) or (d_side2 == left_end)
        playable_on_right = (d_side1 == right_end) or (d_side2 == right_end)

        # For the very first move of the game, _determine_first_player automatically plays a domino.
        # So this branch for 'start' shouldn't be reached by interactive player input after initial setup.
        # But keeping it robust for potential alternative game starts.
        if not self.game.table: # Should not be the case for player input after game start
             messagebox.showerror("Error", "Game has not started or table is empty. This shouldn't happen.")
             self.current_selected_domino_idx = None
             return

        if playable_on_left:
            left_button = tk.Button(self.side_buttons_frame, text=f"Play {selected_domino} on LEFT", 
                                    command=lambda: self.on_play_move('left'))
            left_button.pack(side=tk.LEFT, padx=5)
        if playable_on_right:
            right_button = tk.Button(self.side_buttons_frame, text=f"Play {selected_domino} on RIGHT", 
                                     command=lambda: self.on_play_move('right'))
            right_button.pack(side=tk.LEFT, padx=5)
        
        if not playable_on_left and not playable_on_right:
            messagebox.showerror("Invalid Selection", f"{selected_domino} cannot be played on either end.")
            self.current_selected_domino_idx = None
            self.display_player_hand()

    def on_play_move(self, side_to_attach):
        if self.current_selected_domino_idx is None:
            messagebox.showerror("Error", "Please select a domino from your hand first.")
            return

        # Play the domino
        if self.game.play_domino(self.game.current_player_index, self.current_selected_domino_idx, side_to_attach):
            self.current_selected_domino_idx = None
            self.update_gui_display()
            if self.game.check_for_winner():
                messagebox.showinfo("Game Over", f"Player {self.game.current_player_index + 1} wins the round!")
            else:
                self.game._next_player_turn()
                self.process_current_turn()
        else:
            messagebox.showerror("Invalid Move", "This move is not possible. Please try again.")
            self.current_selected_domino_idx = None
            self.update_gui_display() # Re-enable correct buttons


    def on_pass_turn(self):
        if self.game.boneyard: # Player cannot pass if boneyard isn't empty
            messagebox.showerror("Invalid Pass", "You must draw from the boneyard if you have no playable moves.")
            return
        
        current_player_hand = self.game.players[self.game.current_player_index]
        playable_moves = self.game.get_playable_dominoes(current_player_hand)
        
        if playable_moves: # Player cannot pass if they have playable moves
            messagebox.showerror("Invalid Pass", "You have playable dominoes. You cannot pass.")
            return

        self._log(f"Player {self.game.current_player_index + 1} passed turn.")
        self.game.consecutive_passes += 1

        if self.game.consecutive_passes >= self.game.num_players:
            self.game._handle_blocked_game()
            messagebox.showinfo("Game Over", "The game is blocked!")
        
        if not self.game.game_over:
            self.game._next_player_turn()
            self.master.after(100, self.process_current_turn) # Continue to next turn

    def process_current_turn(self):
        if self.game.game_over:
            return

        current_player_hand = self.game.players[self.game.current_player_index]
        playable_moves = self.game.get_playable_dominoes(current_player_hand)

        self.update_gui_display() # Update display for new player's turn

        if not playable_moves:
            self._log("No playable dominoes in hand for Player " + str(self.game.current_player_index + 1) + ".")
            if self.game.boneyard:
                self._log("Drawing from boneyard...")
                # Simulate drawing until a move is possible or boneyard is empty
                drawn_count = 0
                while not playable_moves and self.game.boneyard:
                    drawn_domino = self.game.draw_from_boneyard(self.game.current_player_index)
                    if drawn_domino:
                        drawn_count += 1
                        playable_moves = self.game.get_playable_dominoes(current_player_hand)
                    else:
                        break # Boneyard truly empty

                if not playable_moves:
                    self._log("No playable dominoes after drawing.")
                    self._log("Passing turn for Player " + str(self.game.current_player_index + 1) + ".")
                    self.game.consecutive_passes += 1
                else:
                    self._log(f"Drew {drawn_count} domino(es) and now Player {self.game.current_player_index + 1} has playable moves.")
                    self.game.consecutive_passes = 0 # Reset passes after a draw that leads to a move
                
                self.update_gui_display() # Update hand after drawing

            else: # Boneyard is empty
                self._log("Boneyard is empty. No playable dominoes. Passing turn for Player " + str(self.game.current_player_index + 1) + ".")
                self.game.consecutive_passes += 1

            if self.game.consecutive_passes >= self.game.num_players:
                self.game._handle_blocked_game()
                messagebox.showinfo("Game Over", "The game is blocked!")
                return # End game since it's blocked

            if not self.game.game_over:
                self.game._next_player_turn()
                self.master.after(500, self.process_current_turn) # Delay for next player's turn (simulate AI/other players)
        else:
            self.game.consecutive_passes = 0
            # If playable moves exist, GUI waits for human interaction via buttons.
            # No `after` call needed here, as the turn is active for human input.

def main():
    root = tk.Tk()
    app = DominoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
