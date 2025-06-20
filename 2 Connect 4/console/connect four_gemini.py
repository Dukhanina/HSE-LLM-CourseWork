import sys

ROWS = 6
COLS = 7

PLAYER_ONE_PIECE = 'R'
PLAYER_TWO_PIECE = 'Y'
EMPTY_SLOT = ' '

def create_board():
    return [[EMPTY_SLOT for _ in range(COLS)] for _ in range(ROWS)]

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return 0 <= col < COLS and board[ROWS - 1][col] == EMPTY_SLOT

def get_next_open_row(board, col):
    for r in range(ROWS):
        if board[r][col] == EMPTY_SLOT:
            return r
    return None

def print_board(board):
    print("\n  0   1   2   3   4   5   6")
    print("-----------------------------")
    for r in range(ROWS - 1, -1, -1):
        row_str = " | ".join(board[r])
        print(f"| {row_str} |")
    print("=============================")

def winning_move(board, piece):
    for c in range(COLS - 3):
        for r in range(ROWS):
            if all(board[r][c + i] == piece for i in range(4)):
                return True

    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True

    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True

    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True
    
    return False

def is_board_full(board):
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == EMPTY_SLOT:
                return False
    return True

def main():
    board = create_board()
    game_over = False
    turn = 0

    while not game_over:
        print_board(board)
        player = (turn % 2) + 1
        piece = PLAYER_ONE_PIECE if player == 1 else PLAYER_TWO_PIECE

        try:
            selection = input(f"Player {player} ({piece}), make your selection (0-{COLS-1}): ")
            if not selection.isdigit():
                print("Invalid input. Please enter a number.", file=sys.stderr)
                continue
            col = int(selection)
        except (ValueError, IndexError):
            print(f"Invalid column. Please choose a number between 0 and {COLS-1}.", file=sys.stderr)
            continue

        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, piece)

            if winning_move(board, piece):
                print_board(board)
                print(f"\n*** Player {player} ({piece}) wins! ***\n")
                game_over = True
            elif is_board_full(board):
                print_board(board)
                print("\n*** The game is a draw! ***\n")
                game_over = True
            else:
                turn += 1
        else:
            print(f"Column {col} is full. Please choose another column.", file=sys.stderr)

if __name__ == "__main__":
    main()
