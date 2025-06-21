import random

ROWS=4
COLS=4
PAIRS=ROWS*COLS//2

def init_board():
    cards=[chr(ord('A')+i) for i in range(PAIRS)]*2
    random.shuffle(cards)
    return cards

def print_board(board,revealed,temp):
    for i in range(ROWS):
        row=[]
        for j in range(COLS):
            idx=i*COLS+j
            if revealed[idx] or idx in temp:
                row.append(board[idx])
            else:
                row.append('*')
        print(' '.join(row))
    print()

def get_choice(board,revealed,temp):
    while True:
        try:
            n=int(input(f"Choose card (1-{ROWS*COLS}): "))-1
            if 0<=n<ROWS*COLS and not revealed[n] and n not in temp:
                return n
        except:
            pass
        print("Invalid choice")

def make_move(board,revealed,p1,p2,current,scores):
    if board[p1]==board[p2]:
        revealed[p1]=True
        revealed[p2]=True
        scores[current]+=1
        return True
    return False

def check_win(scores):
    return sum(scores.values())==PAIRS

def main():
    board=init_board()
    revealed=[False]*(ROWS*COLS)
    scores={1:0,2:0}
    current=1
    while True:
        print_board(board,revealed,[])
        print(f"Player {current}'s turn")
        p1=get_choice(board,revealed,[])
        print_board(board,revealed,[p1])
        p2=get_choice(board,revealed,[p1])
        print_board(board,revealed,[p1,p2])
        if make_move(board,revealed,p1,p2,current,scores):
            print("Match!")
            if check_win(scores):
                break
        else:
            print("No match")
            current=1 if current==2 else 2
        input("Press Enter to continue")
    print("Game over. Scores:",scores)
    if scores[1]>scores[2]:
        print("Player 1 wins")
    elif scores[2]>scores[1]:
        print("Player 2 wins")
    else:
        print("Draw")

if __name__=="__main__":
    main()
