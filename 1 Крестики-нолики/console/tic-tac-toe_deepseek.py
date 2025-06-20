def print_board(board):
    for row in board:
        print(" | ".join(row))
        print("-" * 9)

def check_win(board, player):
    win_conditions = [
        [board[0][0], board[0][1], board[0][2]],
        [board[1][0], board[1][1], board[1][2]],
        [board[2][0], board[2][1], board[2][2]],
        [board[0][0], board[1][0], board[2][0]],
        [board[0][1], board[1][1], board[2][1]],
        [board[0][2], board[1][2], board[2][2]],
        [board[0][0], board[1][1], board[2][2]],
        [board[0][2], board[1][1], board[2][0]]
    ]
    return [player, player, player] in win_conditions

def is_draw(board):
    for row in board:
        if " " in row:
            return False
    return True

def main():
    board = [[" " for _ in range(3)] for _ in range(3)]
    players = ["X", "O"]
    current_player = 0
    print("TIC TAC TOE")
    print_board(board)
    
    while True:
        player_symbol = players[current_player]
        print(f"Player {player_symbol}'s turn")
        
        try:
            row = int(input("Enter row (1-3): ")) - 1
            col = int(input("Enter column (1-3): ")) - 1
            if not (0 <= row <= 2 and 0 <= col <= 2):
                print("Invalid input. Numbers must be 1-3.")
                continue
            if board[row][col] != " ":
                print("Cell already taken!")
                continue
        except ValueError:
            print("Invalid input. Please enter numbers.")
            continue
        
        board[row][col] = player_symbol
        print_board(board)
        
        if check_win(board, player_symbol):
            print(f"Player {player_symbol} wins!")
            break
        if is_draw(board):
            print("It's a draw!")
            break
        
        current_player = 1 - current_player

if __name__ == "__main__":
    main()
