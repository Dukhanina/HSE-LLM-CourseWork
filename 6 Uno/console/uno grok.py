from collections import deque
import random

class Card:
    def __init__(self, color, value):
        self.color = color
        self.value = value

    def __str__(self):
        return f"{self.color} {self.value}"

class UnoGame:
    def __init__(self, num_players):
        self.num_players = num_players
        self.players = [deque() for _ in range(num_players)]
        self.deck = deque()
        self.discard_pile = deque()
        self.current_player = 0
        self.direction = 1
        self.winner = None
        self.create_deck()
        self.deal_cards()

    def create_deck(self):
        colors = ['Red', 'Yellow', 'Green', 'Blue']
        values = [str(i) for i in range(10)] + ['Skip', 'Reverse', 'Draw Two']
        wilds = ['Wild', 'Wild Draw Four']
        for color in colors:
            for value in values:
                self.deck.append(Card(color, value))
                if value != '0':
                    self.deck.append(Card(color, value))
        for _ in range(4):
            for wild in wilds:
                self.deck.append(Card(None, wild))
        random.shuffle(self.deck)

    def deal_cards(self):
        for _ in range(7):
            for player in self.players:
                player.append(self.deck.pop())
        self.discard_pile.append(self.deck.pop())
        while self.discard_pile[-1].value == 'Wild Draw Four':
            self.deck.append(self.discard_pile.pop())
            random.shuffle(self.deck)
            self.discard_pile.append(self.deck.pop())

    def play(self):
        while self.winner is None:
            self.play_turn()
            self.current_player = (self.current_player + self.direction) % self.num_players
        print(f"Player {self.winner} wins!")

    def play_turn(self):
        player = self.players[self.current_player]
        print(f"Player {self.current_player}'s turn")
        print(f"Top card: {self.discard_pile[-1]}")
        print(f"Your hand: {[str(card) for card in player]}")
        can_play = False
        for card in player:
            if self.can_play_card(card):
                can_play = True
                break
        if can_play:
            while True:
                choice = input("Choose card index to play or 'draw': ")
                if choice == 'draw':
                    self.draw_card()
                    break
                try:
                    index = int(choice)
                    card = player[index]
                    if self.can_play_card(card):
                        self.play_card(card)
                        break
                    else:
                        print("Cannot play that card")
                except (ValueError, IndexError):
                    print("Invalid choice")
        else:
            print("No playable cards, drawing a card")
            self.draw_card()

    def can_play_card(self, card):
        top_card = self.discard_pile[-1]
        if card.color == top_card.color or card.value == top_card.value or card.color is None:
            return True
        if card.value == 'Wild Draw Four':
            for c in self.players[self.current_player]:
                if c.color == top_card.color:
                    return False
            return True
        return False

    def play_card(self, card):
        self.discard_pile.append(card)
        self.players[self.current_player].remove(card)
        if len(self.players[self.current_player]) == 0:
            self.winner = self.current_player
        elif len(self.players[self.current_player]) == 1:
            print("UNO!")
        if card.value == 'Reverse':
            self.direction *= -1
        elif card.value == 'Skip':
            self.current_player = (self.current_player + self.direction) % self.num_players
        elif card.value == 'Draw Two':
            next_player = (self.current_player + self.direction) % self.num_players
            for _ in range(2):
                self.players[next_player].append(self.deck.pop())
        elif card.value == 'Wild':
            color = input("Choose a color (Red/Yellow/Green/Blue): ")
            card.color = color
        elif card.value == 'Wild Draw Four':
            color = input("Choose a color (Red/Yellow/Green/Blue): ")
            card.color = color
            next_player = (self.current_player + self.direction) % self.num_players
            for _ in range(4):
                self.players[next_player].append(self.deck.pop())

    def draw_card(self):
        if len(self.deck) == 0:
            self.deck = self.discard_pile[:-1]
            self.discard_pile = deque([self.discard_pile[-1]])
            random.shuffle(self.deck)
        card = self.deck.pop()
        self.players[self.current_player].append(card)
        if self.can_play_card(card):
            print(f"Drew {card}, playing it")
            self.play_card(card)

def main():
    num_players = int(input("Enter number of players: "))
    game = UnoGame(num_players)
    game.play()

if __name__ == "__main__":
    main()
