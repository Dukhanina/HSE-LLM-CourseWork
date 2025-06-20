import tkinter as tk
from tkinter import messagebox

board = [[' ' for _ in range(7)] for _ in range(6)]
current_player = 'R'
game_over = False

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

def print_board_gui():
    board_text.config(state='normal')
    board_text.delete(1.0, tk.END)
    board_text.insert(tk.END, "1 2 3 4 5 6 7\n")
    for r in range(5,-1,-1):
        row = [board[r][c] if board[r][c] != ' ' else '.' for c in range(7)]
        board_text.insert(tk.END, ' '.join(row) + '\n')
    board_text.config(state='disabled')

def make_move():
    global current_player, game_over
    if game_over:
        messagebox.showinfo("Информация", "Игра окончена. Начните новую игру.")
        return
    try:
        col = int(entry.get()) - 1
        if col < 0 or col > 6:
            messagebox.showerror("Ошибка", "Недопустимый столбец. Выберите от 1 до 7.")
            return
    except ValueError:
        messagebox.showerror("Ошибка", "Недопустимый ввод. Введите число.")
        return
    placed = False
    for r in range(6):
        if board[r][col] == ' ':
            board[r][col] = current_player
            placed = True
            break
    if not placed:
        messagebox.showerror("Ошибка", "Столбец заполнен. Выберите другой.")
        return
    print_board_gui()
    if check_win(board, current_player):
        status_label.config(text=f"Игрок {current_player} победил!")
        messagebox.showinfo("Поздравляем", f"Игрок {current_player} победил!")
        game_over = True
        make_move_button.config(state=tk.DISABLED)
        entry.config(state=tk.DISABLED)
    elif all(cell != ' ' for row in board for cell in row):
        status_label.config(text="Ничья!")
        messagebox.showinfo("Ничья", "Игра закончилась вничью!")
        game_over = True
        make_move_button.config(state=tk.DISABLED)
        entry.config(state=tk.DISABLED)
    else:
        current_player = 'Y' if current_player == 'R' else 'R'
        status_label.config(text=f"Ход игрока {current_player}")
    entry.delete(0, tk.END)

def new_game():
    global board, current_player, game_over
    board = [[' ' for _ in range(7)] for _ in range(6)]
    current_player = 'R'
    game_over = False
    print_board_gui()
    status_label.config(text=f"Ход игрока {current_player}")
    make_move_button.config(state=tk.NORMAL)
    entry.config(state=tk.NORMAL)
    entry.delete(0, tk.END)

root = tk.Tk()
root.title("Connect 4")

board_text = tk.Text(root, height=7, width=20, state='disabled')
board_text.pack()

status_label = tk.Label(root, text="")
status_label.pack()

entry = tk.Entry(root)
entry.pack()

button_frame = tk.Frame(root)
button_frame.pack()
make_move_button = tk.Button(button_frame, text="Сделать ход", command=make_move)
make_move_button.pack(side=tk.LEFT)
new_game_button = tk.Button(button_frame, text="Новая игра", command=new_game)
new_game_button.pack(side=tk.LEFT)

new_game()
root.mainloop()
