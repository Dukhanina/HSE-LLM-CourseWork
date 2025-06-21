import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import random

class Player:
    __slots__ = ('id', 'color', 'pawns', 'start_pos', 'home_pos')
    def __init__(self, player_id, color, start_pos):
        self.id = player_id
        self.color = color
        self.pawns = [0] * 4
        self.start_pos = start_pos
        self.home_pos = (start_pos + 52) % 52

class LudoGame:
    def __init__(self, num_players=2):
        self.num_players = num_players
        self.players = []
        colors = ['red', 'green', 'blue', 'yellow']
        start_positions = [0, 13, 26, 39]
        for i in range(num_players):
            self.players.append(Player(i, colors[i], start_positions[i]))
        self.current_player = 0
        self.game_over = False
        self.consecutive_sixes = 0
        self.dice_value = 0
        self.last_move = ""
    
    def roll_dice(self):
        self.dice_value = random.randint(1, 6)
        return self.dice_value
    
    def get_absolute_position(self, player_id, steps):
        return (self.players[player_id].start_pos + steps) % 52
    
    def is_safe_zone(self, position):
        return position in [0, 8, 13, 21, 26, 34, 39, 47]
    
    def is_block(self, position):
        for player in self.players:
            count = 0
            for pawn in player.pawns:
                if pawn >= 52:
                    continue
                abs_pos = self.get_absolute_position(player.id, pawn)
                if abs_pos == position:
                    count += 1
            if count >= 2:
                return True
        return False
    
    def get_available_pawns(self, player_id, dice):
        available = []
        player = self.players[player_id]
        
        for idx, steps in enumerate(player.pawns):
            # Pawn is already home
            if steps == 57:
                continue
                
            new_steps = steps + dice
            
            # Can't move beyond home
            if new_steps > 57:
                continue
            
            # Entering home stretch
            if steps < 52 and new_steps >= 52:
                new_steps = 52 + (new_steps - 52)
            
            # Check if blocked
            if steps < 52 and new_steps < 52:
                new_pos = self.get_absolute_position(player_id, new_steps)
                if not self.is_safe_zone(new_pos) and self.is_block(new_pos):
                    continue
            
            available.append(idx)
        
        return available
    
    def move_pawn(self, player_id, pawn_idx, dice):
        player = self.players[player_id]
        old_steps = player.pawns[pawn_idx]
        new_steps = old_steps + dice
        captured = False
        
        # Validate move
        if new_steps > 57:
            return False, "Cannot move beyond home"
        
        # Handle home stretch
        if old_steps < 52 and new_steps >= 52:
            new_steps = 52 + (new_steps - 52)
        
        player.pawns[pawn_idx] = new_steps
        
        # Check for capture
        if old_steps < 52 and new_steps < 52:
            new_abs_pos = self.get_absolute_position(player_id, new_steps)
            
            if not self.is_safe_zone(new_abs_pos) and not self.is_block(new_abs_pos):
                for other_player in self.players:
                    if other_player.id == player_id:
                        continue
                    for other_idx, other_steps in enumerate(other_player.pawns):
                        if other_steps < 52:
                            other_abs = self.get_absolute_position(other_player.id, other_steps)
                            if other_abs == new_abs_pos:
                                other_player.pawns[other_idx] = 0
                                captured = True
                                self.last_move = f"Player {player_id} captured Player {other_player.id}'s pawn!"
                                break
        
        return True, captured
    
    def check_win(self, player_id):
        return all(steps == 57 for steps in self.players[player_id].pawns)
    
    def get_board_state(self):
        board = {}
        for player in self.players:
            for pawn_idx, steps in enumerate(player.pawns):
                if steps < 52:
                    pos = self.get_absolute_position(player.id, steps)
                    if pos not in board:
                        board[pos] = []
                    board[pos].append((player.id, pawn_idx))
        return board
    
    def next_player(self):
        self.current_player = (self.current_player + 1) % self.num_players
        self.consecutive_sixes = 0
        return self.current_player

class LudoGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ludo Game")
        self.root.geometry("800x600")
        
        # Game variables
        self.game = None
        self.pawn_imgs = {}
        self.canvas_items = {}
        
        # Create UI elements
        self.create_widgets()
        
        self.root.mainloop()
    
    def create_widgets(self):
        # Control frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(control_frame, text="New Game", command=self.start_new_game).pack(side=tk.LEFT)
        
        # Game info frame
        info_frame = tk.Frame(self.root)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = tk.Label(info_frame, text="Start a new game", font=("Arial", 12, "bold"))
        self.status_label.pack(side=tk.LEFT)
        
        self.dice_label = tk.Label(info_frame, text="Dice: -", font=("Arial", 12))
        self.dice_label.pack(side=tk.LEFT, padx=20)
        
        # Board canvas
        self.canvas = tk.Canvas(self.root, width=500, height=400, bg="white")
        self.canvas.pack(side=tk.TOP, padx=10, pady=10)
        
        # Control buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.roll_btn = tk.Button(btn_frame, text="Roll Dice", command=self.roll_dice)
        self.roll_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Label(btn_frame, text="Pawn:").pack(side=tk.LEFT, padx=5)
        self.pawn_var = tk.StringVar()
        self.pawn_combo = ttk.Combobox(btn_frame, textvariable=self.pawn_var, width=5, state="disabled")
        self.pawn_combo.pack(side=tk.LEFT, padx=5)
        
        self.move_btn = tk.Button(btn_frame, text="Make Move", command=self.make_move, state="disabled")
        self.move_btn.pack(side=tk.LEFT, padx=5)
        
        self.skip_btn = tk.Button(btn_frame, text="Skip Turn", command=self.skip_turn, state="disabled")
        self.skip_btn.pack(side=tk.LEFT, padx=5)
        
        # Log display
        log_frame = tk.Frame(self.root)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(log_frame, text="Game Log:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)
    
    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def start_new_game(self):
        # Create dialog for game setup
        setup_dialog = tk.Toplevel(self.root)
        setup_dialog.title("New Game Setup")
        setup_dialog.transient(self.root)
        setup_dialog.grab_set()
        
        tk.Label(setup_dialog, text="Number of players (2-4):").grid(row=0, column=0, padx=5, pady=5)
        num_players_var = tk.StringVar(value="2")
        num_players_combo = ttk.Combobox(setup_dialog, textvariable=num_players_var, 
                                         values=["2", "3", "4"], width=5, state="readonly")
        num_players_combo.grid(row=0, column=1, padx=5, pady=5)
        
        def on_submit():
            try:
                num_players = int(num_players_var.get())
                if num_players < 2 or num_players > 4:
                    raise ValueError("Number of players must be between 2 and 4")
                
                self.game = LudoGame(num_players)
                setup_dialog.destroy()
                self.draw_board()
                self.update_status()
                self.roll_btn.config(state="normal")
                self.log_message("New game started!")
                self.log_message(f"Player {self.game.current_player}'s turn")
            except ValueError as e:
                messagebox.showerror("Invalid Input", str(e))
        
        tk.Button(setup_dialog, text="Start Game", command=on_submit).grid(row=1, column=0, columnspan=2, pady=10)
    
    def draw_board(self):
        # Clear canvas
        self.canvas.delete("all")
        self.canvas_items = {}
        
        # Draw board outline
        self.canvas.create_rectangle(50, 50, 450, 350, outline="black", width=2)
        
        # Draw player bases
        colors = ['red', 'green', 'blue', 'yellow']
        bases = [
            (70, 70, 150, 150),   # Player 0
            (350, 70, 430, 150),   # Player 1
            (350, 250, 430, 330),  # Player 2
            (70, 250, 150, 330)    # Player 3
        ]
        
        for i, base in enumerate(bases):
            if i < self.game.num_players:
                self.canvas.create_rectangle(*base, fill=colors[i], outline="black")
        
        # Draw home positions
        homes = [(200, 100), (300, 100), (300, 200), (200, 200)]
        for i, home in enumerate(homes):
            if i < self.game.num_players:
                self.canvas.create_oval(home[0]-15, home[1]-15, home[0]+15, home[1]+15, 
                                       fill=colors[i], outline="black")
        
        # Draw pawns
        for player in self.game.players:
            for pawn_idx, steps in enumerate(player.pawns):
                if steps == 0:  # In base
                    base_idx = player.id
                    base = bases[base_idx]
                    x = base[0] + 20 + (pawn_idx % 2) * 40
                    y = base[1] + 20 + (pawn_idx // 2) * 40
                elif steps >= 52:  # In home stretch
                    home_pos = steps - 52
                    home = homes[player.id]
                    if player.id == 0:
                        x = home[0] - 20 + home_pos * 10
                        y = home[1]
                    elif player.id == 1:
                        x = home[0]
                        y = home[1] - 20 + home_pos * 10
                    elif player.id == 2:
                        x = home[0] + 20 - home_pos * 10
                        y = home[1]
                    else:  # player.id == 3
                        x = home[0]
                        y = home[1] + 20 - home_pos * 10
                else:  # On main track
                    abs_pos = self.game.get_absolute_position(player.id, steps)
                    angle = (abs_pos / 52) * 360
                    rad = angle * (3.14159 / 180)
                    x = 250 + 150 * math.cos(rad)
                    y = 200 + 150 * math.sin(rad)
                
                pawn = self.canvas.create_oval(x-10, y-10, x+10, y+10, 
                                              fill=player.color, outline="black")
                self.canvas_items[(player.id, pawn_idx)] = pawn
    
    def update_status(self):
        if not self.game:
            return
        
        player = self.game.players[self.game.current_player]
        status = f"Player {self.game.current_player}'s turn ({player.color})"
        self.status_label.config(text=status)
        
        dice_text = f"Dice: {self.game.dice_value}" if self.game.dice_value > 0 else "Dice: -"
        self.dice_label.config(text=dice_text)
        
        # Update pawn positions
        for player in self.game.players:
            for pawn_idx, steps in enumerate(player.pawns):
                if steps == 0:  # In base
                    base_idx = player.id
                    base = [
                        (70, 70, 150, 150),   # Player 0
                        (350, 70, 430, 150),   # Player 1
                        (350, 250, 430, 330),  # Player 2
                        (70, 250, 150, 330)    # Player 3
                    ][base_idx]
                    x = base[0] + 20 + (pawn_idx % 2) * 40
                    y = base[1] + 20 + (pawn_idx // 2) * 40
                elif steps >= 52:  # In home stretch
                    home_pos = steps - 52
                    homes = [(200, 100), (300, 100), (300, 200), (200, 200)]
                    home = homes[player.id]
                    if player.id == 0:
                        x = home[0] - 20 + home_pos * 10
                        y = home[1]
                    elif player.id == 1:
                        x = home[0]
                        y = home[1] - 20 + home_pos * 10
                    elif player.id == 2:
                        x = home[0] + 20 - home_pos * 10
                        y = home[1]
                    else:  # player.id == 3
                        x = home[0]
                        y = home[1] + 20 - home_pos * 10
                else:  # On main track
                    abs_pos = self.game.get_absolute_position(player.id, steps)
                    angle = (abs_pos / 52) * 360
                    rad = angle * (3.14159 / 180)
                    x = 250 + 150 * math.cos(rad)
                    y = 200 + 150 * math.sin(rad)
                
                pawn_id = self.canvas_items.get((player.id, pawn_idx))
                if pawn_id:
                    self.canvas.coords(pawn_id, x-10, y-10, x+10, y+10)
    
    def roll_dice(self):
        if not self.game or self.game.game_over:
            return
        
        self.game.roll_dice()
        self.dice_label.config(text=f"Dice: {self.game.dice_value}")
        self.log_message(f"Player {self.game.current_player} rolled: {self.game.dice_value}")
        
        available_pawns = self.game.get_available_pawns(self.game.current_player, self.game.dice_value)
        
        if not available_pawns:
            self.log_message("No available moves")
            self.pawn_combo.config(values=[], state="disabled")
            self.move_btn.config(state="disabled")
            self.skip_btn.config(state="normal")
            return
        
        self.pawn_combo.config(values=available_pawns, state="readonly")
        self.move_btn.config(state="normal")
        self.skip_btn.config(state="disabled")
    
    def make_move(self):
        if not self.game or self.game.game_over:
            return
        
        player_id = self.game.current_player
        player = self.game.players[player_id]
        
        try:
            pawn_idx = int(self.pawn_combo.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please select a valid pawn")
            return
        
        valid, message = self.game.move_pawn(player_id, pawn_idx, self.game.dice_value)
        
        if not valid:
            messagebox.showerror("Invalid Move", message)
            return
        
        self.log_message(f"Player {player_id} moved pawn {pawn_idx}")
        
        if self.game.last_move:
            self.log_message(self.game.last_move)
            self.game.last_move = ""
        
        self.update_status()
        self.update_board()
        
        if self.game.check_win(player_id):
            self.log_message(f"Player {player_id} wins the game!")
            messagebox.showinfo("Game Over", f"Player {player_id} wins!")
            self.game.game_over = True
            self.roll_btn.config(state="disabled")
            self.move_btn.config(state="disabled")
            self.skip_btn.config(state="disabled")
            return
        
        # Handle sixes and extra turns
        if self.game.dice_value == 6:
            self.game.consecutive_sixes += 1
            
            if self.game.consecutive_sixes == 3:
                self.log_message("Three sixes! Turn skipped.")
                self.game.next_player()
                self.log_message(f"Player {self.game.current_player}'s turn")
                self.roll_btn.config(state="normal")
                self.pawn_combo.set('')
                self.pawn_combo.config(state="disabled")
                self.move_btn.config(state="disabled")
                self.skip_btn.config(state="disabled")
            else:
                self.log_message("Rolled a 6! Extra turn.")
                self.roll_btn.config(state="normal")
                self.pawn_combo.set('')
                self.pawn_combo.config(state="disabled")
                self.move_btn.config(state="disabled")
                self.skip_btn.config(state="disabled")
        else:
            self.game.next_player()
            self.log_message(f"Player {self.game.current_player}'s turn")
            self.roll_btn.config(state="normal")
            self.pawn_combo.set('')
            self.pawn_combo.config(state="disabled")
            self.move_btn.config(state="disabled")
            self.skip_btn.config(state="disabled")
    
    def skip_turn(self):
        if not self.game or self.game.game_over:
            return
        
        self.log_message(f"Player {self.game.current_player} skips turn")
        self.game.next_player()
        self.log_message(f"Player {self.game.current_player}'s turn")
        self.roll_btn.config(state="normal")
        self.pawn_combo.set('')
        self.pawn_combo.config(state="disabled")
        self.move_btn.config(state="disabled")
        self.skip_btn.config(state="disabled")
    
    def update_board(self):
        # Redraw the board with updated positions
        self.draw_board()

if __name__ == "__main__":
    import math
    app = LudoGUI()
