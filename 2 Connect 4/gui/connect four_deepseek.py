import tkinter as tk
from tkinter import messagebox

class ConnectFour:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect Four")
        self.rows, self.cols = 6, 7
        self.cell_size = 60
        self.setup_ui()
        self.new_game()
    
    def setup_ui(self):
        self.btn_new = tk.Button(self.root, text="Новая игра", command=self.new_game)
        self.btn_new.pack(pady=10)
        
        self.canvas = tk.Canvas(self.root, width=self.cols*self.cell_size, 
                               height=self.rows*self.cell_size, bg="blue")
        self.canvas.pack(padx=10, pady=5)
        self.canvas.bind("<Motion>", self.hover)
        self.canvas.bind("<Button-1>", self.click)
        
        self.status = tk.Label(self.root, text="Ход игрока: 🔴", font=("Arial", 12))
        self.status.pack(pady=5)
        
        self.log_area = tk.Text(self.root, width=40, height=8, state="disabled")
        self.log_area.pack(pady=10, padx=10)
    
    def new_game(self):
        self.board = [["" for _ in range(self.cols)] for _ in range(self.rows)]
        self.current_player = "🔴"
        self.game_over = False
        self.log("Новая игра начата. Первый ход: 🔴")
        self.status.config(text="Ход игрока: 🔴")
        self.draw_board()
    
    def draw_board(self):
        self.canvas.delete("all")
        for row in range(self.rows):
            for col in range(self.cols):
                x0 = col * self.cell_size
                y0 = row * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                self.canvas.create_oval(x0+5, y0+5, x1-5, y1-5, fill="white", outline="blue", tags="cell")
                
                if self.board[row][col] == "🔴":
                    self.canvas.create_oval(x0+5, y0+5, x1-5, y1-5, fill="red", outline="darkred")
                elif self.board[row][col] == "🟡":
                    self.canvas.create_oval(x0+5, y0+5, x1-5, y1-5, fill="yellow", outline="goldenrod")
    
    def hover(self, event):
        if self.game_over: return
        col = event.x // self.cell_size
        if 0 <= col < self.cols:
            self.canvas.delete("preview")
            row = self.find_empty_row(col)
            if row != -1:
                x0 = col * self.cell_size
                y0 = row * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                fill = "red" if self.current_player == "🔴" else "yellow"
                self.canvas.create_oval(x0+5, y0+5, x1-5, y1-5, fill=fill, outline="white", tags="preview")
    
    def find_empty_row(self, col):
        for row in range(self.rows-1, -1, -1):
            if not self.board[row][col]:
                return row
        return -1
    
    def click(self, event):
        if self.game_over: return
        col = event.x // self.cell_size
        if not (0 <= col < self.cols): return
        
        row = self.find_empty_row(col)
        if row == -1:
            messagebox.showwarning("Недопустимый ход", "Эта колонка заполнена!")
            return
        
        self.board[row][col] = self.current_player
        self.log(f"Игрок {self.current_player}: колонка {col+1}")
        self.draw_board()
        
        if self.check_win(row, col):
            self.log(f"Игрок {self.current_player} победил!")
            self.game_over = True
            self.status.config(text=f"Победил: {self.current_player}")
            return
        
        if self.is_draw():
            self.log("Ничья!")
            self.game_over = True
            self.status.config(text="Ничья!")
            return
        
        self.current_player = "🟡" if self.current_player == "🔴" else "🔴"
        self.status.config(text=f"Ход игрока: {self.current_player}")
    
    def check_win(self, row, col):
        player = self.board[row][col]
        directions = [
            [(0, 1), (0, -1)],   # Горизонталь
            [(1, 0), (-1, 0)],    # Вертикаль
            [(1, 1), (-1, -1)],   # Диагональ /
            [(1, -1), (-1, 1)]    # Диагональ \
        ]
        
        for dir_pair in directions:
            count = 1
            for dx, dy in dir_pair:
                r, c = row + dx, col + dy
                while 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] == player:
                    count += 1
                    r += dx
                    c += dy
            if count >= 4:
                return True
        return False
    
    def is_draw(self):
        return all(self.board[0][col] for col in range(self.cols))
    
    def log(self, message):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.yview(tk.END)
        self.log_area.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    game = ConnectFour(root)
    root.mainloop()
