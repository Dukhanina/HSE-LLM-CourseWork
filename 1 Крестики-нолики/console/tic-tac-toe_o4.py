def make_move(board,pos,player):
    if board[pos]==' ':
        board[pos]=player
        return True
    return False

def check_win(board,player):
    lines=[(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    return any(board[a]==board[b]==board[c]==player for a,b,c in lines)

def print_board(board):
    for i in range(3):
        print('|'+'|'.join(board[i*3:(i+1)*3])+'|')

def get_move(board,player):
    while True:
        try:
            n=int(input(f"Player {player}, enter move (1-9): "))
            if 1<=n<=9 and board[n-1]==' ':
                return n-1
        except:
            pass

def main():
    board=[' ']*9
    player='X'
    moves=0
    while True:
        print_board(board)
        pos=get_move(board,player)
        make_move(board,pos,player)
        moves+=1
        if check_win(board,player):
            print_board(board)
            print(f"Player {player} wins")
            break
        if moves==9:
            print_board(board)
            print("Draw")
            break
        player='O' if player=='X' else 'X'

if __name__=='__main__':
    main()
