import random

COLORS=['R','G','B','Y']
VALUES=[str(i) for i in range(1,10)]+['+2','Skip','Reverse']
def create_deck():
    deck=[]
    for c in COLORS:
        deck.append(c+'0')
        for v in VALUES:
            deck.append(c+v)
            deck.append(c+v)
    for _ in range(4):
        deck.append('W')
        deck.append('W4')
    return deck

def shuffle_deck(deck):
    random.shuffle(deck)

def deal(deck,players,hand_size=7):
    hands=[[] for _ in range(players)]
    for _ in range(hand_size):
        for h in hands:
            h.append(deck.pop())
    return hands

def draw_card(deck,discard):
    if not deck:
        deck.extend(discard[:-1])
        random.shuffle(deck)
        discard[:] = [discard[-1]]
    return deck.pop()

def can_play(card,top_color,top_value,hand):
    if card in ('W','W4'):
        if card=='W4':
            return all(c[0]!=top_color for c in hand if c not in ('W','W4'))
        return True
    if card[0]==top_color or card[1:]==top_value:
        return True
    return False

def apply_card(card,idx,players,hands,deck,discard,top_color,top_value,skip):
    discard.append(card)
    draw=0
    if card in ('W','W4'):
        while True:
            clr=input("Choose color (R/G/B/Y): ").strip().upper()
            if clr in COLORS:
                top_color=clr
                break
            print("Invalid color")
        top_value=card
    else:
        top_color=card[0]
        top_value=card[1:]
        if top_value in ('Skip','Reverse'):
            skip=True
        if top_value=='+2':
            draw=2
    if card=='W4':
        draw=4
    if draw>0:
        for _ in range(draw):
            hands[(idx+1)%players].append(draw_card(deck,discard))
        skip=True
    return top_color,top_value,skip

def check_win(hands):
    for i,h in enumerate(hands):
        if not h:
            return i
    return None

def main():
    players=2
    deck=create_deck()
    shuffle_deck(deck)
    hands=deal(deck,players)
    discard=[deck.pop()]
    while discard[-1] in ('W','W4'):
        deck.insert(0,discard.pop())
        discard.append(deck.pop())
    top_color=discard[-1][0]
    top_value=discard[-1][1:]
    turn=0
    skip=False
    while True:
        idx=turn%players
        hand=hands[idx]
        print("Top:",discard[-1])
        print("Hand:")
        for i,card in enumerate(hand,1):
            print(f"{i}: {card}")
        if skip:
            print("Turn skipped")
            skip=False
        else:
            move=input("Play card number or draw (d): ").strip()
            if move.lower()=='d':
                card=draw_card(deck,discard)
                hand.append(card)
                print("Drew:",card)
            else:
                if not move.isdigit():
                    print("Invalid input")
                    continue
                num=int(move)
                if num<1 or num>len(hand):
                    print("Invalid input")
                    continue
                i=num-1
                card=hand[i]
                if not can_play(card,top_color,top_value,hand):
                    print("Invalid play")
                    continue
                hand.pop(i)
                top_color,top_value,skip=apply_card(card,idx,players,hands,deck,discard,top_color,top_value,skip)
        winner=check_win(hands)
        if winner is not None:
            print("Player",winner+1,"wins")
            break
        turn+=1

if __name__=='__main__':
    main()
