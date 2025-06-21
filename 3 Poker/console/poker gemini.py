import random

class PokerGame:
    def __init__(self, players_names):
        self.deck = self._create_deck()
        self.players = {name: [] for name in players_names}
        self.pot = 0
        self.dealer_index = 0
        self.ante_amount = 0.05

    def _create_deck(self):
        suits = ['s', 'h', 'd', 'c']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        return [r + s for r in ranks for s in suits]

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def deal_cards(self, num_cards=5):
        for _ in range(num_cards):
            for player_name in self.players:
                self.players[player_name].append(self.deck.pop(0))

    def ante(self):
        for player_name in self.players:
            self.pot += self.ante_amount
        print(f"All players ante {self.ante_amount:.2f}. Pot is now {self.pot:.2f}.")

    def _get_player_order(self):
        player_names = list(self.players.keys())
        dealer_name = player_names[self.dealer_index]
        player_order = player_names[self.dealer_index + 1:] + player_names[:self.dealer_index + 1]
        return player_order, dealer_name

    def betting_round(self):
        current_bet = 0
        player_bets = {name: 0 for name in self.players}
        active_players = list(self.players.keys())
        players_folded = []

        player_order, _ = self._get_player_order()
        
        round_complete = False
        while not round_complete:
            round_complete = True
            for player_name in player_order:
                if player_name not in active_players:
                    continue

                if len([p for p in active_players if p not in players_folded]) <= 1:
                    break

                print(f"\n{player_name}'s turn. Current pot: {self.pot:.2f}. Your hand: {self.players[player_name]}. Current bet to match: {current_bet:.2f}")
                
                action = input("Enter 'call', 'raise', or 'fold': ").lower()

                if action == 'call':
                    bet_needed = current_bet - player_bets[player_name]
                    if bet_needed > 0:
                        self.pot += bet_needed
                        player_bets[player_name] += bet_needed
                        print(f"{player_name} calls, adding {bet_needed:.2f} to the pot.")
                    else:
                        print(f"{player_name} checks.")
                elif action == 'raise':
                    raise_amount_str = input("Enter raise amount (max $0.50): ")
                    try:
                        raise_amount = float(raise_amount_str)
                        if raise_amount > 0.50:
                            print("Raise amount too high, setting to max $0.50.")
                            raise_amount = 0.50
                        
                        bet_needed = current_bet - player_bets[player_name]
                        total_bet_this_turn = bet_needed + raise_amount
                        self.pot += total_bet_this_turn
                        player_bets[player_name] += total_bet_this_turn
                        current_bet += raise_amount 
                        print(f"{player_name} raises by {raise_amount:.2f}, total bet {current_bet:.2f}. Pot is now {self.pot:.2f}.")
                        round_complete = False
                    except ValueError:
                        print("Invalid raise amount. Please enter a number.")
                        active_players.remove(player_name)
                        players_folded.append(player_name)
                        print(f"{player_name} folds due to invalid input.")
                elif action == 'fold':
                    active_players.remove(player_name)
                    players_folded.append(player_name)
                    print(f"{player_name} folds.")
                else:
                    print("Invalid action. Please choose 'call', 'raise', or 'fold'.")
                    active_players.remove(player_name)
                    players_folded.append(player_name)
                    print(f"{player_name} folds due to invalid input.")
            
            if round_complete and any(player_bets[p] != current_bet for p in active_players if p not in players_folded):
                round_complete = False

            if len([p for p in active_players if p not in players_folded]) <= 1:
                break
        
        return [p for p in active_players if p not in players_folded]

    def discard_and_draw(self, active_players):
        for player_name in active_players:
            print(f"\n{player_name}'s turn to discard. Your hand: {self.players[player_name]}")
            while True:
                discard_indices_str = input("Enter indices of cards to discard (e.g., '0 2 4' for 1st, 3rd, 5th card, max 3 cards). Enter nothing to keep all cards: ")
                if not discard_indices_str:
                    discard_indices = []
                else:
                    try:
                        discard_indices = sorted([int(x) for x in discard_indices_str.split()])
                        if not all(0 <= i < len(self.players[player_name]) for i in discard_indices):
                            print("Invalid card index. Please enter indices within your hand's range.")
                            continue
                        if len(discard_indices) > 3:
                            print("You can discard a maximum of 3 cards.")
                            continue
                    except ValueError:
                        print("Invalid input. Please enter numbers separated by spaces.")
                        continue
                break

            new_hand = [card for i, card in enumerate(self.players[player_name]) if i not in discard_indices]
            num_to_draw = len(discard_indices)
            
            for _ in range(num_to_draw):
                if self.deck:
                    new_hand.append(self.deck.pop(0))
                else:
                    print("Deck is empty!")
                    break
            self.players[player_name] = new_hand
            print(f"{player_name}'s new hand: {self.players[player_name]}")


    def _rank_hand(self, hand):
        ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        card_ranks = sorted([ranks[card[0]] for card in hand])
        card_suits = [card[1] for card in hand]

        is_flush = len(set(card_suits)) == 1
        is_straight = True
        if 14 in card_ranks: 
            low_ace_straight = sorted([1 if r == 14 else r for r in card_ranks])
            if low_ace_straight == [2,3,4,5,14] or low_ace_straight == [1,2,3,4,5]:
                pass 
            elif not all(card_ranks[i] == card_ranks[i-1] + 1 for i in range(1, 5)):
                is_straight = False
        else:
            if not all(card_ranks[i] == card_ranks[i-1] + 1 for i in range(1, 5)):
                is_straight = False


        rank_counts = {}
        for r in card_ranks:
            rank_counts[r] = rank_counts.get(r, 0) + 1

        counts_list = sorted(rank_counts.values(), reverse=True)
        unique_ranks = sorted(rank_counts.keys(), reverse=True)

        if 5 in counts_list:
            return (9, unique_ranks[0]) 
        if is_straight and is_flush:
            if card_ranks == [10, 11, 12, 13, 14]:
                return (8, 14)  # Royal Flush
            return (8, card_ranks[-1])
        if 4 in counts_list:
            return (7, unique_ranks[0], unique_ranks[1])
        if counts_list == [3, 2]:
            return (6, unique_ranks[0], unique_ranks[1])
        if is_flush:
            return (5, *unique_ranks)
        if is_straight:
            return (4, card_ranks[-1])
        if 3 in counts_list:
            return (3, unique_ranks[0], *unique_ranks[1:])
        if counts_list == [2, 2, 1]:
            return (2, unique_ranks[0], unique_ranks[1], unique_ranks[2])
        if 2 in counts_list:
            return (1, unique_ranks[0], *unique_ranks[1:])
        return (0, *unique_ranks)

    def determine_winner(self, active_players):
        hand_strengths = {}
        for player_name in active_players:
            hand_strengths[player_name] = self._rank_hand(self.players[player_name])
            print(f"{player_name}'s hand: {self.players[player_name]} - Strength: {hand_strengths[player_name]}")

        if not hand_strengths:
            print("No active players to determine a winner.")
            return

        winner = max(hand_strengths, key=hand_strengths.get)
        print(f"\n{winner} wins the pot of {self.pot:.2f} with {self.players[winner]} (strength: {hand_strengths[winner]})!")
        self.pot = 0

    def play_hand(self):
        self.deck = self._create_deck()
        self.shuffle_deck()
        self.pot = 0
        for player_name in self.players:
            self.players[player_name] = []

        self.ante()
        self.deal_cards()

        active_players_after_first_betting = self.betting_round()
        if len(active_players_after_first_betting) <= 1:
            if active_players_after_first_betting:
                print(f"{active_players_after_first_betting[0]} wins the pot as all other players folded.")
                self.pot = 0
            return

        self.discard_and_draw(active_players_after_first_betting)
        
        final_active_players = self.betting_round()
        if len(final_active_players) <= 1:
            if final_active_players:
                print(f"{final_active_players[0]} wins the pot as all other players folded.")
                self.pot = 0
            return

        self.determine_winner(final_active_players)
        
        self.dealer_index = (self.dealer_index + 1) % len(self.players)

def main():
    player_names_input = input("Enter player names separated by commas (e.g., Alex, Brad, Charley, Dennis, You): ")
    player_names = [name.strip() for name in player_names_input.split(',')]
    
    game = PokerGame(player_names)

    while True:
        game.play_hand()
        play_again = input("\nPlay another hand? (yes/no): ").lower()
        if play_again != 'yes':
            break

if __name__ == "__main__":
    main()
