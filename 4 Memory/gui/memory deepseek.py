import tkinter as tk
from tkinter import messagebox, scrolledtext
import random
import time

class MemoryGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Memory Game")
        self.root.geometry("600x600")
        
        self.num_pairs = 8
        self.board_size = 16
        self.players = 1
        self.current_player = 0
        self.scores = []
        self.board = []
        # Состояния: hidden, visible, matched
        self.state = []  
        self.first_card = None
        self.second_card = None
        self.game_over = False
        self.card_buttons = []
        
        self.create_widgets()
        self.new_game()
    
    def create_widgets(self):
        # Control frame
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=10)
        
        self.new_game_btn = tk.Button(self.control_frame, text="New Game", command=self.new_game)
        self.new_game_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Label(self.control_frame, text="Players:").pack(side=tk.LEFT, padx=5)
        self.player_var = tk.StringVar(value="1")
        self.player_menu = tk.OptionMenu(self.control_frame, self.player_var, "1", "2", "3", "4")
        self.player_menu.pack(side=tk.LEFT, padx=5)
        
        # Status frame
        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(pady=5)
        
        self.player_label = tk.Label(self.status_frame, text="Player: 1")
        self.player_label.pack(side=tk.LEFT, padx=10)
        
        self.score_label = tk.Label(self.status_frame, text="Scores: P1: 0")
        self.score_label.pack(side=tk.LEFT, padx=10)
        
        # Game board
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack(pady=10)
        
        # Game log
        self.log_frame = tk.LabelFrame(self.root, text="Game Log")
        self.log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_area = scrolledtext.ScrolledText(self.log_frame, height=10)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_area.config(state=tk.DISABLED)
    
    def log(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)
    
    def new_game(self):
        # Clear previous board
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        
        self.card_buttons = []
        self.players = int(self.player_var.get())
        self.scores = [0] * self.players
        self.current_player = 0
        self.first_card = None
        self.second_card = None
        self.game_over = False
        
        # Create board
        symbols = list(range(self.num_pairs)) * 2
        random.shuffle(symbols)
        self.board = symbols
        self.state = ['hidden'] * self.board_size
        
        # Create card buttons
        for i in range(4):
            for j in range(4):
                index = i * 4 + j
                btn = tk.Button(
                    self.board_frame, 
                    text="?", 
                    width=4, 
                    height=2,
                    font=("Arial", 14),
                    command=lambda idx=index: self.card_click(idx)
                )
                btn.grid(row=i, column=j, padx=5, pady=5)
                self.card_buttons.append(btn)
        
        self.update_status()
        self.log("=== New game started ===")
        self.log(f"Players: {self.players}")
    
    def update_status(self):
        self.player_label.config(text=f"Player: {self.current_player + 1}")
        score_text = "Scores: " + ", ".join([f"P{i+1}: {s}" for i, s in enumerate(self.scores)])
        self.score_label.config(text=score_text)
    
    def card_click(self, index):
        if self.game_over:
            return
            
        if self.state[index] != 'hidden':
            messagebox.showinfo("Invalid Move", "This card is already revealed!")
            return
            
        if self.second_card is not None:
            messagebox.showinfo("Invalid Move", "Please wait for the current pair to be checked")
            return
            
        self.reveal_card(index)
        self.log(f"Player {self.current_player+1} flipped card {index}")
        
        if self.first_card is None:
            self.first_card = index
        else:
            self.second_card = index
            self.root.after(1000, self.check_match)
    
    def reveal_card(self, index):
        self.state[index] = 'visible'
        self.card_buttons[index].config(text=str(self.board[index]), bg="lightblue")
    
    def hide_card(self, index):
        self.state[index] = 'hidden'
        self.card_buttons[index].config(text="?", bg="SystemButtonFace")
    
    def check_match(self):
        if self.board[self.first_card] == self.board[self.second_card]:
            # Match found
            self.state[self.first_card] = 'matched'
            self.state[self.second_card] = 'matched'
            self.card_buttons[self.first_card].config(bg="green", state=tk.DISABLED)
            self.card_buttons[self.second_card].config(bg="green", state=tk.DISABLED)
            self.scores[self.current_player] += 1
            
            self.log(f"Player {self.current_player+1} found a match!")
            
            # Check for game over
            if all(status == 'matched' for status in self.state):
                self.game_over = True
                self.log("\n=== Game Over! ===")
                max_score = max(self.scores)
                winners = [i+1 for i, score in enumerate(self.scores) if score == max_score]
                
                if len(winners) == 1:
                    self.log(f"Player {winners[0]} wins with {max_score} points!")
                    messagebox.showinfo("Game Over", f"Player {winners[0]} wins with {max_score} points!")
                else:
                    win_text = ", ".join([f"Player {w}" for w in winners])
                    self.log(f"It's a tie! Winners: {win_text} with {max_score} points")
                    messagebox.showinfo("Game Over", f"It's a tie! Winners: {win_text} with {max_score} points")
        else:
            # No match
            self.log(f"Player {self.current_player+1}: no match")
            self.hide_card(self.first_card)
            self.hide_card(self.second_card)
            self.next_player()
        
        self.first_card = None
        self.second_card = None
        self.update_status()
    
    def next_player(self):
        self.current_player = (self.current_player + 1) % self.players
        self.log(f"Turn passed to Player {self.current_player+1}")

if __name__ == "__main__":
    root = tk.Tk()
    game = MemoryGameGUI(root)
    root.mainloop()
