import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import random

class Player:
    __slots__ = ('id', 'position', 'color')
    def __init__(self, player_id, color):
        self.id = player_id
        self.position = 0
        self.color = color

class SnakesAndLaddersGame:
    def __init__(self, num_players=2, exact_win=True):
        self.num_players = num_players
        self.players = []
        colors = ['red', 'green', 'blue', 'yellow']
        for i in range(num_players):
            self.players.append(Player(i, colors[i]))
        self.current_player = 0
        self.game_over = False
        self.exact_win = exact_win
        self.consecutive_sixes = 0
        self.dice_value = 0
        self.last_move = ""
        
        # Define snakes and ladders
        self.snakes = {
            16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 
            64: 60, 87: 24, 93: 73, 95: 75, 98: 78
        }
        self.ladders = {
            1: 38, 4: 14, 9: 31, 21: 42, 28: 84, 
            36: 44, 51: 67, 71: 91, 80: 100
        }
    
    def roll_dice(self):
        self.dice_value = random.randint(1, 6)
        return self.dice_value
    
    def move_player(self, player):
        start_pos = player.position
        new_pos = start_pos + self.dice_value
        
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
        move_desc = f"Player {player.id} rolled {self.dice_value}: {start_pos} → {new_pos}"
        if action:
            move_desc += f" (Hit {action}) → {player.position}"
        
        return False, move_desc
    
    def play_turn(self):
        if self.game_over:
            return False, "Game is already over"
        
        player = self.players[self.current_player]
        
        # Handle three consecutive sixes
        if self.dice_value == 6:
            self.consecutive_sixes += 1
            if self.consecutive_sixes == 3:
                self.consecutive_sixes = 0
                self.next_player()
                return False, f"Player {player.id} rolled three sixes! Turn skipped."
        else:
            self.consecutive_sixes = 0
        
        # Move player and check for win
        win, message = self.move_player(player)
        self.last_move = message
        
        if win:
            self.game_over = True
            return True, message
        
        # Handle extra turn for rolling a six
        if self.dice_value == 6 and not win:
            return False, message + " - Extra turn!"
        
        self.next_player()
        return False, message
    
    def next_player(self):
        self.current_player = (self.current_player + 1) % self.num_players
        self.consecutive_sixes = 0

class SnakesAndLaddersGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Snakes and Ladders")
        self.root.geometry("900x700")
        
        # Game variables
        self.game = None
        self.pawn_icons = {}
        
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
        
        # Board frame
        board_frame = tk.Frame(self.root)
        board_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Board canvas
        self.canvas = tk.Canvas(board_frame, width=600, height=600, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Player info
        self.player_frame = tk.Frame(board_frame)
        self.player_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        # Control buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.roll_btn = tk.Button(btn_frame, text="Roll Dice", command=self.roll_dice, state="disabled")
        self.roll_btn.pack(side=tk.LEFT, padx=5)
        
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
        
        tk.Label(setup_dialog, text="Win condition:").grid(row=1, column=0, padx=5, pady=5)
        win_condition_var = tk.StringVar(value="exact")
        win_condition_combo = ttk.Combobox(setup_dialog, textvariable=win_condition_var, 
                                           values=["exact", "fast"], width=5, state="readonly")
        win_condition_combo.grid(row=1, column=1, padx=5, pady=5)
        
        def on_submit():
            try:
                num_players = int(num_players_var.get())
                if num_players < 2 or num_players > 4:
                    raise ValueError("Number of players must be between 2 and 4")
                
                exact_win = win_condition_var.get() == "exact"
                self.game = SnakesAndLaddersGame(num_players, exact_win)
                setup_dialog.destroy()
                self.draw_board()
                self.update_status()
                self.roll_btn.config(state="normal")
                self.log_message("New game started!")
                self.log_message(f"Player {self.game.current_player}'s turn")
                self.determine_first_player()
            except ValueError as e:
                messagebox.showerror("Invalid Input", str(e))
        
        tk.Button(setup_dialog, text="Start Game", command=on_submit).grid(row=2, column=0, columnspan=2, pady=10)
    
    def determine_first_player(self):
        players = list(range(self.game.num_players))
        rolls = {}
        
        self.log_message("\nDetermining first player:")
        while len(players) > 1:
            max_roll = 0
            next_round = []
            
            for player_id in players:
                roll = random.randint(1, 6)
                rolls[player_id] = roll
                self.log_message(f"Player {player_id} rolled: {roll}")
                if roll > max_roll:
                    max_roll = roll
                    next_round = [player_id]
                elif roll == max_roll:
                    next_round.append(player_id)
            
            if len(next_round) == 1:
                self.game.current_player = next_round[0]
                self.log_message(f"Player {next_round[0]} goes first!")
                return
            
            self.log_message(f"Tie between players: {', '.join(str(p) for p in next_round)}")
            players = next_round
        
        self.game.current_player = players[0]
        self.log_message(f"Player {players[0]} goes first!")
    
    def draw_board(self):
        # Clear canvas
        self.canvas.delete("all")
        self.pawn_icons = {}
        
        # Draw board grid (10x10)
        cell_size = 50
        for row in range(10):
            for col in range(10):
                # Calculate position number (zigzag pattern)
                if row % 2 == 0:  # Even rows (0,2,4,6,8) left to right
                    pos = row * 10 + col + 1
                else:  # Odd rows (1,3,5,7,9) right to left
                    pos = row * 10 + (9 - col) + 1
                
                # Calculate coordinates
                x1 = col * cell_size
                y1 = (9 - row) * cell_size  # Invert rows to start from bottom
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                # Draw cell
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black")
                self.canvas.create_text(x1 + 10, y1 + 10, text=str(pos), font=("Arial", 8))
                
                # Draw snakes and ladders
                if pos in self.game.snakes:
                    target = self.game.snakes[pos]
                    target_row = 9 - ((target - 1) // 10)
                    target_col = (target - 1) % 10
                    if (target - 1) // 10 % 2 != 0:  # Adjust for zigzag
                        target_col = 9 - target_col
                    
                    self.canvas.create_line(
                        col * cell_size + cell_size//2, 
                        (9 - row) * cell_size + cell_size//2,
                        target_col * cell_size + cell_size//2,
                        target_row * cell_size + cell_size//2,
                        fill="red", width=2, arrow=tk.LAST
                    )
                
                if pos in self.game.ladders:
                    target = self.game.ladders[pos]
                    target_row = 9 - ((target - 1) // 10)
                    target_col = (target - 1) % 10
                    if (target - 1) // 10 % 2 != 0:  # Adjust for zigzag
                        target_col = 9 - target_col
                    
                    self.canvas.create_line(
                        col * cell_size + cell_size//2, 
                        (9 - row) * cell_size + cell_size//2,
                        target_col * cell_size + cell_size//2,
                        target_row * cell_size + cell_size//2,
                        fill="green", width=2, arrow=tk.LAST
                    )
        
        # Draw player pawns
        self.update_pawns()
    
    def update_pawns(self):
        # Remove old pawns
        for pawn in self.pawn_icons.values():
            self.canvas.delete(pawn)
        self.pawn_icons = {}
        
        # Draw new pawns
        cell_size = 50
        pawn_offsets = [(15, 15), (35, 15), (15, 35), (35, 35)]
        
        for player in self.game.players:
            pos = player.position
            if pos == 0:  # Start position
                row, col = 9, 0
            elif pos == 100:  # End position
                row, col = 0, 9
            else:
                row = 9 - ((pos - 1) // 10)
                col = (pos - 1) % 10
                
                # Adjust for zigzag pattern
                if row % 2 != (9 % 2):  # Even rows (0-indexed: 0,2,4,6,8) are odd in 1-indexed
                    col = 9 - col
            
            # Calculate pawn position
            x = col * cell_size + pawn_offsets[player.id][0]
            y = row * cell_size + pawn_offsets[player.id][1]
            
            # Draw pawn
            pawn = self.canvas.create_oval(
                x-10, y-10, x+10, y+10, 
                fill=player.color, outline="black"
            )
            self.pawn_icons[player.id] = pawn
    
    def update_status(self):
        if not self.game:
            return
        
        player = self.game.players[self.game.current_player]
        status = f"Player {self.game.current_player}'s turn ({player.color})"
        self.status_label.config(text=status)
        
        dice_text = f"Dice: {self.game.dice_value}" if self.game.dice_value > 0 else "Dice: -"
        self.dice_label.config(text=dice_text)
    
    def roll_dice(self):
        if not self.game or self.game.game_over:
            messagebox.showerror("Game Error", "No active game or game is over")
            return
        
        self.game.roll_dice()
        self.dice_label.config(text=f"Dice: {self.game.dice_value}")
        self.log_message(f"Player {self.game.current_player} rolled: {self.game.dice_value}")
        
        win, message = self.game.play_turn()
        self.log_message(self.game.last_move)
        
        if win:
            self.log_message(message)
            self.log_message(f"Player {self.game.current_player} wins the game!")
            messagebox.showinfo("Game Over", message)
            self.game.game_over = True
            self.roll_btn.config(state="disabled")
        
        self.update_pawns()
        self.update_status()
        
        # Handle extra turn for six
        if "Extra turn" in self.game.last_move:
            self.log_message(f"Player {self.game.current_player} gets another turn!")

if __name__ == "__main__":
    app = SnakesAndLaddersGUI()
