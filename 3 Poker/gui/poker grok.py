import tkinter as tk
from tkinter import messagebox
from collections import namedtuple, Counter
import random

Card = namedtuple('Card', ['rank', 'suit'])

def card_str(card):
    return f"{card.rank}{card.suit}"

def rank_to_num(rank):
    if rank.isdigit():
        return int(rank)
    elif rank == 'J':
        return 11
    elif rank == 'Q':
        return 12
    elif rank == 'K':
        return 13
    elif rank == 'A':
        return 14

def create_deck():
    ranks = [str(i) for i in range(2,11)] + ['J', 'Q', 'K', 'A']
    suits = ['S', 'H', 'D', 'C']
    return [Card(rank, suit) for suit in suits for rank in ranks]

class Player:
    def __init__(self, id):
        self.id = id
        self.hand = []
        self.stack = 100
        self.folded = False
        self.bet_this_round = 0

def is_straight_check(sorted_ranks):
    if set(sorted_ranks) == {2,3,4,5,14}:
        return True, 5
    elif max(sorted_ranks) - min(sorted_ranks) == 4 and len(set(sorted_ranks)) == 5:
        return True, max(sorted_ranks)
    else:
        return False, 0

def evaluate_hand(hand):
    ranks = [rank_to_num(card.rank) for card in hand]
    suits = [card.suit for card in hand]
    sorted_ranks = sorted(ranks)
    is_flush = len(set(suits)) == 1
    is_straight, straight_high = is_straight_check(sorted_ranks)
    if is_straight and is_flush:
        return 8, [straight_high] if straight_high != 5 else [5]
    rank_counts = Counter(ranks)
    four_count = [r for r, c in rank_counts.items() if c == 4]
    if four_count:
        kicker = max([r for r in ranks if r != four_count[0]])
        return 7, [four_count[0], kicker]
    three_count = [r for r, c in rank_counts.items() if c == 3]
    two_count = [r for r, c in rank_counts.items() if c == 2]
    if three_count and len(two_count) == 1:
        return 6, [three_count[0], two_count[0]]
    if is_flush:
        return 5, sorted(ranks, reverse=True)
    if is_straight:
        return 4, [straight_high]
    if three_count:
        kickers = sorted([r for r in ranks if r != three_count[0]], reverse=True)
        return 3, [three_count[0]] + kickers
    if len(two_count) == 2:
        pair1, pair2 = sorted(two_count, reverse=True)
        kicker = max([r for r in ranks if r not in (pair1, pair2)])
        return 2, [pair1, pair2, kicker]
    if len(two_count) == 1:
        pair = two_count[0]
        kickers = sorted([r for r in ranks if r != pair], reverse=True)
        return 1, [pair] + kickers
    return 0, sorted(ranks, reverse=True)

