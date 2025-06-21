import tkinter as tk
from tkinter import messagebox, scrolledtext
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
        return self.players[0]  # Return first player
    
    def play_first_domino(self, player, domino_idx):
        if not 0 <= domino_idx < len(player.hand):
            return False, "Invalid domino index"
        
        domino = player.play_domino(domino_idx)
        self.chain.append(domino)
        self.left_end = domino.a
        self.right_end = domino.b
        return True, f"{player.name} plays {domino} as set"
    
    def play_domino_turn(self, player, domino_idx, end_choice):
        if not 0 <= domino_idx < len(player.hand):
            return False, "Invalid domino index"
        
        if end_choice not in ('L', 'R'):
            return False, "Invalid end choice (must be L or R)"
        
        domino = player.hand[domino_idx]
        target = self.left_end if end_choice == 'L' else self.right_end
        
        if not domino.matches(target):
            return False, f"{domino} doesn't match {target}!"
        
        # Valid play
        player.play_domino(domino_idx)
        if domino.a == target:
            new_end = domino.b
        else:
            new_end = domino.a
        
        if end_choice == 'L':
            self.left_end = new_end
        else:
            self.right_end = new_end
        
        self.chain.append(domino)
        return True, f"{player.name} plays {domino} on {'left' if end_choice == 'L' else 'right'} end"
    
    def draw_from_boneyard(self, player):
        draw_limit = 1 if len(self.players) > 2 else 2
        if len(self.boneyard) <= draw_limit:
            return False, "Boneyard exhausted, no draw possible"
        
        domino = self.boneyard.pop()
        player.draw(domino)
        message = f"{player.name} draws {domino}"
        
        if player.hand[-1].matches(self.left_end) or player.hand[-1].matches(self.right_end):
            message += " - drawn domino is playable"
        return True, message
    
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
    
    def get_current_player(self):
        return self.players[self.current_player_index]
    
    def get_board_ends(self):
        return self.left_end, self.right_end
    
    def get_boneyard_count(self):
        return len(self.boneyard)
    
    def get_chain_str(self):
        return " ".join(str(d) for d in self.chain)

class DominoGameGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Domino Game")
        self.root.geometry("800x600")
        
        # Game variables
        self.game = None
        self.round_num = 1
        
        # Create UI elements
        self.create_widgets()
        
        self.root.mainloop()
    
    def create_widgets(self):
        # Control frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(control_frame, text="New Game", command=self.start_new_game).pack(side=tk.LEFT)
        
        # Player info
        self.player_frame = tk.Frame(self.root)
        self.player_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Board display
        board_frame = tk.Frame(self.root)
        board_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(board_frame, text="Board:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        self.board_label = tk.Label(board_frame, text="", font=("Arial", 12))
        self.board_label.pack(fill=tk.X, padx=5)
        
        # Ends display
        self.ends_label = tk.Label(board_frame, text="Ends: -/-", font=("Arial", 10))
        self.ends_label.pack(anchor=tk.W, padx=5)
        
        # Boneyard display
        self.boneyard_label = tk.Label(board_frame, text="Boneyard: 0", font=("Arial", 10))
        self.boneyard_label.pack(anchor=tk.W, padx=5)
        
        # Hand display
        hand_frame = tk.Frame(self.root)
        hand_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(hand_frame, text="Your Hand:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        self.hand_frame = tk.Frame(hand_frame)
        self.hand_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Move input
        move_frame = tk.Frame(self.root)
        move_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(move_frame, text="Make Move:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        input_frame = tk.Frame(move_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(input_frame, text="Domino Index:").pack(side=tk.LEFT)
        self.domino_entry = tk.Entry(input_frame, width=5)
        self.domino_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(input_frame, text="End (L/R):").pack(side=tk.LEFT)
        self.end_entry = tk.Entry(input_frame, width=5)
        self.end_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(input_frame, text="Play", command=self.make_move).pack(side=tk.LEFT, padx=5)
        tk.Button(input_frame, text="Draw", command=self.draw_domino).pack(side=tk.LEFT, padx=5)
        tk.Button(input_frame, text="Skip", command=self.skip_turn).pack(side=tk.LEFT, padx=5)
        
        # Log display
        log_frame = tk.Frame(self.root)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(log_frame, text="Game Log:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)
        
        # Scores display
        self.scores_label = tk.Label(self.root, text="Scores: ", font=("Arial", 10))
        self.scores_label.pack(anchor=tk.W, padx=10, pady=5)
    
    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def start_new_game(self):
        # Reset game state
        self.round_num = 1
        
        # Create dialog for game setup
        setup_dialog = tk.Toplevel(self.root)
        setup_dialog.title("New Game Setup")
        setup_dialog.transient(self.root)
        setup_dialog.grab_set()
        
        tk.Label(setup_dialog, text="Number of players (2-4):").grid(row=0, column=0, padx=5, pady=5)
        num_players_var = tk.StringVar(value="2")
        num_players_entry = tk.Entry(setup_dialog, textvariable=num_players_var, width=5)
        num_players_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(setup_dialog, text="Game type:").grid(row=1, column=0, padx=5, pady=5)
        game_type_var = tk.StringVar(value="block")
        game_type_menu = tk.OptionMenu(setup_dialog, game_type_var, "block", "draw")
        game_type_menu.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(setup_dialog, text="Target score:").grid(row=2, column=0, padx=5, pady=5)
        target_score_var = tk.StringVar(value="100")
        target_score_entry = tk.Entry(setup_dialog, textvariable=target_score_var, width=5)
        target_score_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def on_submit():
            try:
                num_players = int(num_players_var.get())
                if num_players < 2 or num_players > 4:
                    raise ValueError("Number of players must be between 2 and 4")
                
                target_score = int(target_score_var.get())
                game_type = game_type_var.get()
                
                self.game = DominoGame(num_players, game_type, target_score)
                setup_dialog.destroy()
                self.new_round()
            except ValueError as e:
                messagebox.showerror("Invalid Input", str(e))
        
        tk.Button(setup_dialog, text="Start Game", command=on_submit).grid(row=3, column=0, columnspan=2, pady=10)
    
    def new_round(self):
        # Clear UI
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        
        # Setup new round
        first_player = self.game.setup_game()
        self.log_message(f"\n=== Round {self.round_num} ===")
        self.log_message(f"{first_player.name} goes first")
        self.log_message("Select a domino to start the game")
        
        # Display player's hand
        current_player = self.game.get_current_player()
        for idx, domino in enumerate(current_player.hand):
            tk.Label(self.hand_frame, text=str(domino), font=("Arial", 12), 
                     borderwidth=1, relief="solid", padx=5, pady=2).grid(row=0, column=idx, padx=2)
        
        # Update board info
        self.update_board()
    
    def update_board(self):
        # Update scores
        scores_text = "Scores: " + " | ".join(
            f"{player.name}: {self.game.scores[player]}" for player in self.game.players
        )
        self.scores_label.config(text=scores_text)
        
        # Update board display
        if self.game.chain:
            self.board_label.config(text=self.game.get_chain_str())
            left, right = self.game.get_board_ends()
            self.ends_label.config(text=f"Ends: {left}/{right}")
        else:
            self.board_label.config(text="Board is empty")
            self.ends_label.config(text="Ends: -/-")
        
        # Update boneyard
        self.boneyard_label.config(text=f"Boneyard: {self.game.get_boneyard_count()}")
    
    def make_move(self):
        if not self.game:
            messagebox.showerror("Error", "No game in progress")
            return
        
        current_player = self.game.get_current_player()
        
        try:
            domino_idx = int(self.domino_entry.get())
            end_choice = self.end_entry.get().strip().upper()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers")
            return
        
        # Handle first move
        if not self.game.chain:
            success, message = self.game.play_first_domino(current_player, domino_idx)
            if success:
                self.log_message(message)
                self.end_turn()
            else:
                messagebox.showerror("Invalid Move", message)
            return
        
        # Handle subsequent moves
        success, message = self.game.play_domino_turn(current_player, domino_idx, end_choice)
        if success:
            self.log_message(message)
            self.end_turn()
        else:
            messagebox.showerror("Invalid Move", message)
    
    def draw_domino(self):
        if not self.game:
            messagebox.showerror("Error", "No game in progress")
            return
        
        if self.game.game_type != "draw":
            messagebox.showerror("Not Allowed", "Drawing is only allowed in 'draw' game type")
            return
        
        current_player = self.game.get_current_player()
        success, message = self.game.draw_from_boneyard(current_player)
        self.log_message(message)
        
        # If drawn domino is playable, give player a chance to play it
        if success and "playable" in message:
            self.log_message("You can play the drawn domino now")
        else:
            self.end_turn()
    
    def skip_turn(self):
        if not self.game:
            messagebox.showerror("Error", "No game in progress")
            return
        
        current_player = self.game.get_current_player()
        self.log_message(f"{current_player.name} skips turn")
        self.end_turn()
    
    def end_turn(self):
        # Check for win condition
        current_player = self.game.get_current_player()
        if len(current_player.hand) == 0:
            winner = current_player
            score = sum(p.hand_total() for p in self.game.players if p != winner)
            self.game.scores[winner] += score
            self.log_message(f"\n{winner.name} wins round with score {score}")
            self.log_message(f"Scores updated: {', '.join(f'{p.name}: {s}' for p, s in self.game.scores.items())}")
            self.next_round()
            return
        
        if self.game.is_blocked():
            winner, score = self.game.calculate_round_winner()
            self.game.scores[winner] += score
            self.log_message(f"\nGame blocked! {winner.name} wins with score {score}")
            self.log_message(f"Scores updated: {', '.join(f'{p.name}: {s}' for p, s in self.game.scores.items())}")
            self.next_round()
            return
        
        # Move to next player
        next_player = self.game.next_player()
        self.log_message(f"\n{next_player.name}'s turn")
        
        # Update hand display
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        
        for idx, domino in enumerate(next_player.hand):
            tk.Label(self.hand_frame, text=str(domino), font=("Arial", 12), 
                     borderwidth=1, relief="solid", padx=5, pady=2).grid(row=0, column=idx, padx=2)
        
        # Update board
        self.update_board()
    
    def next_round(self):
        # Check if game is over
        max_score = max(score for score in self.game.scores.values())
        if max_score >= self.game.target_score:
            winner = max(self.game.scores, key=self.game.scores.get)
            self.log_message(f"\n{winner.name} wins the game with {self.game.scores[winner]} points!")
            return
        
        # Prepare for next round
        self.round_num += 1
        self.game.reset_round()
        self.new_round()

if __name__ == "__main__":
    app = DominoGameGUI()
