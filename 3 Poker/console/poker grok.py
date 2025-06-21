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

def main():
    deck = create_deck()
    random.shuffle(deck)
    players = [Player(1), Player(2)]
    pot = 0
    ante = 5
    for player in players:
        player.stack -= ante
        pot += ante
    for player in players:
        player.hand = [deck.pop() for _ in range(5)]
    for player in players:
        print(f"Player {player.id} hand: {[card_str(card) for card in player.hand]}")
    current_bet = 0
    for round_num in range(2):
        if round_num == 1:
            for player in players:
                if not player.folded:
                    print(f"Player {player.id}, your hand: {[card_str(card) for card in player.hand]}")
                    discards = input("Enter cards to discard (e.g., 2S 3H, or none): ").split()
                    discard_cards = [Card(d[:-1], d[-1]) for d in discards if d] if discards else []
                    if len(discard_cards) > 3:
                        print("Cannot discard more than 3 cards.")
                        continue
                    for card in discard_cards:
                        if card in player.hand:
                            player.hand.remove(card)
                            player.hand.append(deck.pop())
                        else:
                            print(f"Card {card_str(card)} not in hand.")
        bets = [0, 0]
        active_players = [p for p in players if not p.folded]
        if len(active_players) < 2:
            break
        start_player = 0 if round_num == 0 else 1
        while True:
            all_called = True
            for i in range(len(active_players)):
                player_idx = (start_player + i) % len(players)
                player = players[player_idx]
                if player.folded:
                    continue
                to_call = current_bet - bets[player_idx]
                print(f"Player {player.id} stack: {player.stack}, pot: {pot}")
                if to_call > 0:
                    action = input(f"Player {player.id}, call {to_call}? (call/fold): ")
                    if action == 'fold':
                        player.folded = True
                    else:
                        if to_call > player.stack:
                            print("Not enough chips to call.")
                            continue
                        player.stack -= to_call
                        pot += to_call
                        bets[player_idx] += to_call
                else:
                    action = input(f"Player {player.id}, bet/raise or check? (bet/check): ")
                    if action == 'bet':
                        bet_amount = int(input("Enter bet amount: "))
                        if bet_amount > player.stack:
                            print("Not enough chips to bet.")
                            continue
                        player.stack -= bet_amount
                        pot += bet_amount
                        bets[player_idx] += bet_amount
                        current_bet = max(bets)
                        all_called = False
            if all_called or len([p for p in active_players if not p.folded]) < 2:
                break
    active_players = [p for p in players if not p.folded]
    if len(active_players) == 1:
        winner = active_players[0]
    else:
        hand_values = [(evaluate_hand(p.hand), p) for p in active_players]
        winner = max(hand_values, key=lambda x: (x[0][0], x[0][1]))[1]
    print(f"Player {winner.id} wins the pot of {pot} with hand: {[card_str(card) for card in winner.hand]}")
    winner.stack += pot

if __name__ == "__main__":
    main()
