import random

def create_deck():
    return [(i,j) for i in range(7) for j in range(i,7)]

def draw_hands(deck,players):
    hand_size = 7 if players==2 else 5
    return [ [deck.pop() for _ in range(hand_size)] for _ in range(players) ]

def get_playable(hand,left,right):
    if left is None:
        return list(range(len(hand)))
    playable=[]
    for i,(a,b) in enumerate(hand):
        if a==left or b==left or a==right or b==right:
            playable.append(i)
    return playable

def play_tile(hand,layout,index,left,right):
    a,b = hand.pop(index)
    if left is None:
        layout.append((a,b))
        return a,b
    if a==left:
        layout.insert(0,(b,a))
        return b,right
    if b==left:
        layout.insert(0,(a,b))
        return a,right
    if a==right:
        layout.append((a,b))
        return left,b
    if b==right:
        layout.append((b,a))
        return left,a
    return left,right

def sum_pips(hand):
    return sum(a+b for a,b in hand)

def main():
    players=2
    deck=create_deck()
    random.shuffle(deck)
    hands=draw_hands(deck,players)
    layout=[]
    left=right=None
    passes=0
    turn=0
    while True:
        idx = turn % players
        hand = hands[idx]
        print(f"Player {idx+1} hand:",["{}-{}".format(a,b) for a,b in hand])
        if left is None:
            playable = list(range(len(hand)))
        else:
            playable = get_playable(hand,left,right)
        if playable:
            print("Layout ends:",left, right)
            print("Playable:",[i+1 for i in playable])
            choice = input(f"Player {idx+1}, choose tile number: ")
            if not choice.isdigit():
                print("Invalid input"); continue
            i = int(choice)-1
            if i not in playable:
                print("Invalid play"); continue
            left,right = play_tile(hand,layout,i,left,right)
            passes=0
            if not hand:
                print(f"Player {idx+1} wins")
                break
        else:
            print(f"Player {idx+1} passes")
            passes += 1
            if passes >= players:
                scores = [sum_pips(h) for h in hands]
                winner = scores.index(min(scores))
                print("Blocked. Player",winner+1,"wins by lowest pips")
                break
        turn += 1
        print("Layout:",["{}-{}".format(a,b) for a,b in layout])

if __name__=="__main__":
    main()
