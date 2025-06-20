def print_board(board):
    print("0 1 2 3 4 5 6")
    print("--------------")
    for row in board:
        print(" ".join(row))

def get_valid_move(board, player):
    while True:
        try:
            col = int(input(f"Player {player}, choose column (0-6): "))
            if col < 0 or col > 6:
                print("Invalid column. Choose 0-6.")
                continue
            if board[0][col] != '.':
                print("Column full. Choose another.")
                continue
            return col
        except ValueError:
            print("Enter a number.")

def drop_piece(board, col, player):
    for row in range(5, -1, -1):
        if board[row][col] == '.':
            board[row][col] = player
            return row, col

def check_win(board, row, col, player):
    directions = [
        [(0, 1), (0, -1)],  
        [(1, 0), (-1, 0)],  
        [(1, 1), (-1, -1)], 
        [(1, -1), (-1, 1)] 
    ]
    for direction_pair in directions:
        count = 1
        for dr, dc in direction_pair:
            r, c = row + dr, col + dc
            while 0 <= r < 6 and 0 <= c < 7 and board[r][c] == player:
                count += 1
                r += dr
                c += dc
                if count >= 4:
                    return True
    return False

def check_draw(board):
    return all(cell != '.' for cell in board[0])

def main():
    board = [['.' for _ in range(7)] for _ in range(6)]
    players = ['X', 'O']
    current = 0
    
    while True:
        print_board(board)
        player = players[current]
        col = get_valid_move(board, player)
        row, _ = drop_piece(board, col, player)
        
        if check_win(board, row, col, player):
            print_board(board)
            print(f"Player {player} wins!")
            break
            
        if check_draw(board):
            print_board(board)
            print("It's a draw!")
            break
            
        current = 1 - current

if __name__ == "__main__":
    main()
