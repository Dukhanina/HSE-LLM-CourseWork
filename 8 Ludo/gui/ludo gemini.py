import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter.simpledialog import askinteger
import random

class LudoGame:
    def __init__(self, num_players=2, logger=None):
        if num_players not in [2, 4]:
            raise ValueError("Number of players must be 2 or 4.")
        self.num_players = num_players
        self.logger = logger if logger else print
        self.players = []
        self.current_player_idx = 0
        self.game_over = False
        self.consecutive_sixes = 0

        self.TRACK_LENGTH = 52
        self.HOME_PATH_LENGTH = 6
        self.PAWNS_PER_PLAYER = 4

        self.PLAYER_START_POS = [0, 13, 26, 39]
        self.PLAYER_HOME_ENTRY_POS = [51, 12, 25, 38]
        
        self.FIXED_SAFE_ZONES = set([
            0, 13, 26, 39,
            8, 21, 34, 47
        ])
        
        self._init_players()

    def _init_players(self):
        self.players = [] # Reset players for new game
        for p_idx in range(self.num_players):
            player_pawns = []
            for i in range(self.PAWNS_PER_PLAYER):
                player_pawns.append({'id': i, 'state': 'nest', 'position': -1, 'player_idx': p_idx})
            self.players.append(player_pawns)
        self.current_player_idx = 0
        self.game_over = False
        self.consecutive_sixes = 0

    def roll_dice(self):
        return random.randint(1, 6)

    def _is_safe_position(self, global_pos):
        if global_pos in self.FIXED_SAFE_ZONES:
            return True
        
        pawns_on_square = []
        for p_idx in range(self.num_players):
            for pawn in self.players[p_idx]:
                if pawn['state'] == 'track' and pawn['position'] == global_pos:
                    pawns_on_square.append(pawn)
        
        if len(pawns_on_square) >= 2:
            first_pawn_owner = pawns_on_square[0]['player_idx']
            if all(pawn['player_idx'] == first_pawn_owner for pawn in pawns_on_square):
                return True
            
        return False

    def get_possible_moves(self, player_idx, roll):
        possible_moves = []
        player_pawns = self.players[player_idx]

        for pawn in player_pawns:
            if pawn['state'] == 'nest':
                if roll == 6:
                    target_pos = self.PLAYER_START_POS[player_idx]
                    
                    pawns_on_target = [
                        p for p_list in self.players 
                        for p in p_list if p['state'] == 'track' and p['position'] == target_pos
                    ]
                    
                    if not (len(pawns_on_target) >= 2 and len(set(p['player_idx'] for p in pawns_on_target)) == 1):
                        possible_moves.append((pawn['id'], 'open', target_pos))
            
            elif pawn['state'] == 'track':
                current_pos = pawn['position']
                player_home_entry = self.PLAYER_HOME_ENTRY_POS[player_idx]
                
                dist_to_home_entry_from_current = (player_home_entry - current_pos + self.TRACK_LENGTH) % self.TRACK_LENGTH
                
                if roll <= dist_to_home_entry_from_current:
                    target_pos = (current_pos + roll) % self.TRACK_LENGTH
                    
                    pawns_on_target = [
                        p for p_list in self.players 
                        for p in p_list if p['state'] == 'track' and p['position'] == target_pos
                    ]
                    if not (len(pawns_on_target) >= 2 and len(set(p['player_idx'] for p in pawns_on_target)) == 1):
                         possible_moves.append((pawn['id'], 'move_on_track', target_pos))
                else:
                    steps_past_entry = roll - dist_to_home_entry_from_current
                    if steps_past_entry <= self.HOME_PATH_LENGTH:
                        target_home_path_idx = steps_past_entry - 1
                        
                        if target_home_path_idx == self.HOME_PATH_LENGTH - 1:
                            possible_moves.append((pawn['id'], 'finish', None))
                        else:
                            possible_moves.append((pawn['id'], 'move_home_path', target_home_path_idx))

            elif pawn['state'] == 'home_path':
                current_home_path_idx = pawn['position']
                remaining_steps = self.HOME_PATH_LENGTH - 1 - current_home_path_idx
                if roll <= remaining_steps:
                    target_home_path_idx = current_home_path_idx + roll
                    if target_home_path_idx == self.HOME_PATH_LENGTH - 1:
                        possible_moves.append((pawn['id'], 'finish', None))
                    else:
                        possible_moves.append((pawn['id'], 'move_home_path', target_home_path_idx))
        
        return possible_moves

    def execute_move(self, player_idx, pawn_id, roll, move_type, target_pos_info):
        pawn = self.players[player_idx][pawn_id]

        if move_type == 'open':
            target_global_pos = self.PLAYER_START_POS[player_idx]
            
            for opp_idx in range(self.num_players):
                if opp_idx == player_idx: continue
                for opp_pawn in self.players[opp_idx]:
                    if opp_pawn['state'] == 'track' and opp_pawn['position'] == target_global_pos:
                        if not self._is_safe_position(target_global_pos):
                            opp_pawn['state'] = 'nest'
                            opp_pawn['position'] = -1
                            self.logger(f"Pawn P{player_idx+1}_{pawn_id+1} captured opponent P{opp_idx+1}_{opp_pawn['id']+1}!")
                            break
            
            pawn['state'] = 'track'
            pawn['position'] = target_global_pos
            self.logger(f"Pawn P{player_idx+1}_{pawn_id+1} opened and moved to {target_global_pos}.")

        elif move_type == 'move_on_track':
            target_global_pos = target_pos_info
            
            for opp_idx in range(self.num_players):
                if opp_idx == player_idx: continue
                for opp_pawn in self.players[opp_idx]:
                    if opp_pawn['state'] == 'track' and opp_pawn['position'] == target_global_pos:
                        if not self._is_safe_position(target_global_pos):
                            opp_pawn['state'] = 'nest'
                            opp_pawn['position'] = -1
                            self.logger(f"Pawn P{player_idx+1}_{pawn_id+1} captured opponent P{opp_idx+1}_{opp_pawn['id']+1}!")
                            break
            
            pawn['state'] = 'track'
            pawn['position'] = target_global_pos
            self.logger(f"Pawn P{player_idx+1}_{pawn_id+1} moved to {target_global_pos}.")

        elif move_type == 'move_home_path':
            pawn['state'] = 'home_path'
            pawn['position'] = target_pos_info
            self.logger(f"Pawn P{player_idx+1}_{pawn_id+1} moved to home path position {target_pos_info+1}.")

        elif move_type == 'finish':
            pawn['state'] = 'finished'
            pawn['position'] = self.HOME_PATH_LENGTH - 1
            self.logger(f"Pawn P{player_idx+1}_{pawn_id+1} reached home!")
        
        self.check_winner()

    def check_winner(self):
        for p_idx, pawns in enumerate(self.players):
            if all(pawn['state'] == 'finished' for pawn in pawns):
                self.game_over = True
                self.logger(f"\n--- Player {p_idx+1} wins the game! ---")
                return True
        return False

    def _next_player_turn(self):
        self.current_player_idx = (self.current_player_idx + 1) % self.num_players

