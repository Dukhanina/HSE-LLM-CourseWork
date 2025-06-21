import tkinter as tk
from tkinter import messagebox, scrolledtext

class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        
        self.setup_ui()
        self.new_game()
    
    def setup_ui(self):
        # Создание кнопки новой игры
        self.btn_new = tk.Button(self.root, text="Новая игра", command=self.new_game)
        self.btn_new.pack(pady=10)
        
        # Создание игрового поля
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack()
        self.buttons = []
        for i in range(3):
            row = []
            for j in range(3):
                btn = tk.Button(self.board_frame, text=" ", width=5, height=2,
                                font=('Arial', 16), 
                                command=lambda i=i, j=j: self.make_move(i, j))
                btn.grid(row=i, column=j, padx=5, pady=5)
                row.append(btn)
            self.buttons.append(row)
        
        # Создание поля для логов
        self.log_area = scrolledtext.ScrolledText(self.root, width=30, height=10, state='disabled')
        self.log_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    
    def new_game(self):
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.game_over = False
        self.update_board()
        self.log("Новая игра начата. Первый ход: X")
    
    def make_move(self, row, col):
        if self.game_over:
            return
            
        if self.board[row][col] != " ":
            messagebox.showerror("Недопустимый ход", "Эта клетка уже занята!")
            return
            
        self.board[row][col] = self.current_player
        self.log(f"Игрок {self.current_player}: [{row+1},{col+1}]")
        self.update_board()
        
        if self.check_win():
            self.log(f"Игрок {self.current_player} победил!")
            self.game_over = True
            return
        
        if self.is_draw():
            self.log("Ничья!")
            self.game_over = True
            return
            
        self.current_player = "O" if self.current_player == "X" else "X"
    
    def check_win(self):
        # Проверка строк
        for row in self.board:
            if row[0] == row[1] == row[2] != " ":
                return True
        # Проверка столбцов
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != " ":
                return True
        # Проверка диагоналей
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
            return True
        return False
    
    def is_draw(self):
        for row in self.board:
            if " " in row:
                return False
        return True
    
    def update_board(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text=self.board[i][j])
    
    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.yview(tk.END)
        self.log_area.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.mainloop()
