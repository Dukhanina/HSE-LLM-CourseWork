import random

class UnoCard:
    def __init__(self, color, value):
        self.color = color
        self.value = value

    def __str__(self):
        if self.color == "Wild":
            return f"{self.color} {self.value}"
        return f"{self.color} {self.value}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.color == other.color and self.value == other.value

    def is_wild(self):
        return self.color == "Wild"

class UnoGame:
    def __init__(self, num_players):
        self.colors = ["Red", "Green", "Blue", "Yellow"]
        self.values = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "Skip", "Reverse", "Draw Two"]
        self.wild_cards = ["Wild", "Wild Draw Four"]
        self.deck = self._create_deck()
        self.players = [[] for _ in range(num_players)]
        self.discard_pile = []
        self.current_player_index = 0
        self.direction = 1 # 1 for clockwise (left), -1 for counter-clockwise (right)
        self.game_over = False
        self.current_color = None
        self.current_value = None

    def _create_deck(self):
        deck = []
        for color in self.colors:
            deck.append(UnoCard(color, "0")) # One 0 card per color 
            for value in self.values[1:]: # Two of each 1-9, Skip, Reverse, Draw Two per color 
                deck.append(UnoCard(color, value))
                deck.append(UnoCard(color, value))
        for _ in range(4): # Four Wild cards 
            deck.append(UnoCard("Wild", "Wild"))
            deck.append(UnoCard("Wild", "Wild Draw Four")) # Four Wild Draw 4 cards 
        random.shuffle(deck)
        return deck

    def _deal_cards(self):
        for i in range(len(self.players)):
            for _ in range(7): # Each player dealt seven cards 
                self.players[i].append(self._draw_card())

    def _draw_card(self):
        if not self.deck:
            if not self.discard_pile:
                print("No cards left to draw! Game might be stuck.")
                return None
            last_card = self.discard_pile.pop() # Keep the top card on discard 
            self.deck = self.discard_pile
            random.shuffle(self.deck)
            self.discard_pile = [last_card]
        return self.deck.pop(0)

    def _setup_discard_pile(self):
        while True:
            first_card = self._draw_card()
            if first_card.value == "Wild" or first_card.value == "Wild Draw Four": # If top card is Wild or Wild Draw 4, return it and pick another 
                self.deck.append(first_card)
                random.shuffle(self.deck)
            elif first_card.value == "Draw Two": # If Draw 2 is turned up, first player must draw 2 cards 
                self.discard_pile.append(first_card)
                self.current_color = first_card.color
                self.current_value = first_card.value
                print(f"Starting card: {first_card}. Player 1 must draw 2 cards and forfeit turn.")
                self.draw_cards_and_skip_turn(self.players[self.current_player_index], 2)
                self._next_player_turn() # Skip the first player's turn
                break
            elif first_card.value == "Reverse": # If Reverse is turned up, play goes to the right, player to the right plays first 
                self.discard_pile.append(first_card)
                self.current_color = first_card.color
                self.current_value = first_card.value
                self.direction *= -1
                print(f"Starting card: {first_card}. Play direction reversed. Player {self.current_player_index + 1} plays first.")
                break
            elif first_card.value == "Skip": # If Skip is turned up, first player is skipped 
                self.discard_pile.append(first_card)
                self.current_color = first_card.color
                self.current_value = first_card.value
                print(f"Starting card: {first_card}. Player 1 is skipped.")
                self._next_player_turn() # Skip the first player's turn
                break
            else:
                self.discard_pile.append(first_card)
                self.current_color = first_card.color
                self.current_value = first_card.value
                print(f"Starting card: {first_card}")
                break

    def start_game(self):
        self._deal_cards()
        self._setup_discard_pile()
        print("\n--- Game Started ---")
        self.run_game_loop()

    def _next_player_turn(self):
        self.current_player_index = (self.current_player_index + self.direction) % len(self.players)

    def is_valid_play(self, card_to_play):
        top_card = self.discard_pile[-1]

        if card_to_play.is_wild():
            return True # Wild cards can always be played 

        # Match by color or number/word 
        if card_to_play.color == self.current_color or card_to_play.value == self.current_value:
            return True

        return False

    def play_card(self, player_index, card_index, chosen_color=None):
        player_hand = self.players[player_index]
        card_to_play = player_hand[card_index]

        if not self.is_valid_play(card_to_play):
            print("Invalid card to play. Try again.")
            return False

        if card_to_play.value == "Wild Draw Four": # Check Wild Draw Four rules 
            has_matching_color = False
            for card in player_hand:
                if card.color == self.current_color and not card.is_wild():
                    has_matching_color = True
                    break
            if has_matching_color:
                print("You have a card matching the current color. You can only play Wild Draw Four if you don't have a card in hand that matches the color of the card previously played.")
                # Implement challenge option here, but for simplicity, we'll prevent it if a matching color is found.
                return False # Prevent playing illegally by default for AI, or prompt user.

        player_hand.pop(card_index)
        self.discard_pile.append(card_to_play)

        print(f"Player {player_index + 1} played: {card_to_play}")

        # Update current color/value based on played card
        if card_to_play.is_wild():
            self.current_color = chosen_color # Player chooses new color 
            self.current_value = "Wild" if card_to_play.value == "Wild" else "Wild Draw Four"
            print(f"Color changed to {self.current_color}.")
        else:
            self.current_color = card_to_play.color
            self.current_value = card_to_play.value

        # Apply special card effects
        if card_to_play.value == "Skip": # Skip the next person's turn 
            self._next_player_turn()
            print(f"Player {self.current_player_index + 1} is skipped.")
        elif card_to_play.value == "Reverse": # Reverse the direction of play 
            self.direction *= -1
            print(f"Play direction reversed.")
        elif card_to_play.value == "Draw Two": # Next player must draw 2 cards and forfeit turn 
            self.draw_cards_and_skip_turn(self.players[self.current_player_index + self.direction], 2)
            self._next_player_turn()
            print(f"Player {self.current_player_index + 1} draws 2 cards and is skipped.")
        elif card_to_play.value == "Wild Draw Four": # Next player must draw 4 cards and forfeit turn 
            self.draw_cards_and_skip_turn(self.players[self.current_player_index + self.direction], 4)
            self._next_player_turn()
            print(f"Player {self.current_player_index + 1} draws 4 cards and is skipped.")

        return True

    def draw_cards_and_skip_turn(self, player_hand, num_cards):
        for _ in range(num_cards):
            drawn_card = self._draw_card()
            if drawn_card:
                player_hand.append(drawn_card)

    def check_for_winner(self):
        if not self.players[self.current_player_index]: # Player plays their last card, hand is over 
            self.game_over = True
            print(f"\n--- Player {self.current_player_index + 1} wins the round! ---")
            return True
        return False

    def say_uno(self, player_index):
        # In a CLI, this is simplified. A real game would have a 'catch' mechanic.
        print(f"Player {player_index + 1} says 'UNO!'")

    def run_game_loop(self):
        while not self.game_over:
            current_player_hand = self.players[self.current_player_index]
            
            print(f"\n--- Player {self.current_player_index + 1}'s Turn ---")
            print(f"Top card on discard: {self.discard_pile[-1]} (Current color: {self.current_color})")
            print(f"Your hand: {current_player_hand}")

            playable_cards_indices = []
            for i, card in enumerate(current_player_hand):
                if self.is_valid_play(card):
                    playable_cards_indices.append(i)
            
            if not playable_cards_indices:
                print("No playable cards. Drawing a card...")
                drawn_card = self._draw_card()
                if not drawn_card:
                    print("Cannot draw, deck is empty and discard pile is almost empty. Game ends in a draw.")
                    self.game_over = True
                    continue
                current_player_hand.append(drawn_card)
                print(f"You drew: {drawn_card}")
                if self.is_valid_play(drawn_card):
                    print("You can play the drawn card.")
                    # Player can choose to play the drawn card immediately 
                    choice = input("Do you want to play the drawn card? (yes/no): ").lower()
                    if choice == 'yes':
                        played = self.play_card(self.current_player_index, len(current_player_hand) - 1, self._get_color_choice(drawn_card))
                        if not played: # If play failed (e.g. illegal Wild Draw Four)
                            print("Could not play the drawn card.")
                            self._next_player_turn()
                            continue
                    else:
                        self._next_player_turn()
                        continue
                else:
                    print("Drawn card is not playable. Turn passes.")
                    self._next_player_turn()
                    continue
            else:
                while True:
                    try:
                        print("Playable cards in hand (indices):", playable_cards_indices)
                        card_choice = input(f"Enter the index of the card to play (0-{len(current_player_hand) - 1}), or 'draw' to draw a card: ").lower()
                        
                        if card_choice == 'draw':
                            print("Drawing a card...")
                            drawn_card = self._draw_card()
                            if not drawn_card:
                                print("Cannot draw, deck is empty and discard pile is almost empty. Game ends in a draw.")
                                self.game_over = True
                                break
                            current_player_hand.append(drawn_card)
                            print(f"You drew: {drawn_card}")
                            if self.is_valid_play(drawn_card):
                                print("You can play the drawn card.")
                                choice = input("Do you want to play the drawn card? (yes/no): ").lower()
                                if choice == 'yes':
                                    played = self.play_card(self.current_player_index, len(current_player_hand) - 1, self._get_color_choice(drawn_card))
                                    if played:
                                        break
                                else:
                                    self._next_player_turn()
                                    break
                            else:
                                print("Drawn card is not playable. Turn passes.")
                                self._next_player_turn()
                                break

                        card_index = int(card_choice)
                        if 0 <= card_index < len(current_player_hand) and card_index in playable_cards_indices:
                            card_to_play = current_player_hand[card_index]
                            chosen_color = None
                            if card_to_play.is_wild():
                                chosen_color = self._get_color_choice(card_to_play)

                            played = self.play_card(self.current_player_index, card_index, chosen_color)
                            if played:
                                if len(current_player_hand) == 1: # After playing, check if 1 card left
                                    self.say_uno(self.current_player_index) # Player says UNO 
                                break
                        else:
                            print("Invalid card index or card is not playable. Please select a valid index from your hand that is also a playable card.")
                    except ValueError:
                        print("Invalid input. Please enter a number or 'draw'.")
            
            if self.check_for_winner():
                break
            
            if not self.game_over:
                self._next_player_turn()

    def _get_color_choice(self, card):
        if card.is_wild():
            while True:
                color_choice = input("Choose a color (Red, Green, Blue, Yellow): ").capitalize()
                if color_choice in self.colors:
                    return color_choice
                else:
                    print("Invalid color. Please choose from Red, Green, Blue, Yellow.")
        return None

def main():
    while True:
        try:
            num_players = int(input("Enter number of players (2-10): ")) # 2-10 players 
            if 2 <= num_players <= 10:
                break
            else:
                print("Number of players must be between 2 and 10.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    game = UnoGame(num_players)
    game.start_game()

if __name__ == "__main__":
    main()