class PokerGame:
    def __init__(self, root):
        self.root = root
        self.root.title("5-Card Draw Poker")
        self.deck = create_deck()
        random.shuffle(self.deck)
        self.players = [Player(1), Player(2)]
        self.pot = 0
        self.ante = 5
        self.current_player = 0
        self.round_num = 0
        self.bets = [0, 0]
        self.current_bet = 0
        self.game_over = False

        self.log_text = tk.Text(root, height=15, width=50, state='disabled')
        self.log_text.pack()

        self.status_label = tk.Label(root, text="")
        self.status_label.pack()

        self.entry = tk.Entry(root)
        self.entry.pack()

        self.action_button = tk.Button(root, text="Action", command=self.perform_action)
        self.action_button.pack()

        self.new_game_button = tk.Button(root, text="New Game", command=self.new_game)
        self.new_game_button.pack()

        self.new_game()

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)

    def new_game(self):
        self.deck = create_deck()
        random.shuffle(self.deck)
        for player in self.players:
            player.hand = [self.deck.pop() for _ in range(5)]
            player.stack = 100
            player.folded = False
            player.bet_this_round = 0
        self.pot = 0
        self.current_player = 0
        self.round_num = 0
        self.bets = [0, 0]
        self.current_bet = 0
        self.game_over = False
        self.log("New game started.")
        self.ante_phase()

    def ante_phase(self):
        for player in self.players:
            player.stack -= self.ante
            self.pot += self.ante
        self.log(f"Ante: {self.ante} from each player. Pot: {self.pot}")
        self.start_betting_round()

    def start_betting_round(self):
        self.bets = [0, 0]
        self.current_bet = 0
        self.current_player = 0 if self.round_num == 0 else 1
        self.prompt_player_action()

    def prompt_player_action(self):
        player = self.players[self.current_player]
        if player.folded:
            self.next_player()
            return
        to_call = self.current_bet - self.bets[self.current_player]
        self.status_label.config(text=f"Player {player.id}, your turn. Stack: {player.stack}, Pot: {self.pot}")
        self.log(f"Player {player.id}'s hand: {[card_str(card) for card in player.hand]}")
        if to_call > 0:
            self.log(f"Player {player.id}, call {to_call} or fold. Enter 'call' or 'fold'.")
        else:
            self.log(f"Player {player.id}, enter 'bet <amount>' or 'check'.")

    def perform_action(self):
        player = self.players[self.current_player]
        action = self.entry.get().strip().lower()
        self.entry.delete(0, tk.END)
        if player.folded:
            self.next_player()
            return
        to_call = self.current_bet - self.bets[self.current_player]
        if to_call > 0:
            if action == 'call':
                if to_call > player.stack:
                    messagebox.showerror("Error", "Not enough chips to call.")
                    return
                player.stack -= to_call
                self.pot += to_call
                self.bets[self.current_player] += to_call
                self.log(f"Player {player.id} calls {to_call}.")
            elif action == 'fold':
                player.folded = True
                self.log(f"Player {player.id} folds.")
            else:
                messagebox.showerror("Error", "Invalid action. Enter 'call' or 'fold'.")
                return
        else:
            if action.startswith('bet '):
                try:
                    bet_amount = int(action.split()[1])
                    if bet_amount > player.stack:
                        messagebox.showerror("Error", "Not enough chips to bet.")
                        return
                    player.stack -= bet_amount
                    self.pot += bet_amount
                    self.bets[self.current_player] += bet_amount
                    self.current_bet = max(self.bets)
                    self.log(f"Player {player.id} bets {bet_amount}.")
                except (ValueError, IndexError):
                    messagebox.showerror("Error", "Invalid bet amount.")
                    return
            elif action == 'check':
                self.log(f"Player {player.id} checks.")
            else:
                messagebox.showerror("Error", "Invalid action. Enter 'bet <amount>' or 'check'.")
                return
        self.next_player()

    def next_player(self):
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) < 2:
            self.end_hand()
            return
        self.current_player = (self.current_player + 1) % 2
        if self.bets[0] == self.bets[1]:
            if self.round_num == 0:
                self.round_num = 1
                self.discard_phase()
            else:
                self.end_hand()
        else:
            self.prompt_player_action()

    def discard_phase(self):
        for player in self.players:
            if not player.folded:
                self.log(f"Player {player.id}, enter cards to discard (e.g., '2S 3H' or 'none'):")
                discards = self.entry.get().strip().split()
                self.entry.delete(0, tk.END)
                if discards and discards[0].lower() != 'none':
                    discard_cards = [Card(d[:-1], d[-1]) for d in discards if d]
                    if len(discard_cards) > 3:
                        messagebox.showerror("Error", "Cannot discard more than 3 cards.")
                        continue
                    for card in discard_cards:
                        if card in player.hand:
                            player.hand.remove(card)
                            player.hand.append(self.deck.pop())
                        else:
                            messagebox.showerror("Error", f"Card {card_str(card)} not in hand.")
                            continue
                self.log(f"Player {player.id}'s new hand: {[card_str(card) for card in player.hand]}")
        self.start_betting_round()

    def end_hand(self):
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) == 1:
            winner = active_players[0]
        else:
            hand_values = [(evaluate_hand(p.hand), p) for p in active_players]
            winner = max(hand_values, key=lambda x: (x[0][0], x[0][1]))[1]
        self.log(f"Player {winner.id} wins pot {self.pot} with hand: {[card_str(card) for card in winner.hand]}")
        winner.stack += self.pot
        self.game_over = True
        self.action_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    game = PokerGame(root)
    root.mainloop()
