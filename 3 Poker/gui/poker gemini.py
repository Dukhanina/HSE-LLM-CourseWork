import random
import tkinter as tk
from tkinter import messagebox, scrolledtext

class PokerGame:
    def __init__(self, player_names, gui_app):
        self.gui_app = gui_app
        self.deck = self._create_deck()
        self.players = {name: [] for name in player_names}
        self.pot = 0
        self.dealer_index = 0
        self.ante_amount = 0.05
        self.current_bet = 0
        self.player_bets = {name: 0 for name in player_names}
        self.active_players = list(self.players.keys())
        self.current_player_index = 0
        self.round_complete = False

    def _create_deck(self):
        suits = ['s', 'h', 'd', 'c']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        return [r + s for r in ranks for r in suits]

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def deal_cards(self, num_cards=5):
        for _ in range(num_cards):
            for player_name in self.players:
                self.players[player_name].append(self.deck.pop(0))

    def ante(self):
        for player_name in self.players:
            self.pot += self.ante_amount
        self.gui_app.log_message(f"All players ante {self.ante_amount:.2f}. Pot is now {self.pot:.2f}.")

    def start_betting_round(self):
        self.current_bet = 0
        self.player_bets = {name: 0 for name in self.players}
        self.active_players = list(self.players.keys())
        player_order, _ = self._get_player_order()
        self.active_players_in_order = [p for p in player_order if p in self.active_players]
        self.current_player_index = 0
        self.round_complete = False
        self.gui_app.update_game_state()
        self.gui_app.enable_player_input()
        self.next_player_turn()

    def _get_player_order(self):
        player_names = list(self.players.keys())
        dealer_name = player_names[self.dealer_index]
        player_order = player_names[self.dealer_index + 1:] + player_names[:self.dealer_index + 1]
        return player_order, dealer_name

    def next_player_turn(self):
        if len(self.active_players) <= 1:
            self.end_betting_round()
            return
            
        current_player_name = self.active_players_in_order[self.current_player_index]
        
        # Skip folded players
        while current_player_name not in self.active_players:
            self.current_player_index = (self.current_player_index + 1) % len(self.active_players_in_order)
            current_player_name = self.active_players_in_order[self.current_player_index]
            if len(self.active_players) <= 1: # Check again if only one player left after skipping
                self.end_betting_round()
                return

        self.gui_app.log_message(f"\n--- {current_player_name}'s turn ---")
        self.gui_app.log_message(f"Your hand: {self.players[current_player_name]}")
        self.gui_app.log_message(f"Current pot: {self.pot:.2f}. Bet to match: {self.current_bet:.2f}")
        
        self.gui_app.current_player_label.config(text=f"Current Player: {current_player_name}")
        self.gui_app.update_game_state()

    def process_player_action(self, player_name, action, amount=0):
        if player_name not in self.active_players:
            self.gui_app.show_error("It's not your turn or you have folded.")
            return

        bet_needed = self.current_bet - self.player_bets[player_name]

        if action == 'call':
            if bet_needed > 0:
                self.pot += bet_needed
                self.player_bets[player_name] += bet_needed
                self.gui_app.log_message(f"{player_name} calls, adding {bet_needed:.2f} to the pot.")
            else:
                self.gui_app.log_message(f"{player_name} checks.")
            self.advance_turn()

        elif action == 'raise':
            if amount <= 0 or amount > 0.50:
                self.gui_app.show_error("Invalid raise amount. Max raise is $0.50.")
                return

            total_bet_this_turn = bet_needed + amount
            self.pot += total_bet_this_turn
            self.player_bets[player_name] += total_bet_this_turn
            self.current_bet += amount 
            self.gui_app.log_message(f"{player_name} raises by {amount:.2f}, total bet {self.current_bet:.2f}. Pot is now {self.pot:.2f}.")
            
            # Reset current player index to ensure everyone gets to respond to the raise
            self.current_player_index = (self.active_players_in_order.index(player_name) + 1) % len(self.active_players_in_order)
            self.round_complete = False # A raise means the round is not complete
            self.advance_turn(raised=True)

        elif action == 'fold':
            self.active_players.remove(player_name)
            self.gui_app.log_message(f"{player_name} folds.")
            self.advance_turn()
        else:
            self.gui_app.show_error("Invalid action.")

        self.gui_app.update_game_state()
        if not self.round_complete:
            self.next_player_turn()

    def advance_turn(self, raised=False):
        if raised:
            # When someone raises, the turn goes to the next player, and then circles back to the raiser
            # if no one else raises. The round isn't complete until everyone has called or folded.
            self.current_player_index = (self.current_player_index + 1) % len(self.active_players_in_order)
        else:
            self.current_player_index = (self.current_player_index + 1) % len(self.active_players_in_order)

        if self.current_player_index == self.active_players_in_order.index(self.active_players[0]) and not raised:
            # This logic needs refinement for a truly robust betting round where everyone calls/folds after a raise.
            # For simplicity, we'll assume a round ends when it comes back to the initial bettor or everyone calls.
            # A more complex state machine is needed for full compliance with poker betting rules.
            # Here, we'll check if everyone has matched the current bet.
            all_called = True
            for player in self.active_players:
                if self.player_bets[player] != self.current_bet:
                    all_called = False
                    break
            if all_called:
                self.round_complete = True
            
        if self.round_complete or len(self.active_players) <= 1:
            self.end_betting_round()

    def end_betting_round(self):
        self.gui_app.log_message("Betting round over.")
        self.gui_app.disable_player_input()
        if len(self.active_players) <= 1:
            if self.active_players:
                self.gui_app.log_message(f"{self.active_players[0]} wins the pot as all other players folded.")
                self.pot = 0
            self.gui_app.new_game_button.config(state=tk.NORMAL)
            return
        
        # After first betting round, allow discard and draw
        if self.gui_app.game_stage == "first_betting":
            self.gui_app.game_stage = "discard_draw"
            self.gui_app.log_message("\n--- Discard and Draw Phase ---")
            self.gui_app.enable_discard_input()
            self.gui_app.current_player_index_for_discard = 0
            self.prompt_discard_for_next_player()
        elif self.gui_app.game_stage == "second_betting":
            self.gui_app.game_stage = "showdown"
            self.determine_winner(self.active_players)
            self.gui_app.new_game_button.config(state=tk.NORMAL)


    def prompt_discard_for_next_player(self):
        if self.gui_app.current_player_index_for_discard >= len(self.active_players):
            self.gui_app.disable_discard_input()
            self.gui_app.game_stage = "second_betting"
            self.gui_app.log_message("\n--- Starting Second Betting Round ---")
            self.start_betting_round()
            return

        player_name = self.active_players[self.gui_app.current_player_index_for_discard]
        self.gui_app.current_player_label.config(text=f"Current Player for Discard: {player_name}")
        self.gui_app.log_message(f"\n{player_name}'s turn to discard. Your hand: {self.players[player_name]}")


    def process_discard_draw(self, player_name, discard_indices_str):
        if player_name not in self.active_players:
            self.gui_app.show_error("It's not your turn for discard.")
            return

        discard_indices = []
        if discard_indices_str:
            try:
                discard_indices = sorted([int(x) for x in discard_indices_str.split()])
                if not all(0 <= i < len(self.players[player_name]) for i in discard_indices):
                    self.gui_app.show_error("Invalid card index. Please enter indices within your hand's range.")
                    return
                if len(discard_indices) > 3: # Can discard up to 3 cards [cite: 49]
                    self.gui_app.show_error("You can discard a maximum of 3 cards.")
                    return
            except ValueError:
                self.gui_app.show_error("Invalid input. Please enter numbers separated by spaces.")
                return

        new_hand = [card for i, card in enumerate(self.players[player_name]) if i not in discard_indices]
        num_to_draw = len(discard_indices)
        
        for _ in range(num_to_draw):
            if self.deck:
                new_hand.append(self.deck.pop(0))
            else:
                self.gui_app.log_message("Deck is empty!")
                break
        self.players[player_name] = new_hand
        self.gui_app.log_message(f"{player_name}'s new hand: {self.players[player_name]}")

        self.gui_app.current_player_index_for_discard += 1
        self.prompt_discard_for_next_player()


    def _rank_hand(self, hand):
        ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        card_ranks_numerical = sorted([ranks[card[0]] for card in hand])
        card_suits = [card[1] for card in hand]

        is_flush = len(set(card_suits)) == 1
        
        # Check for straight
        is_straight = True
        if 14 in card_ranks_numerical and 2 in card_ranks_numerical and 3 in card_ranks_numerical and 4 in card_ranks_numerical and 5 in card_ranks_numerical:
            # [cite_start]Special case for A-2-3-4-5 straight (Ace as low) [cite: 15, 26]
            straight_ranks = [1, 2, 3, 4, 5]
        else:
            straight_ranks = card_ranks_numerical
            for i in range(len(straight_ranks) - 1):
                if straight_ranks[i+1] != straight_ranks[i] + 1:
                    is_straight = False
                    break
        
        if len(set(card_ranks_numerical)) < 5: # Not possible to be a straight if there are duplicates
            is_straight = False

        rank_counts = {}
        for r in card_ranks_numerical:
            rank_counts[r] = rank_counts.get(r, 0) + 1

        counts_list = sorted(rank_counts.values(), reverse=True)
        unique_ranks = sorted(rank_counts.keys(), reverse=True)

        # [cite_start]Poker hand rankings [cite: 11]
        if 5 in counts_list: # Five of a Kind [cite: 12]
            return (9, unique_ranks[0]) 
        if is_straight and is_flush: # Straight Flush [cite: 14]
            if card_ranks_numerical == [10, 11, 12, 13, 14]:
                return (8, 14)  # Royal Flush [cite: 17]
            return (8, card_ranks_numerical[-1])
        if 4 in counts_list: # Four of a Kind [cite: 18]
            return (7, unique_ranks[0], unique_ranks[1] if len(unique_ranks) > 1 else 0)
        if counts_list == [3, 2]: # Full House [cite: 22]
            return (6, unique_ranks[0], unique_ranks[1])
        if is_flush: # Flush [cite: 24]
            return (5, *unique_ranks)
        if is_straight: # Straight [cite: 25]
            return (4, straight_ranks[-1])
        if 3 in counts_list: # Three of a Kind [cite: 29]
            return (3, unique_ranks[0], unique_ranks[1] if len(unique_ranks) > 1 else 0, unique_ranks[2] if len(unique_ranks) > 2 else 0)
        if counts_list == [2, 2, 1]: # Two Pair [cite: 30]
            return (2, unique_ranks[0], unique_ranks[1], unique_ranks[2])
        if 2 in counts_list: # Pair [cite: 31]
            return (1, unique_ranks[0], unique_ranks[1] if len(unique_ranks) > 1 else 0, unique_ranks[2] if len(unique_ranks) > 2 else 0, unique_ranks[3] if len(unique_ranks) > 3 else 0)
        return (0, *unique_ranks) # High Card [cite: 32]

    def determine_winner(self, active_players):
        hand_strengths = {}
        for player_name in active_players:
            hand_strengths[player_name] = self._rank_hand(self.players[player_name])
            self.gui_app.log_message(f"{player_name}'s hand: {self.players[player_name]} - Strength: {hand_strengths[player_name]}")

        if not hand_strengths:
            self.gui_app.log_message("No active players to determine a winner.")
            return

        winner = max(hand_strengths, key=hand_strengths.get)
        self.gui_app.log_message(f"\n{winner} wins the pot of {self.pot:.2f} with {self.players[winner]} (strength: {hand_strengths[winner]})!")
        self.pot = 0

    def play_hand(self):
        self.deck = self._create_deck()
        self.shuffle_deck()
        self.pot = 0
        for player_name in self.players:
            self.players[player_name] = []

        self.ante()
        self.deal_cards()
        
        self.gui_app.game_stage = "first_betting"
        self.start_betting_round()

class PokerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Basic Poker Game")

        self.game = None
        self.player_names = ["Alex", "Brad", "Charley", "Dennis", "You"] # Default players

        # Game State
        self.game_stage = "" # "first_betting", "discard_draw", "second_betting", "showdown"
        self.current_player_index_for_discard = 0

        # Widgets
        self.log_text = scrolledtext.ScrolledText(master, state='disabled', width=80, height=20)
        self.log_text.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

        self.new_game_button = tk.Button(master, text="New Game", command=self.start_new_game)
        self.new_game_button.grid(row=1, column=0, columnspan=4, pady=5)

        self.current_player_label = tk.Label(master, text="Current Player:")
        self.current_player_label.grid(row=2, column=0, columnspan=4)

        self.player_action_frame = tk.LabelFrame(master, text="Player Actions")
        self.player_action_frame.grid(row=3, column=0, columnspan=4, padx=5, pady=5)

        self.call_button = tk.Button(self.player_action_frame, text="Call", command=lambda: self.perform_action('call'))
        self.call_button.grid(row=0, column=0, padx=2, pady=2)

        self.raise_button = tk.Button(self.player_action_frame, text="Raise", command=lambda: self.perform_action('raise'))
        self.raise_button.grid(row=0, column=1, padx=2, pady=2)

        self.raise_amount_entry = tk.Entry(self.player_action_frame, width=10)
        self.raise_amount_entry.grid(row=0, column=2, padx=2, pady=2)
        self.raise_amount_entry.insert(0, "0.10") # Default raise amount

        self.fold_button = tk.Button(self.player_action_frame, text="Fold", command=lambda: self.perform_action('fold'))
        self.fold_button.grid(row=0, column=3, padx=2, pady=2)

        self.discard_frame = tk.LabelFrame(master, text="Discard Cards")
        self.discard_frame.grid(row=4, column=0, columnspan=4, padx=5, pady=5)

        self.discard_entry_label = tk.Label(self.discard_frame, text="Discard indices (e.g., 0 2 4):")
        self.discard_entry_label.grid(row=0, column=0, padx=2, pady=2)
        self.discard_entry = tk.Entry(self.discard_frame, width=20)
        self.discard_entry.grid(row=0, column=1, padx=2, pady=2)
        self.discard_button = tk.Button(self.discard_frame, text="Discard", command=self.perform_discard)
        self.discard_button.grid(row=0, column=2, padx=2, pady=2)

        self.disable_player_input()
        self.disable_discard_input()

    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def update_game_state(self):
        if self.game:
            self.log_text.config(state='normal')
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state='disabled')
            self.log_message(f"Pot: {self.game.pot:.2f}")
            for name, hand in self.game.players.items():
                self.log_message(f"{name}'s hand: {' '.join(hand)}")
            self.log_message(f"Current bet: {self.game.current_bet:.2f}")

    def disable_player_input(self):
        self.call_button.config(state=tk.DISABLED)
        self.raise_button.config(state=tk.DISABLED)
        self.raise_amount_entry.config(state=tk.DISABLED)
        self.fold_button.config(state=tk.DISABLED)

    def enable_player_input(self):
        self.call_button.config(state=tk.NORMAL)
        self.raise_button.config(state=tk.NORMAL)
        self.raise_amount_entry.config(state=tk.NORMAL)
        self.fold_button.config(state=tk.NORMAL)

    def disable_discard_input(self):
        self.discard_entry.config(state=tk.DISABLED)
        self.discard_button.config(state=tk.DISABLED)

    def enable_discard_input(self):
        self.discard_entry.config(state=tk.NORMAL)
        self.discard_button.config(state=tk.NORMAL)

    def start_new_game(self):
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        self.log_message("Starting a new game...")
        self.game = PokerGame(self.player_names, self)
        self.new_game_button.config(state=tk.DISABLED)
        self.game.play_hand()

    def perform_action(self, action_type):
        current_player_name = self.game.active_players_in_order[self.game.current_player_index]
        if current_player_name != "You": # Assuming "You" is the human player
            self.show_error("It's not your turn.")
            return

        amount = 0
        if action_type == 'raise':
            try:
                amount = float(self.raise_amount_entry.get())
            except ValueError:
                self.show_error("Invalid raise amount. Please enter a number.")
                return

        self.game.process_player_action(current_player_name, action_type, amount)
        self.raise_amount_entry.delete(0, tk.END)
        self.raise_amount_entry.insert(0, "0.10") # Reset default for next raise

    def perform_discard(self):
        current_player_name = self.game.active_players[self.current_player_index_for_discard]
        if current_player_name != "You": # Assuming "You" is the human player
            self.show_error("It's not your turn to discard.")
            return

        discard_input = self.discard_entry.get()
        self.game.process_discard_draw(current_player_name, discard_input)
        self.discard_entry.delete(0, tk.END)

def main():
    root = tk.Tk()
    gui = PokerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
