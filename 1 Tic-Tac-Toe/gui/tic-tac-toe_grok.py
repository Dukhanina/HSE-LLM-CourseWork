import tkinter as tk
from tkinter import messagebox

# Глобальные переменные
board = [[" " for _ in range(3)] for _ in range(3)]
current_player = "X"
game_over = False

# Функции
def check_win(board, player):
    for i in range(3):
        if all(board[i][j] == player for j in range(3)):
            return True
    for j in range(3):
        if all(board[i][j] == player for i in range(3)):
            return True
    if all(board[i][i] == player for i in range(3)):
        return True
    if all(board[i][2 - i] == player for i in range(3)):
        return True
    return False

def is_board_full(board):
    for i in range(3):
        for j in range(3):
            if board[i][j] == " ":
                return False
    return True

def print_board_gui():
    text_widget.config(state='normal')
    text_widget.delete(1.0, tk.END)
    for i in range(3):
        line = ""
        for j in range(3):
            if board[i][j] == " ":
                line += str(i*3 + j + 1)
            else:
                line += board[i][j]
            if j < 2:
                line += " | "
        text_widget.insert(tk.END, line + "\n")
        if i < 2:
            text_widget.insert(tk.END, "---------\n")
    text_widget.config(state='disabled')

def make_move_gui():
    global current_player, game_over
    if game_over:
        messagebox.showinfo("Информация", "Игра окончена. Начните новую игру.")
        return
    try:
        move = int(entry.get())
        if move < 1 or move > 9:
            raise ValueError
    except ValueError:
        messagebox.showerror("Ошибка", "Недопустимый ход. Введите число от 1 до 9.")
        entry.delete(0, tk.END)
        return
    row = (move - 1) // 3
    col = (move - 1) % 3
    if board[row][col] != " ":
        messagebox.showerror("Ошибка", "Эта клетка уже занята. Выберите другую.")
        entry.delete(0, tk.END)
        return
    board[row][col] = current_player
    print_board_gui()
    if check_win(board, current_player):
        status_label.config(text=f"Игрок {current_player} победил!")
        messagebox.showinfo("Поздравляем", f"Игрок {current_player} победил!")
        game_over = True
        make_move_button.config(state=tk.DISABLED)
        entry.config(state=tk.DISABLED)
    elif is_board_full(board):
        status_label.config(text="Ничья!")
        messagebox.showinfo("Ничья", "Игра закончилась вничью!")
        game_over = True
        make_move_button.config(state=tk.DISABLED)
        entry.config(state=tk.DISABLED)
    else:
        current_player = "O" if current_player == "X" else "X"
        status_label.config(text=f"Ход игрока {current_player}")
    entry.delete(0, tk.END)

def new_game():
    global board, current_player, game_over
    board = [[" " for _ in range(3)] for _ in range(3)]
    current_player = "X"
    game_over = False
    print_board_gui()
    status_label.config(text=f"Ход игрока {current_player}")
    entry.delete(0, tk.END)
    entry.config(state=tk.NORMAL)
    make_move_button.config(state=tk.NORMAL)

# Основной код
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Крестики-нолики")

    text_widget = tk.Text(root, state='disabled', height=10, width=30)
    text_widget.pack()

    status_label = tk.Label(root, text="")
    status_label.pack()

    entry = tk.Entry(root)
    entry.pack()

    button_frame = tk.Frame(root)
    button_frame.pack()

    make_move_button = tk.Button(button_frame, text="Сделать ход", command=make_move_gui)
    make_move_button.pack(side=tk.LEFT)

    new_game_button = tk.Button(button_frame, text="Новая игра", command=new_game)
    new_game_button.pack(side=tk.LEFT)

    new_game()  # Запуск новой игры
    root.mainloop()
