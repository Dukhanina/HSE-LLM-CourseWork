import tkinter as tk
from tkinter import messagebox, scrolledtext
import random

class Card:
    def __init__(self, color, value, card_type):
        self.color = color
        self.value = value
        self.type = card_type
    
    def __str__(self):
        if self.type == 'number':
            return f"{self.color} {self.value}"
        elif self.type == 'wild':
            return "Wild"
        elif self.type == 'wild_draw4':
            return "Wild Draw 4"
        else:
            return f"{self.color} {self.type.capitalize()}"

class Player:
    def __init__(self, name, is_human=False):
        self.name = name
        self.hand = []
        self.is_human = is_human
        self.uno_not_said = False

class UnoGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("UNO Game")
        self.root.geometry("700x600")
        
        # Game state variables
        self.players = []
        self.deck = []
        self.discard_pile = []
        self.current_player_index = 0
        self.skip_next = False
        self.current_color = None
        self.game_active = False
        
        # Create UI elements
        self.create_widgets()
        self.root.mainloop()
    
    def create_widgets(self):
        # Top frame for game controls
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)
        
        self.new_game_btn = tk.Button(top_frame, text="New Game", command=self.start_new_game)
        self.new_game_btn.pack(side=tk.LEFT, padx=5)
        
        self.top_card_label = tk.Label(top_frame, text="Top Card: -", font=("Arial", 12))
        self.top_card_label.pack(side=tk.LEFT, padx=20)
        
        self.current_player_label = tk.Label(top_frame, text="Current Player: -", font=("Arial", 12))
        self.current_player_label.pack(side=tk.LEFT, padx=20)
        
        # Player hand display
        hand_frame = tk.LabelFrame(self.root, text="Your Hand")
        hand_frame.pack(pady=10, fill=tk.X, padx=10)
        
        self.hand_listbox = tk.Listbox(hand_frame, height=8, width=50)
        self.hand_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Action buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        
        self.play_btn = tk.Button(btn_frame, text="Play Selected Card", command=self.play_selected_card)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        self.draw_btn = tk.Button(btn_frame, text="Draw Card", command=self.draw_card)
        self.draw_btn.pack(side=tk.LEFT, padx=5)
        
        # Game log
        log_frame = tk.LabelFrame(self.root, text="Game Log")
        log_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=10)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, height=12)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_area.config(state=tk.DISABLED)
    
    def log_message(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)
    
    def create_deck(self):
        colors = ['Red', 'Blue', 'Green', 'Yellow']
        deck = []
        
        # Number cards
        for color in colors:
            for num in range(0, 10):
                count = 2 if num != 0 else 1
                deck.extend([Card(color, num, 'number') for _ in range(count)])
        
        # Action cards
        for color in colors:
            deck.extend([Card(color, None, 'reverse') for _ in range(2)])
            deck.extend([Card(color, None, 'skip') for _ in range(2)])
            deck.extend([Card(color, None, 'draw2') for _ in range(2)])
        
        # Wild cards
        deck.extend([Card(None, None, 'wild') for _ in range(4)])
        deck.extend([Card(None, None, 'wild_draw4') for _ in range(4)])
        
        random.shuffle(deck)
        return deck
    
    def valid_play(self, played_card):
        top_card = self.discard_pile[-1]
        
        if played_card.type in ['wild', 'wild_draw4']:
            return True
        if played_card.color == self.current_color:
            return True
        if played_card.type == top_card.type and top_card.type != 'number':
            return True
        if played_card.type == 'number' and top_card.type == 'number' and played_card.value == top_card.value:
            return True
        return False
    
    def start_new_game(self):
        self.game_active = True
        self.log_message("=== Starting new UNO game ===")
        
        # Create players
        self.players = [
            Player("Player 1", is_human=True),
            Player("Computer")
        ]
        
        # Initialize deck and hands
        self.deck = self.create_deck()
        self.discard_pile = []
        
        for player in self.players:
            player.hand = []
            player.uno_not_said = False
            for _ in range(7):
                player.hand.append(self.deck.pop())
        
        # Start with first card
        while True:
            card = self.deck.pop()
            if card.type not in ['wild', 'wild_draw4']:
                self.discard_pile.append(card)
                self.current_color = card.color
                self.log_message(f"First card: {card}")
                break
            else:
                self.deck.insert(0, card)
        
        self.current_player_index = 0
        self.skip_next = False
        self.update_ui()
    
    def update_ui(self):
        # Update top card display
        if self.discard_pile:
            self.top_card_label.config(text=f"Top Card: {str(self.discard_pile[-1])} (Color: {self.current_color})")
        
        # Update player info
        current_player = self.players[self.current_player_index]
        self.current_player_label.config(text=f"Current Player: {current_player.name}")
        
        # Update hand display for human player
        self.hand_listbox.delete(0, tk.END)
        if current_player.is_human:
            for i, card in enumerate(current_player.hand):
                self.hand_listbox.insert(tk.END, f"{i}: {str(card)}")
        
        # Enable/disable buttons based on game state
        human_turn = current_player.is_human
        self.play_btn.config(state=tk.NORMAL if human_turn and current_player.hand else tk.DISABLED)
        self.draw_btn.config(state=tk.NORMAL if human_turn else tk.DISABLED)
    
    def play_selected_card(self):
        if not self.game_active:
            return
        
        player = self.players[self.current_player_index]
        if not player.is_human:
            return
        
        try:
            selection = self.hand_listbox.curselection()[0]
            card = player.hand[selection]
            
            if not self.valid_play(card):
                messagebox.showwarning("Invalid Move", "You can't play that card now!")
                return
            
            self.play_card(player, selection)
        except IndexError:
            messagebox.showwarning("Selection Error", "Please select a card to play")
    
    def draw_card(self):
        if not self.game_active:
            return
        
        player = self.players[self.current_player_index]
        if not player.is_human or not self.deck:
            return
        
        # Draw card
        new_card = self.deck.pop()
        player.hand.append(new_card)
        self.log_message(f"{player.name} draws a card")
        
        # Check if playable
        if self.valid_play(new_card):
            play = messagebox.askyesno("Play Card?", f"Do you want to play {new_card}?")
            if play:
                player.hand.remove(new_card)
                self.discard_pile.append(new_card)
                self.log_message(f"{player.name} plays {new_card}")
                self.handle_special_card(new_card)
                
                # Handle color choice for wild cards
                if new_card.type in ['wild', 'wild_draw4']:
                    self.prompt_color_choice()
                
                # Check win condition
                if not player.hand:
                    self.handle_win(player)
                    return
                
                # Handle UNO call
                if len(player.hand) == 1:
                    self.handle_uno(player)
        
        self.next_player()
    
    def play_card(self, player, card_index):
        card = player.hand.pop(card_index)
        self.discard_pile.append(card)
        self.log_message(f"{player.name} plays {card}")
        
        # Handle special card effects
        self.handle_special_card(card)
        
        # Handle color choice for wild cards
        if card.type in ['wild', 'wild_draw4']:
            if player.is_human:
                self.prompt_color_choice()
            else:
                # AI chooses most common color in hand
                colors = [c.color for c in player.hand if c.color]
                self.current_color = max(set(colors), key=colors.count) if colors else random.choice(['Red', 'Blue', 'Green', 'Yellow'])
                self.log_message(f"{player.name} chooses {self.current_color}")
        
        # Check win condition
        if not player.hand:
            self.handle_win(player)
            return
        
        # Handle UNO call
        if len(player.hand) == 1:
            self.handle_uno(player)
        
        self.next_player()
    
    def prompt_color_choice(self):
        color_window = tk.Toplevel(self.root)
        color_window.title("Choose Color")
        color_window.geometry("300x150")
        
        tk.Label(color_window, text="Select a color:", font=("Arial", 12)).pack(pady=10)
        
        btn_frame = tk.Frame(color_window)
        btn_frame.pack(pady=10)
        
        colors = ['Red', 'Blue', 'Green', 'Yellow']
        for color in colors:
            btn = tk.Button(btn_frame, text=color, bg=color.lower(), 
                           command=lambda c=color: self.set_color(c, color_window))
            btn.pack(side=tk.LEFT, padx=5)
    
    def set_color(self, color, window):
        self.current_color = color
        self.log_message(f"Color changed to {color}")
        window.destroy()
        self.update_ui()
    
    def handle_special_card(self, card):
        opponent_index = (self.current_player_index + 1) % 2
        opponent = self.players[opponent_index]
        
        if card.type == 'reverse':
            # In 2-player, reverse acts as skip
            self.skip_next = True
            self.log_message(f"Reverse played! Next player skipped")
        
        elif card.type == 'skip':
            self.skip_next = True
            self.log_message(f"Skip played! Next player skipped")
        
        elif card.type == 'draw2':
            for _ in range(2):
                if self.deck:
                    opponent.hand.append(self.deck.pop())
            self.log_message(f"{opponent.name} draws 2 cards")
            self.skip_next = True
        
        elif card.type == 'wild_draw4':
            # Challenge mechanism
            if opponent.is_human:
                challenge = messagebox.askyesno("Challenge?", "Challenge Wild Draw 4?")
            else:
                # AI challenges only if it has current color
                has_color = any(c.color == self.current_color for c in opponent.hand)
                challenge = has_color
            
            if challenge:
                self.log_message(f"{opponent.name} challenges!")
                if any(c.color == self.current_color for c in self.players[self.current_player_index].hand):
                    # Challenger wins, current player draws 4
                    for _ in range(4):
                        if self.deck:
                            self.players[self.current_player_index].hand.append(self.deck.pop())
                    self.log_message(f"Challenge successful! {self.players[self.current_player_index].name} draws 4 cards")
                else:
                    # Challenge fails, opponent draws 6
                    for _ in range(6):
                        if self.deck:
                            opponent.hand.append(self.deck.pop())
                    self.log_message(f"Challenge failed! {opponent.name} draws 6 cards")
            else:
                # No challenge, opponent draws 4
                for _ in range(4):
                    if self.deck:
                        opponent.hand.append(self.deck.pop())
                self.log_message(f"{opponent.name} draws 4 cards")
            
            self.skip_next = True
    
    def handle_uno(self, player):
        if player.is_human:
            uno_said = messagebox.askyesno("UNO!", "Say UNO!")
            player.uno_not_said = not uno_said
        else:
            player.uno_not_said = False
        
        if player.uno_not_said:
            self.log_message(f"{player.name} forgot to say UNO!")
        else:
            self.log_message(f"{player.name} says UNO!")
    
    def handle_win(self, player):
        self.log_message(f"=== {player.name} WINS THE ROUND! ===")
        self.game_active = False
        messagebox.showinfo("Game Over", f"{player.name} wins the round!")
    
    def next_player(self):
        if self.skip_next:
            self.skip_next = False
            self.log_message("Skipping next player")
            self.current_player_index = (self.current_player_index + 1) % 2
        
        self.current_player_index = (self.current_player_index + 1) % 2
        
        # Replenish deck if needed
        if not self.deck and self.discard_pile:
            self.log_message("Reshuffling discard pile into deck")
            top_card = self.discard_pile.pop()
            self.deck = self.discard_pile
            random.shuffle(self.deck)
            self.discard_pile = [top_card]
        
        self.update_ui()
        
        # Computer's turn
        current_player = self.players[self.current_player_index]
        if not current_player.is_human and self.game_active:
            self.root.after(1500, self.computer_move)
    
    def computer_move(self):
        if not self.game_active:
            return
        
        player = self.players[self.current_player_index]
        self.log_message(f"{player.name}'s turn")
        
        # Find playable cards
        playable_cards = [card for card in player.hand if self.valid_play(card)]
        
        # Play card if possible
        if playable_cards:
            # Prefer non-wild cards
            non_wild = [card for card in playable_cards if card.type not in ['wild', 'wild_draw4']]
            card_to_play = non_wild[0] if non_wild else playable_cards[0]
            
            card_index = player.hand.index(card_to_play)
            self.play_card(player, card_index)
        else:
            # Draw a card
            if self.deck:
                new_card = self.deck.pop()
                player.hand.append(new_card)
                self.log_message(f"{player.name} draws a card")
                
                # Play if possible
                if self.valid_play(new_card):
                    self.log_message(f"{player.name} plays {new_card}")
                    player.hand.remove(new_card)
                    self.discard_pile.append(new_card)
                    self.handle_special_card(new_card)
                    
                    if new_card.type in ['wild', 'wild_draw4']:
                        colors = [c.color for c in player.hand if c.color]
                        self.current_color = max(set(colors), key=colors.count) if colors else random.choice(['Red', 'Blue', 'Green', 'Yellow'])
                        self.log_message(f"{player.name} chooses {self.current_color}")
                    
                    if not player.hand:
                        self.handle_win(player)
                        return
                    
                    if len(player.hand) == 1:
                        self.handle_uno(player)
                else:
                    self.next_player()
            else:
                self.next_player()

if __name__ == "__main__":
    UnoGame()
