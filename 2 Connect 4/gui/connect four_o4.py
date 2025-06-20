import tkinter as tk
from tkinter import messagebox

ROWS = 6
COLS = 7

def make_move(board, col, player):
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == ' ':
            board[r][col] = player
            return True
    return False

def check_win(board, player):
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] != player:
                continue
            if c <= COLS - 4 and all(board[r][c + i] == player for i in range(4)):
                return True
            if r <= ROWS - 4 and all(board[r + i][c] == player for i in range(4)):
                return True
            if r <= ROWS - 4 and c <= COLS - 4 and all(board[r + i][c + i] == player for i in range(4)):
                return True
            if r >= 3 and c <= COLS - 4 and all(board[r - i][c + i] == player for i in range(4)):
                return True
    return False

class Connect4App:
    def __init__(self, master):
        master.title("Connect 4")
        self.new_button = tk.Button(master, text="Новая игра", command=self.new_game)
        self.new_button.pack(pady=5)
        self.log = tk.Text(master, height=15, state=tk.NORMAL)
        self.log.pack(pady=5)
        self.entry = tk.Entry(master)
        self.entry.pack(pady=5)
        self.entry.bind('<Return>', self.on_move)
        self.move_button = tk.Button(master, text="Сделать ход", command=self.on_move)
        self.move_button.pack(pady=5)
        self.new_game()

    def new_game(self):
        self.board = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        self.player = 'X'
        self.moves = 0
        self.log.config(state=tk.NORMAL)
        self.log.delete('1.0', tk.END)
        self.log.insert(tk.END, "Новая игра\n")
        self.print_board()
        self.log.config(state=tk.DISABLED)
        self.entry.delete(0, tk.END)
        self.entry.focus()

    def print_board(self):
        header = ' '.join(str(i+1) for i in range(COLS))
        self.log.insert(tk.END, header + "\n")
        for row in self.board:
            self.log.insert(tk.END, '|' + '|'.join(row) + '|\n')
        self.log.insert(tk.END, "\n")

    def on_move(self, event=None):
        try:
            n = int(self.entry.get())
            if not 1 <= n <= COLS:
                raise ValueError
            col = n - 1
            if self.board[0][col] != ' ':
                raise IndexError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите число от 1 до 7")
            return
        except IndexError:
            messagebox.showerror("Ошибка", "Столбец заполнен")
            return

        make_move(self.board, col, self.player)
        self.moves += 1
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, f"Игрок {self.player} -> столбец {n}\n")
        self.print_board()

        if check_win(self.board, self.player):
            self.log.insert(tk.END, f"Игрок {self.player} победил\n")
            self.log.config(state=tk.DISABLED)
            return

        if self.moves == ROWS * COLS:
            self.log.insert(tk.END, "Ничья\n")
            self.log.config(state=tk.DISABLED)
            return

        self.player = 'O' if self.player == 'X' else 'X'
        self.log.config(state=tk.DISABLED)
        self.entry.delete(0, tk.END)
        self.entry.focus()

if __name__ == '__main__':
    root = tk.Tk()
    app = Connect4App(root)
    root.mainloop()
