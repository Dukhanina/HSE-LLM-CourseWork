import tkinter as tk
from tkinter import messagebox

class GameApp:
    def __init__(self, master):
        master.title("Tic-Tac-Toe")
        self.new_button = tk.Button(master, text="Новая игра", command=self.new_game)
        self.new_button.pack(pady=5)
        self.log = tk.Text(master, height=12, state=tk.NORMAL)
        self.log.pack(pady=5)
        self.entry = tk.Entry(master)
        self.entry.pack(pady=5)
        self.entry.bind('<Return>', self.on_move)
        self.move_button = tk.Button(master, text="Сделать ход", command=self.on_move)
        self.move_button.pack(pady=5)
        self.new_game()

    def new_game(self):
        self.board = [' ']*9
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
        for i in range(3):
            row = '|'.join(self.board[i*3:(i+1)*3])
            self.log.insert(tk.END, row + "\n")
        self.log.insert(tk.END, "\n")

    def on_move(self, event=None):
        try:
            n = int(self.entry.get())
            if not 1 <= n <= 9:
                raise ValueError
            pos = n - 1
            if self.board[pos] != ' ':
                raise IndexError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите число от 1 до 9")
            return
        except IndexError:
            messagebox.showerror("Ошибка", "Клетка уже занята")
            return

        self.board[pos] = self.player
        self.moves += 1
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, f"Игрок {self.player} -> {n}\n")
        self.print_board()

        lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        if any(self.board[a]==self.board[b]==self.board[c]==self.player for a,b,c in lines):
            self.log.insert(tk.END, f"Игрок {self.player} победил\n")
            self.log.config(state=tk.DISABLED)
            return

        if self.moves == 9:
            self.log.insert(tk.END, "Ничья\n")
            self.log.config(state=tk.DISABLED)
            return

        self.player = 'O' if self.player == 'X' else 'X'
        self.log.config(state=tk.DISABLED)
        self.entry.delete(0, tk.END)
        self.entry.focus()

if __name__ == '__main__':
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()
