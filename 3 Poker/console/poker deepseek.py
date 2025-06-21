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
    
    def betting_round(self, start_idx):
        active_players = [p for p in self.players if not p.folded]
        idx = start_idx % len(active_players)
        max_bet = max(self.current_bets.values())
        
        while any(p.can_act and not p.folded for p in active_players):
            player = active_players[idx]
            if not player.can_act or player.folded:
                idx = (idx + 1) % len(active_players)
                continue
            
            call_amount = max_bet - self.current_bets[player]
            action, amount = player.make_decision(call_amount, max_bet)
            
            if action == "fold":
                player.folded = True
            elif action == "call":
                player.chips -= call_amount
                self.pot += call_amount
                self.current_bets[player] += call_amount
                player.can_act = False
            elif action == "raise":
                total_raise = call_amount + amount
                player.chips -= total_raise
                self.pot += total_raise
                self.current_bets[player] = max_bet + amount
                max_bet = self.current_bets[player]
                player.can_act = False
                for p in active_players:
                    if p != player and not p.folded:
                        p.can_act = True
            
            idx = (idx + 1) % len(active_players)
            active_players = [p for p in self.players if not p.folded]
            if len(active_players) == 1:
                break

class Player:
    def __init__(self, name, chips, is_human=False):
        self.name = name
        self.chips = chips
        self.hand = []
        self.folded = False
        self.can_act = True
        self.is_human = is_human
    
    def make_decision(self, call_amount, current_bet):
        if self.is_human:
            print(f"\nYour hand: {self.hand}")
            print(f"Your chips: {self.chips}, Call: {call_amount}, Current bet: {current_bet}")
            while True:
                action = input("Action (fold/call/raise): ").lower()
                if action == "fold":
                    return "fold", 0
                elif action == "call":
                    if call_amount <= self.chips:
                        return "call", 0
                    print("Not enough chips to call")
                elif action == "raise":
                    try:
                        amount = int(input("Raise amount: "))
                        if amount > self.chips - call_amount:
                            print("Not enough chips")
                        elif amount < 1:
                            print("Invalid amount")
                        else:
                            return "raise", amount
                    except ValueError:
                        print("Invalid input")
        else:
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

def main():
    human = Player("You", 100, is_human=True)
    bots = [Player(f"Bot {i+1}", 100) for i in range(3)]
    game = PokerGame([human] + bots)
    
    while any(player.chips > 0 for player in game.players):
        game.reset_game()
        game.ante_up(5)
        game.deal_cards()
        
        for player in game.players:
            player.can_act = True
        
        game.betting_round(0)
        
        if sum(1 for p in game.players if not p.folded) > 1:
            for player in game.players:
                if player.folded:
                    continue
                if player.is_human:
                    print(f"\nYour hand: {player.hand}")
                    discards = input("Discard (0-4, comma separated): ")
                    indices = [int(idx.strip()) for idx in discards.split(",")] if discards else []
                    new_hand = game.draw_cards(player, indices)
                    print(f"New hand: {new_hand}")
                else:
                    discard_count = min(3, random.randint(0, 3))
                    indices = random.sample(range(5), discard_count)
                    game.draw_cards(player, indices)
            
            for player in game.players:
                player.can_act = True
            game.betting_round(1)
        
        winner, hand_type = game.compare_hands({p: p.hand for p in game.players})
        if winner:
            winner.chips += game.pot
            print(f"\nWinner: {winner.name} with {hand_type}!")
            print(f"{winner.name} wins {game.pot} chips")
        else:
            print("All players folded, no winner")
        
        print("\nChip counts:")
        for player in game.players:
            print(f"{player.name}: {player.chips} chips")
        
        if input("\nPlay again? (y/n): ").lower() != 'y':
            break

if __name__ == "__main__":
    main()
