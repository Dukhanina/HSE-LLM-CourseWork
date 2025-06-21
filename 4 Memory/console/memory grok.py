import random

def create_board(size):
    cards = list(range(1, size*size//2 + 1)) * 2
    random.shuffle(cards)
    board = [cards[i:i+size] for i in range(0, len(cards), size)]
    revealed = [[False]*size for _ in range(size)]
    return board, revealed

def print_board(board, revealed):
    for i in range(len(board)):
        for j in range(len(board[i])):
            if revealed[i][j]:
                print(f"{board[i][j]:2}", end=" ")
            else:
                print(" X", end=" ")
        print()

def get_move(board_size):
    while True:
        try:
            move = input("Enter row and column (e.g., 1 2): ").split()
            if len(move) != 2:
                raise ValueError
            row, col = int(move[0])-1, int(move[1])-1
            if row < 0 or col < 0 or row >= board_size or col >= board_size:
                raise ValueError
            return row, col
        except ValueError:
            print(f"Invalid input. Enter two numbers between 1 and {board_size}.")

def main():
    size = 4
    board, revealed = create_board(size)
    pairs = size*size//2
    player1_score = 0
    player2_score = 0
    current_player = 1
    while player1_score + player2_score < pairs:
        print_board(board, revealed)
        print(f"Player {current_player}'s turn")
        row1, col1 = get_move(size)
        if revealed[row1][col1]:
            print("Card already revealed. Choose another.")
            continue
        revealed[row1][col1] = True
        print_board(board, revealed)
        row2, col2 = get_move(size)
        if (row1, col1) == (row2, col2):
            print("Cannot choose the same card twice.")
            revealed[row1][col1] = False
            continue
        if revealed[row2][col2]:
            print("Card already revealed. Choose another.")
            revealed[row1][col1] = False
            continue
        revealed[row2][col2] = True
        print_board(board, revealed)
        if board[row1][col1] == board[row2][col2]:
            print("Match found!")
            if current_player == 1:
                player1_score += 1
            else:
                player2_score += 1
        else:
            print("No match. Next player's turn.")
            revealed[row1][col1] = False
            revealed[row2][col2] = False
            current_player = 2 if current_player == 1 else 1
    print(f"Game over! Player 1: {player1_score}, Player 2: {player2_score}")
    if player1_score > player2_score:
        print("Player 1 wins!")
    elif player2_score > player1_score:
        print("Player 2 wins!")
    else:
        print("It's a tie!")

if __name__ == "__main__":
    main()
