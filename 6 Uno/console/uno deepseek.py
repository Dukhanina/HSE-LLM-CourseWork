import random

class Card:
    def __init__(self, color, value, card_type):
        self.color = color
        self.value = value
        self.type = card_type
    
    def __str__(self):
        if self.type == 'number':
            return f"{self.color} {self.value}"
        elif self.type == 'wild' or self.type == 'wild_draw4':
            return self.type.replace('_', ' ').title()
        else:
            return f"{self.color} {self.type}"

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.score = 0
        self.uno_not_said = False

def create_deck():
    colors = ['Red', 'Blue', 'Green', 'Yellow']
    deck = []
    
    for color in colors:
        for num in range(0, 10):
            count = 2 if num != 0 else 1
            deck.extend([Card(color, num, 'number') for _ in range(count)])
    
    for color in colors:
        deck.extend([Card(color, None, 'reverse') for _ in range(2)])
        deck.extend([Card(color, None, 'skip') for _ in range(2)])
        deck.extend([Card(color, None, 'draw2') for _ in range(2)])
    
    deck.extend([Card(None, None, 'wild') for _ in range(4)])
    deck.extend([Card(None, None, 'wild_draw4') for _ in range(4)])
    
    random.shuffle(deck)
    return deck

def valid_play(top_card, played_card):
    if played_card.type in ['wild', 'wild_draw4']:
        return True
    if played_card.color == top_card.color:
        return True
    if played_card.type == top_card.type and top_card.type != 'number':
        return True
    if played_card.type == 'number' and top_card.type == 'number' and played_card.value == top_card.value:
        return True
    return False

