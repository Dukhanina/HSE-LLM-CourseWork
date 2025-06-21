import random

LADDERS={1:38,4:14,9:31,21:42,28:84,36:44,51:67,71:91,80:100}
SNAKES={16:6,47:26,49:11,56:53,62:19,64:60,87:24,93:73,95:75,98:78}

def roll_dice():
    return random.randint(1,6)

def move(position,roll):
    pos=position+roll
    if pos>100:
        pos=100-(pos-100)
    if pos in LADDERS:
        pos=LADDERS[pos]
    elif pos in SNAKES:
        pos=SNAKES[pos]
    return pos

def check_win(position):
    return position==100

def main():
    players=['Player 1','Player 2']
    positions=[0,0]
    current=0
    while True:
        input(f"{players[current]}, press Enter to roll the dice")
        r=roll_dice()
        print(f"{players[current]} rolled a {r}")
        positions[current]=move(positions[current],r)
        print(f"{players[current]} is now on square {positions[current]}")
        if check_win(positions[current]):
            print(f"{players[current]} wins!")
            break
        if r!=6:
            current=(current+1)%len(players)

if __name__=="__main__":
    main()
