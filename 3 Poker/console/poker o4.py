import random

VALUES = '23456789TJQKA'
SUITS = 'SHDC'

def create_deck():
    return [v+s for v in VALUES for s in SUITS]

def deal(deck):
    return [deck.pop() for _ in range(5)]

def hand_rank(hand):
    counts = {}
    vals = []
    for card in hand:
        v = VALUES.index(card[0]) + 2
        counts[v] = counts.get(v,0) + 1
        vals.append(v)
    flush = len({card[1] for card in hand}) == 1
    unique_vals = sorted(set(vals))
    straight = False
    if len(unique_vals) == 5:
        if max(unique_vals) - min(unique_vals) == 4:
            straight = True
            high = max(unique_vals)
        elif set(unique_vals) == {14,2,3,4,5}:
            straight = True
            high = 5
    counts_items = sorted(counts.items(), key=lambda x: (-x[1], -x[0]))
    if straight and flush:
        return (9, [high])
    if counts_items[0][1] == 4:
        four = counts_items[0][0]
        kicker = [v for v in vals if v != four][0]
        return (8, [four, kicker])
    if counts_items[0][1] == 3 and counts_items[1][1] == 2:
        return (7, [counts_items[0][0], counts_items[1][0]])
    if flush:
        return (6, sorted(vals, reverse=True))
    if straight:
        return (5, [high])
    if counts_items[0][1] == 3:
        three = counts_items[0][0]
        kickers = sorted([v for v in vals if v != three], reverse=True)
        return (4, [three] + kickers)
    if counts_items[0][1] == 2 and counts_items[1][1] == 2:
        p1, p2 = counts_items[0][0], counts_items[1][0]
        kicker = [v for v in vals if v not in (p1,p2)][0]
        highp, lowp = max(p1,p2), min(p1,p2)
        return (3, [highp, lowp, kicker])
    if counts_items[0][1] == 2:
        pair = counts_items[0][0]
        kickers = sorted([v for v in vals if v != pair], reverse=True)
        return (2, [pair] + kickers)
    return (1, sorted(vals, reverse=True))

def main():
    deck = create_deck()
    random.shuffle(deck)
    p1 = deal(deck)
    p2 = deal(deck)
    for label, hand in [("Player 1", p1), ("Player 2", p2)]:
        print(label, "hand:", " ".join(hand))
        disc = input("Discard positions (1-5): ").split()
        idxs = sorted({int(x)-1 for x in disc if x.isdigit() and 1<=int(x)<=5}, reverse=True)
        for i in idxs:
            if 0 <= i < len(hand):
                hand.pop(i)
        while len(hand) < 5:
            hand.append(deck.pop())
        print(label, "new hand:", " ".join(hand))
    r1 = hand_rank(p1)
    r2 = hand_rank(p2)
    if r1 > r2:
        result = "Player 1 wins"
    elif r2 > r1:
        result = "Player 2 wins"
    else:
        result = "Tie"
    print("Player 1:", " ".join(p1), "Rank:", r1)
    print("Player 2:", " ".join(p2), "Rank:", r2)
    print(result)

if __name__ == "__main__":
    main()
