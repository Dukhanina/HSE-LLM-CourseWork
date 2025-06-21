import sys
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_board():
    return [
        {"problem": "38 - 26", "answer": 12, "mark": " "},
        {"problem": "76 - 58", "answer": 18, "mark": " "},
        {"problem": "35 - 16", "answer": 19, "mark": " "},
        {"problem": "67 - 31", "answer": 36, "mark": " "},
        {"problem": "50 - 42", "answer": 8, "mark": " "},
        {"problem": "28 - 15", "answer": 13, "mark": " "},
        {"problem": "86 - 26", "answer": 60, "mark": " "},
        {"problem": "44 - 15", "answer": 29, "mark": " "},
        {"problem": "92 - 46", "answer": 46, "mark": " "},
    ]

def display_board(board):
    clear_screen()
    print("Tic-Tac-Toe: Solve to Place Your Mark!")
    print("=" * 35)
    for i in range(0, 9, 3):
        row_str = " | ".join(
            f"{board[j]['mark']:^3}" if board[j]['mark'] != " " else f"{j+1:^3}"
            for j in range(i, i + 3)
        )
        print(f" {row_str} ")
        if i < 6:
            print("---*---*---")
    print("=" * 35)

def get_player_move(player, board):
    while True:
        try:
            choice = input(f"Player {player}, choose a square (1-9): ")
            if not choice.isdigit():
                print("Invalid input. Please enter a number.")
                continue
            
            square_index = int(choice) - 1

            if not 0 <= square_index <= 8:
                print("Invalid choice. Please choose a number between 1 and 9.")
                continue

            if board[square_index]["mark"] != " ":
                print("That square is already taken. Choose another one.")
                continue
            
            return square_index
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_problem_answer(problem):
    while True:
        try:
            answer = input(f"Solve the problem: {problem} = ")
            return int(answer)
        except ValueError:
            print("Invalid answer. Please enter a whole number.")

def check_win(board, player):
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for condition in win_conditions:
        if all(board[i]["mark"] == player for i in condition):
            return True
    return False

def check_draw(board):
    return all(cell["mark"] != " " for cell in board)

def switch_player(player):
    return "O" if player == "X" else "X"

def main():
    board = create_board()
    current_player = "X"

    while True:
        display_board(board)
        
        square_index = get_player_move(current_player, board)
        
        problem_data = board[square_index]
        user_answer = get_problem_answer(problem_data["problem"])

        if user_answer == problem_data["answer"]:
            print(f"Correct! Player {current_player} places an '{current_player}'.")
            board[square_index]["mark"] = current_player
        else:
            opponent = switch_player(current_player)
            print(f"Incorrect. The answer was {problem_data['answer']}. Player {opponent} places an '{opponent}'.")
            board[square_index]["mark"] = opponent
        
        input("Press Enter to continue...")

        if check_win(board, "X"):
            display_board(board)
            print("Player X wins!")
            break
        elif check_win(board, "O"):
            display_board(board)
            print("Player O wins!")
            break

        if check_draw(board):
            display_board(board)
            print("It's a draw!")
            break
        
        current_player = switch_player(current_player)

if __name__ == "__main__":
    main()
