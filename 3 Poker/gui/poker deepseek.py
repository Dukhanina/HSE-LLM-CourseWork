import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import random
from collections import Counter

class PokerGame:
    SUITS = ['♠', '♥', '♦', '♣']
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    HAND_RANKS = [
        "High Card", "Pair", "Two Pair", "Three of a Kind", "Straight",
        "Flush", "Full House", "Four of a Kind", "Straight Flush"
    ]
    
    def __init__(self, players):
        self.players = players
        self.deck = []
        self.pot = 0
        self.current_bets = {}
        self.discards = {}
        self.reset_game()
        
    def reset_game(self):
        self.deck = [(suit, rank) for suit in self.SUITS for rank in self.RANKS]
        random.shuffle(self.deck)
        self.pot = 0
        self.current_bets = {player: 0 for player in self.players}
        self.discards = {player: [] for player in self.players}
        for player in self.players:
            player.hand = []
            player.folded = False
            player.can_act = True
    
    def deal_cards(self):
        for _ in range(5):
            for player in self.players:
                player.hand.append(self.deck.pop())
    
    def ante_up(self, amount):
        for player in self.players:
            player.chips -= amount
            self.pot += amount
            self.current_bets[player] = amount
    
    def draw_cards(self, player, discard_indices):
        new_cards = []
        for idx in sorted(discard_indices, reverse=True):
            self.discards[player].append(player.hand.pop(idx))
        for _ in range(len(discard_indices)):
            if self.deck:
                player.hand.append(self.deck.pop())
        return player.hand
    
    def evaluate_hand(self, hand):
        values = sorted([self.RANKS.index(card[1]) for card in hand], reverse=True)
        suits = [card[0] for card in hand]
        value_counter = Counter(values)
        is_flush = len(set(suits)) == 1
        is_straight = len(set(values)) == 5 and (max(values) - min(values) == 4 or set(values) == {12, 3, 2, 1, 0})
        straight_high = min(values) if values == [12, 3, 2, 1, 0] else max(values)
        
        if is_straight and is_flush:
            return (8, straight_high)
        if 4 in value_counter.values():
            quad_value = next(val for val, count in value_counter.items() if count == 4)
            kicker = next(val for val in values if val != quad_value)
            return (7, quad_value, kicker)
        if 3 in value_counter.values() and 2 in value_counter.values():
            trio = next(val for val, count in value_counter.items() if count == 3)
            pair = next(val for val, count in value_counter.items() if count == 2)
            return (6, trio, pair)
        if is_flush:
            return (5, *values)
        if is_straight:
            return (4, straight_high)
        if 3 in value_counter.values():
            trio = next(val for val, count in value_counter.items() if count == 3)
            kickers = sorted([val for val in values if val != trio], reverse=True)
            return (3, trio, *kickers)
        if list(value_counter.values()).count(2) == 2:
            pairs = sorted([val for val, count in value_counter.items() if count == 2], reverse=True)
            kicker = next(val for val in values if val not in pairs)
            return (2, *pairs, kicker)
        if 2 in value_counter.values():
            pair_val = next(val for val, count in value_counter.items() if count == 2)
            kickers = sorted([val for val in values if val != pair_val], reverse=True)
            return (1, pair_val, *kickers)
        return (0, *values)
    
    def compare_hands(self, hands):
        evaluations = {}
        for player, hand in hands.items():
            if not player.folded:
                evaluations[player] = self.evaluate_hand(hand)
        
        best_player = None
        best_eval = (-1,)
        
        for player, eval_score in evaluations.items():
            if eval_score > best_eval:
                best_eval = eval_score
                best_player = player
        
        return best_player, self.HAND_RANKS[best_eval[0]]

class Player:
    def __init__(self, name, chips, is_human=False):
        self.name = name
        self.chips = chips
        self.hand = []
        self.folded = False
        self.can_act = True
        self.is_human = is_human
    
    def make_decision(self, call_amount, current_bet):
        hand_strength = max(Counter(card[1] for card in self.hand).values(), default=0)
        if call_amount == 0:
            return "call", 0
        if hand_strength < 2 and call_amount > 5:
            return "fold", 0
        if hand_strength == 2 and call_amount > 10:
            return "fold", 0
        if hand_strength >= 3 or random.random() > 0.3:
            if self.chips > call_amount + 5 and random.random() > 0.7:
                raise_amt = min(5, self.chips - call_amount)
                return "raise", raise_amt
            return "call", 0
        return "fold", 0

class PokerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Game")
        self.root.geometry("800x600")
        
        self.game = None
        self.human_player = None
        self.current_state = None
        
        self.create_widgets()
        self.new_game()
    
    def create_widgets(self):
        # Control buttons
        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.pack(pady=10)
        
        self.new_game_btn = tk.Button(self.controls_frame, text="New Game", command=self.new_game)
        self.new_game_btn.pack(side=tk.LEFT, padx=5)
        
        self.fold_btn = tk.Button(self.controls_frame, text="Fold", command=lambda: self.player_action("fold"))
        self.fold_btn.pack(side=tk.LEFT, padx=5)
        
        self.call_btn = tk.Button(self.controls_frame, text="Call", command=lambda: self.player_action("call"))
        self.call_btn.pack(side=tk.LEFT, padx=5)
        
        self.raise_btn = tk.Button(self.controls_frame, text="Raise", command=lambda: self.player_action("raise"))
        self.raise_btn.pack(side=tk.LEFT, padx=5)
        
        self.raise_entry = tk.Entry(self.controls_frame, width=10)
        self.raise_entry.pack(side=tk.LEFT, padx=5)
        self.raise_entry.insert(0, "5")
        
        # Game info
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.pot_label = tk.Label(self.info_frame, text="Pot: $0")
        self.pot_label.pack(side=tk.LEFT, padx=10)
        
        self.current_bet_label = tk.Label(self.info_frame, text="Current Bet: $0")
        self.current_bet_label.pack(side=tk.LEFT, padx=10)
        
        self.player_chips_label = tk.Label(self.info_frame, text="Your Chips: $0")
        self.player_chips_label.pack(side=tk.RIGHT, padx=10)
        
        # Player hand
        self.hand_frame = tk.LabelFrame(self.root, text="Your Hand")
        self.hand_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.hand_label = tk.Label(self.hand_frame, text="No cards yet")
        self.hand_label.pack(pady=10)
        
        # Game log
        self.log_frame = tk.LabelFrame(self.root, text="Game Log")
        self.log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_area = scrolledtext.ScrolledText(self.log_frame, height=15)
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_area.config(state=tk.DISABLED)
    
    def log(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)
    
    def new_game(self):
        self.log("=== Starting new game ===")
        human = Player("You", 100, is_human=True)
        bots = [Player(f"Bot {i+1}", 100) for i in range(3)]
        self.game = PokerGame([human] + bots)
        self.human_player = human
        
        self.game.ante_up(5)
        self.game.deal_cards()
        
        self.update_display()
        self.log("Ante collected: $5 from each player")
        self.log("Cards dealt")
        
        self.current_state = "first_bet"
        self.next_turn()
    
    def update_display(self):
        if self.game and self.human_player:
            self.pot_label.config(text=f"Pot: ${self.game.pot}")
            max_bet = max(self.game.current_bets.values())
            self.current_bet_label.config(text=f"Current Bet: ${max_bet}")
            self.player_chips_label.config(text=f"Your Chips: ${self.human_player.chips}")
            
            hand_text = " ".join([f"{rank}{suit}" for suit, rank in self.human_player.hand])
            self.hand_label.config(text=hand_text)
    
    def next_turn(self):
        if not self.game:
            return
        
        active_players = [p for p in self.game.players if not p.folded]
        human_turn = active_players[0] == self.human_player
        
        if self.current_state in ["first_bet", "second_bet"]:
            max_bet = max(self.game.current_bets.values())
            
            if human_turn:
                call_amount = max_bet - self.game.current_bets[self.human_player]
                self.log(f"\nYour turn. Call: ${call_amount}")
                self.update_buttons(call_amount)
            else:
                player = active_players[0]
                self.log(f"\n{player.name}'s turn")
                self.root.after(1500, lambda: self.bot_action(player))
        
        elif self.current_state == "draw":
            if human_turn:
                self.log("\nYour turn to discard cards")
                self.ask_discard()
            else:
                player = active_players[0]
                self.root.after(1000, lambda: self.bot_discard(player))
    
    def update_buttons(self, call_amount):
        max_bet = max(self.game.current_bets.values())
        human_bet = self.game.current_bets[self.human_player]
        call_needed = max_bet - human_bet
        
        self.fold_btn.config(state=tk.NORMAL)
        self.call_btn.config(state=tk.NORMAL if call_needed <= self.human_player.chips else tk.DISABLED)
        
        can_raise = self.human_player.chips > call_needed
        self.raise_btn.config(state=tk.NORMAL if can_raise else tk.DISABLED)
        self.raise_entry.config(state=tk.NORMAL if can_raise else tk.DISABLED)
    
    def player_action(self, action):
        if not self.human_player.can_act or self.human_player.folded:
            return
        
        call_amount = max(self.game.current_bets.values()) - self.game.current_bets[self.human_player]
        raise_amount = 0
        
        if action == "raise":
            try:
                raise_amount = int(self.raise_entry.get())
                if raise_amount <= 0:
                    messagebox.showerror("Invalid Raise", "Raise amount must be positive")
                    return
                if raise_amount > self.human_player.chips - call_amount:
                    messagebox.showerror("Invalid Raise", "Not enough chips")
                    return
            except ValueError:
                messagebox.showerror("Invalid Raise", "Please enter a valid number")
                return
        
        self.process_action(self.human_player, action, raise_amount)
    
    def bot_action(self, player):
        call_amount = max(self.game.current_bets.values()) - self.game.current_bets[player]
        action, raise_amount = player.make_decision(call_amount, max(self.game.current_bets.values()))
        self.process_action(player, action, raise_amount)
    
    def process_action(self, player, action, raise_amount=0):
        max_bet = max(self.game.current_bets.values())
        call_amount = max_bet - self.game.current_bets[player]
        
        if action == "fold":
            player.folded = True
            self.log(f"{player.name} folds")
        elif action == "call":
            player.chips -= call_amount
            self.game.pot += call_amount
            self.game.current_bets[player] += call_amount
            player.can_act = False
            self.log(f"{player.name} calls ${call_amount}")
        elif action == "raise":
            total_raise = call_amount + raise_amount
            player.chips -= total_raise
            self.game.pot += total_raise
            self.game.current_bets[player] = max_bet + raise_amount
            player.can_act = False
            self.log(f"{player.name} raises by ${raise_amount} (total bet: ${self.game.current_bets[player]})")
            
            # Reset other players' actions
            for p in self.game.players:
                if p != player and not p.folded:
                    p.can_act = True
        
        self.update_display()
        self.advance_game_state()
    
    def advance_game_state(self):
        active_players = [p for p in self.game.players if not p.folded]
        
        # Check if betting round is complete
        if self.current_state in ["first_bet", "second_bet"]:
            if len(active_players) == 1:
                self.showdown()
                return
            
            # All players have either called the max bet or folded
            if all(not p.can_act or p.folded for p in self.game.players):
                if self.current_state == "first_bet":
                    self.current_state = "draw"
                    self.log("\n=== Discard phase ===")
                    for player in active_players:
                        player.can_act = True
                else:
                    self.showdown()
                    return
        
        self.next_turn()
    
    def ask_discard(self):
        self.discard_window = tk.Toplevel(self.root)
        self.discard_window.title("Discard Cards")
        self.discard_window.geometry("300x200")
        self.discard_window.transient(self.root)
        self.discard_window.grab_set()
        
        tk.Label(self.discard_window, text="Select cards to discard (max 3):").pack(pady=10)
        
        self.discard_vars = []
        for i, card in enumerate(self.human_player.hand):
            var = tk.IntVar()
            chk = tk.Checkbutton(self.discard_window, 
                                text=f"{card[1]}{card[0]}", 
                                variable=var)
            chk.pack(anchor=tk.W, padx=20)
            self.discard_vars.append(var)
        
        tk.Button(self.discard_window, text="Confirm", command=self.confirm_discard).pack(pady=10)
    
    def confirm_discard(self):
        discard_indices = [i for i, var in enumerate(self.discard_vars) if var.get() == 1]
        
        if len(discard_indices) > 3:
            messagebox.showerror("Invalid Discard", "You can discard at most 3 cards")
            return
        
        new_hand = self.game.draw_cards(self.human_player, discard_indices)
        self.log(f"You discarded {len(discard_indices)} cards")
        
        hand_text = " ".join([f"{rank}{suit}" for suit, rank in new_hand])
        self.hand_label.config(text=hand_text)
        
        self.discard_window.destroy()
        self.human_player.can_act = False
        self.advance_game_state()
    
    def bot_discard(self, player):
        discard_count = min(3, random.randint(0, 3))
        indices = random.sample(range(5), discard_count)
        self.game.draw_cards(player, indices)
        self.log(f"{player.name} discards {discard_count} cards")
        player.can_act = False
        self.advance_game_state()
    
    def advance_game_state(self):
        active_players = [p for p in self.game.players if not p.folded]
        
        if self.current_state == "draw":
            # Check if all players have discarded
            if all(not p.can_act for p in active_players):
                self.current_state = "second_bet"
                self.log("\n=== Second betting round ===")
                for player in active_players:
                    player.can_act = True
                
                # Reset bets for new round
                max_bet = max(self.game.current_bets.values())
                for player in active_players:
                    self.game.current_bets[player] = 0
        
        self.next_turn()
    
    def showdown(self):
        self.log("\n=== Showdown ===")
        active_players = [p for p in self.game.players if not p.folded]
        
        for player in active_players:
            hand_text = " ".join([f"{rank}{suit}" for suit, rank in player.hand])
            self.log(f"{player.name} shows: {hand_text}")
        
        winner, hand_type = self.game.compare_hands({p: p.hand for p in self.game.players})
        if winner:
            winner.chips += self.game.pot
            self.log(f"\n{winner.name} wins ${self.game.pot} with {hand_type}!")
        else:
            self.log("No winner - all players folded")
        
        self.log("\nFinal chip counts:")
        for player in self.game.players:
            self.log(f"{player.name}: ${player.chips}")
        
        self.current_state = "game_over"
        self.update_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = PokerApp(root)
    root.mainloop()