class LudoGUI:
    def __init__(self, master):
        self.master = master
        master.title("Ludo Game")

        self.game = None
        self.possible_moves = []
        self.last_roll = 0

        # GUI Elements
        self.log_area = scrolledtext.ScrolledText(master, width=80, height=20, state='disabled')
        self.log_area.pack(pady=10)

        self.board_display_frame = tk.Frame(master)
        self.board_display_frame.pack(pady=5)

        self.track_label = tk.Label(self.board_display_frame, text="Main Track:")
        self.track_label.pack()
        self.track_value_label = tk.Label(self.board_display_frame, text="")
        self.track_value_label.pack()

        self.player_info_labels = []
        for i in range(4): # Max 4 players
            frame = tk.Frame(self.board_display_frame)
            frame.pack()
            label = tk.Label(frame, text="")
            label.pack(side=tk.LEFT)
            self.player_info_labels.append(label)

        self.current_player_label = tk.Label(master, text="Current Player: -")
        self.current_player_label.pack(pady=5)
        self.dice_roll_label = tk.Label(master, text="Last Roll: -")
        self.dice_roll_label.pack(pady=5)

        self.controls_frame = tk.Frame(master)
        self.controls_frame.pack(pady=10)

        self.roll_button = tk.Button(self.controls_frame, text="Roll Dice", command=self.on_roll_dice)
        self.roll_button.pack(side=tk.LEFT, padx=5)

        self.pawn_choice_label = tk.Label(self.controls_frame, text="Choose Pawn (ID):")
        self.pawn_choice_label.pack(side=tk.LEFT, padx=5)
        self.pawn_choice_entry = tk.Entry(self.controls_frame, width=5)
        self.pawn_choice_entry.pack(side=tk.LEFT, padx=5)
        
        self.make_move_button = tk.Button(self.controls_frame, text="Make Move", command=self.on_make_move)
        self.make_move_button.pack(side=tk.LEFT, padx=5)
        
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
        num_players = askinteger("New Game", "Enter number of players (2 or 4):", parent=self.master, minvalue=2, maxvalue=4)
        if num_players is not None:
            self.game = LudoGame(num_players=num_players, logger=self._log)
            self.update_gui_display()
            self.set_controls_state(True)
            self._log(f"New game started with {num_players} players.")
            self.process_current_turn_phase1() # Start the first turn phase

    def update_gui_display(self):
        if not self.game: return

        player_symbols = {0: 'R', 1: 'G', 2: 'Y', 3: 'B'}
        
        track_display = ['_'] * self.game.TRACK_LENGTH
        for p_idx in range(self.game.num_players):
            for pawn in self.game.players[p_idx]:
                if pawn['state'] == 'track':
                    current_content = track_display[pawn['position']]
                    if current_content == '_':
                        track_display[pawn['position']] = player_symbols[p_idx]
                    elif player_symbols[p_idx] not in current_content:
                        track_display[pawn['position']] += player_symbols[p_idx]
        self.track_value_label.config(text=" ".join(track_display))

        for i in range(len(self.player_info_labels)):
            if i < self.game.num_players:
                p_idx = i
                nest_pawns = [p for p in self.game.players[p_idx] if p['state'] == 'nest']
                home_path_pawns = [p for p in self.game.players[p_idx] if p['state'] == 'home_path']
                finished_pawns = [p for p in self.game.players[p_idx] if p['state'] == 'finished']

                home_path_str = ['_'] * self.game.HOME_PATH_LENGTH
                for p in home_path_pawns:
                    home_path_str[p['position']] = player_symbols[p_idx]
                
                info_text = (f"Player {p_idx+1} ({player_symbols[p_idx]}): Nest={len(nest_pawns)} "
                             f"HomePath=[{' '.join(home_path_str)}] Finished={len(finished_pawns)}")
                self.player_info_labels[i].config(text=info_text)
            else:
                self.player_info_labels[i].config(text="") # Hide unused player labels

        self.current_player_label.config(text=f"Current Player: {self.game.current_player_idx+1} ({player_symbols[self.game.current_player_idx]})")
        self.dice_roll_label.config(text=f"Last Roll: {self.last_roll}")
        
        if self.game.game_over:
            self.set_controls_state(False)
            messagebox.showinfo("Game Over", f"Player {self.game.current_player_idx+1} wins!")


    def set_controls_state(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.roll_button.config(state=state)
        self.pawn_choice_entry.config(state=state)
        self.make_move_button.config(state=state)

    def process_current_turn_phase1(self):
        if self.game.game_over: return
        self.update_gui_display()
        self.set_controls_state(False) # Disable input while processing (or waiting for roll)
        self.roll_button.config(state=tk.NORMAL)
        self._log(f"\nPlayer {self.game.current_player_idx+1}'s turn. Roll the dice.")

    def on_roll_dice(self):
        if self.game.game_over: return
        self.last_roll = self.game.roll_dice()
        self._log(f"Player {self.game.current_player_idx+1} rolled a {self.last_roll}.")
        self.dice_roll_label.config(text=f"Last Roll: {self.last_roll}")

        if self.last_roll == 6:
            self.game.consecutive_sixes += 1
            if self.game.consecutive_sixes == 3:
                self._log(f"Player {self.game.current_player_idx+1} rolled three 6s! Turn lost.")
                self.game.consecutive_sixes = 0
                self.game._next_player_turn()
                self.master.after(500, self.process_current_turn_phase1) # Next player's turn
                return
        else:
            self.game.consecutive_sixes = 0

        self.possible_moves = self.game.get_possible_moves(self.game.current_player_idx, self.last_roll)

        if not self.possible_moves:
            self._log(f"No possible moves for Player {self.game.current_player_idx+1}. Passing turn.")
            if self.last_roll != 6:
                self.game._next_player_turn()
            self.master.after(500, self.process_current_turn_phase1)
        else:
            self._log("Possible moves:")
            for i, move in enumerate(self.possible_moves):
                pawn_id, move_type, target_pos_info = move
                pawn_desc = f"Pawn {pawn_id+1}"
                if move_type == 'open':
                    self._log(f"  {i}: {pawn_desc} from nest to start.")
                elif move_type == 'move_on_track':
                    self._log(f"  {i}: {pawn_desc} from {self.game.players[self.game.current_player_idx][pawn_id]['position']} to {target_pos_info} (on main track).")
                elif move_type == 'move_home_path':
                    self._log(f"  {i}: {pawn_desc} to home path position {target_pos_info+1}.")
                elif move_type == 'finish':
                    self._log(f"  {i}: {pawn_desc} to finish home.")
            
            self.set_controls_state(False) # Disable Roll button
            self.pawn_choice_entry.config(state=tk.NORMAL)
            self.make_move_button.config(state=tk.NORMAL)
            self.pawn_choice_entry.delete(0, tk.END)

    def on_make_move(self):
        if self.game.game_over: return
        
        try:
            choice_idx = int(self.pawn_choice_entry.get())
            if not (0 <= choice_idx < len(self.possible_moves)):
                messagebox.showerror("Invalid Move", "Invalid choice. Please enter a valid number for the move.")
                return
        except ValueError:
            messagebox.showerror("Invalid Input", "Invalid input. Please enter a number for your move choice.")
            return
        
        chosen_move = self.possible_moves[choice_idx]
        pawn_id, move_type, target_pos_info = chosen_move
        
        self.game.execute_move(self.game.current_player_idx, pawn_id, self.last_roll, move_type, target_pos_info)
        
        self.update_gui_display()

        if self.game.game_over:
            self.set_controls_state(False)
        else:
            if self.last_roll != 6:
                self.game._next_player_turn()
            self.master.after(500, self.process_current_turn_phase1) # Schedule next turn phase

def main():
    root = tk.Tk()
    app = LudoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