def main():
    players = [Player("Player 0"), Player("Player 1")]
    game_score = [0, 0]
    first_round = True

    while max(game_score) < 500:
        deck = create_deck()
        discard_pile = []
        players[0].hand = []
        players[1].hand = []
        players[0].uno_not_said = False
        players[1].uno_not_said = False
        
        for _ in range(7):
            players[0].hand.append(deck.pop())
            players[1].hand.append(deck.pop())
        
        while True:
            card = deck.pop()
            if card.type not in ['wild', 'wild_draw4']:
                discard_pile.append(card)
                current_color = card.color
                break
            else:
                deck.insert(0, card)
        
        current_player = 1
        skip_next = False
        
        while True:
            if skip_next:
                skip_next = False
            else:
                opponent = (current_player + 1) % 2
                if players[opponent].uno_not_said:
                    catch = input(f"{players[opponent].name} forgot UNO! Catch? (y/n): ").lower()
                    if catch == 'y':
                        for _ in range(4):
                            if deck:
                                players[opponent].hand.append(deck.pop())
                        players[opponent].uno_not_said = False
            
            top_card = discard_pile[-1]
            print(f"\nTop card: {top_card}")
            print(f"{players[current_player].name}'s turn")
            print("Your hand: " + ", ".join(str(card) for card in players[current_player].hand))
            
            playable_cards = [card for card in players[current_player].hand if valid_play(top_card, card)]
            action = input("Play card index (0-based) or 'draw': ")
            
            played_card = None
            if action.isdigit():
                index = int(action)
                if 0 <= index < len(players[current_player].hand):
                    card = players[current_player].hand[index]
                    if card in playable_cards:
                        played_card = players[current_player].hand.pop(index)
            
            if played_card:
                discard_pile.append(played_card)
                if played_card.type in ['wild', 'wild_draw4']:
                    chosen_color = input("Choose color (Red/Blue/Green/Yellow): ").capitalize()
                    while chosen_color not in ['Red', 'Blue', 'Green', 'Yellow']:
                        chosen_color = input("Invalid color. Choose color (Red/Blue/Green/Yellow): ").capitalize()
                    current_color = chosen_color
                else:
                    current_color = played_card.color
                
                if len(players[current_player].hand) == 1:
                    uno_said = input("Say UNO! Type 'uno': ").lower()
                    players[current_player].uno_not_said = uno_said != 'uno'
                
                if played_card.type == 'reverse' or played_card.type == 'skip':
                    skip_next = True
                
                if played_card.type == 'draw2':
                    for _ in range(2):
                        if deck:
                            players[opponent].hand.append(deck.pop())
                    skip_next = True
                
                if played_card.type == 'wild_draw4':
                    challenge = input(f"{players[opponent].name}, challenge? (y/n): ").lower() == 'y'
                    prev_color = top_card.color
                    has_color_card = any(card.color == prev_color for card in players[current_player].hand if card.color)
                    
                    if challenge and has_color_card:
                        for _ in range(4):
                            if deck:
                                players[current_player].hand.append(deck.pop())
                    elif challenge and not has_color_card:
                        for _ in range(6):
                            if deck:
                                players[opponent].hand.append(deck.pop())
                    else:
                        for _ in range(4):
                            if deck:
                                players[opponent].hand.append(deck.pop())
                    skip_next = True
                
                if len(players[current_player].hand) == 0:
                    break
            else:
                if action == 'draw':
                    if deck:
                        new_card = deck.pop()
                        players[current_player].hand.append(new_card)
                        if valid_play(top_card, new_card):
                            play_now = input(f"Play {new_card}? (y/n): ").lower()
                            if play_now == 'y':
                                players[current_player].hand.pop()
                                discard_pile.append(new_card)
                                if new_card.type in ['wild', 'wild_draw4']:
                                    chosen_color = input("Choose color (Red/Blue/Green/Yellow): ").capitalize()
                                    current_color = chosen_color
                                else:
                                    current_color = new_card.color
                                
                                if len(players[current_player].hand) == 1:
                                    uno_said = input("Say UNO! Type 'uno': ").lower()
                                    players[current_player].uno_not_said = uno_said != 'uno'
                                
                                if new_card.type == 'reverse' or new_card.type == 'skip':
                                    skip_next = True
                                if new_card.type == 'draw2':
                                    for _ in range(2):
                                        if deck:
                                            players[opponent].hand.append(deck.pop())
                                    skip_next = True
                                if new_card.type == 'wild_draw4':
                                    challenge = input(f"{players[opponent].name}, challenge? (y/n): ").lower() == 'y'
                                    prev_color = top_card.color
                                    has_color_card = any(card.color == prev_color for card in players[current_player].hand if card.color)
                                    
                                    if challenge and has_color_card:
                                        for _ in range(4):
                                            if deck:
                                                players[current_player].hand.append(deck.pop())
                                    elif challenge and not has_color_card:
                                        for _ in range(6):
                                            if deck:
                                                players[opponent].hand.append(deck.pop())
                                    else:
                                        for _ in range(4):
                                            if deck:
                                                players[opponent].hand.append(deck.pop())
                                    skip_next = True
                                
                                if len(players[current_player].hand) == 0:
                                    break
            
            if not skip_next:
                current_player = opponent
            
            if not deck:
                discard_top = discard_pile.pop()
                deck = discard_pile
                random.shuffle(deck)
                discard_pile = [discard_top]
        
        round_winner = current_player
        points = 0
        for player in players:
            for card in player.hand:
                if card.type == 'number':
                    points += card.value
                elif card.type in ['reverse', 'skip', 'draw2']:
                    points += 20
                elif card.type in ['wild', 'wild_draw4']:
                    points += 50
        game_score[round_winner] += points
        
        print(f"\n{players[round_winner].name} wins the round! +{points} points")
        print(f"Scores: {players[0].name}: {game_score[0]}, {players[1].name}: {game_score[1]}")
        
        if first_round:
            current_player = round_winner
            first_round = False
        else:
            current_player = (round_winner + 1) % 2
    
    winner_idx = 0 if game_score[0] >= 500 else 1
    print(f"\n{players[winner_idx].name} wins the game with {game_score[winner_idx]} points!")

if __name__ == "__main__":
    main()
