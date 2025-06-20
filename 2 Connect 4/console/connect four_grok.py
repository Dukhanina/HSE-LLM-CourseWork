def check_win(board, player):
    for r in range(6):
        for c in range(4):
            if all(board[r][c+i] == player for i in range(4)):
                return True
    for c in range(7):
        for r in range(3):
            if all(board[r+i][c] == player for i in range(4)):
                return True
    for r in range(3):
        for c in range(4):
            if all(board[r+i][c+i] == player for i in range(4)):
                return True
    for r in range(3):
        for c in range(3,7):
            if all(board[r+i][c-i] == player for i in range(4)):
                return True
    return False

def print_board(board):
    print("1 2 3 4 5 6 7")
    for r in range(5,-1,-1):
        row = [board[r][c] if board[r][c] != ' ' else '.' for c in range(7)]
        print(' '.join(row))

def main():
    board = [[' ' for _ in range(7)] for _ in range(6)]
    current_player = 'R'
    while True:
        print_board(board)
        print(f"Player {current_player}, enter column (1-7): ", end='')
        try:
            col = int(input()) - 1
            if col < 0 or col > 6:
                print("Invalid column. Choose between 1 and 7.")
                continue
            placed = False
            for r in range(6):
                if board[r][col] == ' ':
                    board[r][col] = current_player
                    placed = True
                    break
            if not placed:
                print("Column is full. Choose another.")
                continue
            if check_win(board, current_player):
                print_board(board)
                print(f"Player {current_player} wins!")
                break
            if all(cell != ' ' for row in board for cell in row):
                print_board(board)
                print("It's a draw!")
                break
            current_player = 'Y' if current_player == 'R' else 'R'
        except ValueError:
            print("Invalid input. Enter a number.")

if __name__ == "__main__":
    main()
