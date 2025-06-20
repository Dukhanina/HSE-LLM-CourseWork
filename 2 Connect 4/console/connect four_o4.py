ROWS=6
COLS=7
def make_move(board,col,player):
    for r in range(ROWS-1,-1,-1):
        if board[r][col]==' ':
            board[r][col]=player
            return True
    return False
def check_win(board,player):
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c]!=player: continue
            if c<=COLS-4 and all(board[r][c+i]==player for i in range(4)): return True
            if r<=ROWS-4 and all(board[r+i][c]==player for i in range(4)): return True
            if r<=ROWS-4 and c<=COLS-4 and all(board[r+i][c+i]==player for i in range(4)): return True
            if r>=3 and c<=COLS-4 and all(board[r-i][c+i]==player for i in range(4)): return True
    return False
def print_board(board):
    print(' '.join(str(i+1) for i in range(COLS)))
    for row in board:
        print('|'+'|'.join(row)+'|')
def get_move(board,player):
    while True:
        try:
            col=int(input(f"Player {player}, choose column (1-7): "))-1
            if 0<=col<COLS and board[0][col]==' ':
                return col
        except:
            pass
        print("Invalid move. Try again.")
def main():
    board=[[' ' for _ in range(COLS)] for _ in range(ROWS)]
    player='X'
    while True:
        print_board(board)
        col=get_move(board,player)
        make_move(board,col,player)
        if check_win(board,player):
            print_board(board)
            print(f"Player {player} wins!")
            break
        if all(cell!=' ' for row in board for cell in row):
            print_board(board)
            print("Draw!")
            break
        player='O' if player=='X' else 'X'
if __name__=='__main__':
    main()
