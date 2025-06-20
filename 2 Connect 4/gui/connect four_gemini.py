import tkinter as tk
from tkinter import messagebox, scrolledtext

class ConnectFourGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("4 в ряд")
        self.master.configure(bg='#f0f0f0')
        self.master.resizable(False, False)

        self.ROWS = 6
        self.COLS = 7
        self.PLAYER_ONE_PIECE = 'R'
        self.PLAYER_TWO_PIECE = 'Y'
        self.EMPTY_SLOT = ' '

        self.board = []
        self.game_over = True
        self.current_player = self.PLAYER_ONE_PIECE

        # UI constants
        self.SQUARESIZE = 80
        self.RADIUS = int(self.SQUARESIZE / 2 - 5)
        self.WIDTH = self.COLS * self.SQUARESIZE
        self.HEIGHT = (self.ROWS + 1) * self.SQUARESIZE
        self.COLORS = {'R': 'red', 'Y': 'yellow', 'BOARD': 'blue', 'EMPTY': 'white'}

        self._create_widgets()
        self.new_game()

    def _create_widgets(self):
        # Top Frame for controls
        control_frame = tk.Frame(self.master, pady=5, bg='#f0f0f0')
        control_frame.pack(fill=tk.X)

        self.new_game_button = tk.Button(control_frame, text="Новая игра", command=self.new_game)
        self.new_game_button.pack(side=tk.LEFT, padx=10)
        
        self.status_label = tk.Label(control_frame, text="", font=('Helvetica', 12, 'bold'), bg='#f0f0f0')
        self.status_label.pack(side=tk.LEFT, expand=True)

        # Canvas for the game board
        self.canvas = tk.Canvas(self.master, width=self.WIDTH, height=self.HEIGHT, bg=self.COLORS['BOARD'])
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_mouse_hover)

        # Log Frame
        log_frame = tk.Frame(self.master, padx=10, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_widget = scrolledtext.ScrolledText(log_frame, state='disabled', height=6, wrap=tk.WORD, font=('Arial', 10))
        self.log_widget.pack(fill=tk.BOTH, expand=True)

    def new_game(self):
        self.board = [[self.EMPTY_SLOT for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.current_player = self.PLAYER_ONE_PIECE
        self.game_over = False
        self.log_widget.config(state='normal')
        self.log_widget.delete('1.0', tk.END)
        self.log_widget.config(state='disabled')
        self._log("Началась новая игра!")
        self._update_status()
        self._draw_board()

    def _draw_board(self):
        self.canvas.delete("all")
        for c in range(self.COLS):
            for r in range(self.ROWS):
                x1 = c * self.SQUARESIZE
                y1 = (self.ROWS - 1 - r) * self.SQUARESIZE + self.SQUARESIZE
                x2 = x1 + self.SQUARESIZE
                y2 = y1 + self.SQUARESIZE
                
                fill_color = self.COLORS['EMPTY']
                if self.board[r][c] == self.PLAYER_ONE_PIECE:
                    fill_color = self.COLORS['R']
                elif self.board[r][c] == self.PLAYER_TWO_PIECE:
                    fill_color = self.COLORS['Y']
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.COLORS['BOARD'], outline=self.COLORS['BOARD'])
                self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill=fill_color, outline=self.COLORS['BOARD'])

    def _log(self, message):
        self.log_widget.config(state='normal')
        self.log_widget.insert(tk.END, message + "\n")
        self.log_widget.see(tk.END)
        self.log_widget.config(state='disabled')

    def _update_status(self):
        if not self.game_over:
            text = f"Ход игрока: {self.current_player}"
            color = self.COLORS[self.current_player]
            self.status_label.config(text=text, fg=color)
        else:
            self.status_label.config(text="Игра окончена!", fg='black')

    def on_canvas_click(self, event):
        if self.game_over:
            messagebox.showwarning("Игра окончена", "Игра завершена. Начните новую, чтобы продолжить.")
            return

        col = event.x // self.SQUARESIZE
        
        if 0 <= col < self.COLS:
            if self._is_valid_location(col):
                row = self._get_next_open_row(col)
                self._drop_piece(row, col, self.current_player)
                self._log(f"Игрок {self.current_player} сделал ход в колонку {col}.")
                self._draw_board()

                if self._winning_move(self.current_player):
                    self.game_over = True
                    winner_msg = f"Игрок {self.current_player} победил!"
                    self._log(winner_msg)
                    self._update_status()
                    messagebox.showinfo("Победа!", winner_msg)
                elif self._is_board_full():
                    self.game_over = True
                    self._log("Игра окончена. Ничья!")
                    self._update_status()
                    messagebox.showinfo("Ничья", "Поле заполнено. Ничья!")
                else:
                    self.current_player = self.PLAYER_TWO_PIECE if self.current_player == self.PLAYER_ONE_PIECE else self.PLAYER_ONE_PIECE
                    self._update_status()
            else:
                messagebox.showerror("Недопустимый ход", "Эта колонка уже заполнена.")
        
    def on_mouse_hover(self, event):
        if self.game_over:
            return
        
        self.canvas.delete("hover")
        col = event.x // self.SQUARESIZE
        if 0 <= col < self.COLS:
            x = col * self.SQUARESIZE + self.SQUARESIZE/2
            color = self.COLORS[self.current_player]
            self.canvas.create_oval(x - self.RADIUS, 5, x + self.RADIUS, self.SQUARESIZE - 5, 
                                    fill=color, outline=self.COLORS['BOARD'], tags="hover")

    def _drop_piece(self, row, col, piece):
        self.board[row][col] = piece

    def _is_valid_location(self, col):
        return self.board[self.ROWS - 1][col] == self.EMPTY_SLOT

    def _get_next_open_row(self, col):
        for r in range(self.ROWS):
            if self.board[r][col] == self.EMPTY_SLOT:
                return r
        return None

    def _is_board_full(self):
        for r in range(self.ROWS):
            for c in range(self.COLS):
                if self.board[r][c] == self.EMPTY_SLOT:
                    return False
        return True

    def _winning_move(self, piece):
        for c in range(self.COLS - 3):
            for r in range(self.ROWS):
                if all(self.board[r][c + i] == piece for i in range(4)):
                    return True
        for c in range(self.COLS):
            for r in range(self.ROWS - 3):
                if all(self.board[r + i][c] == piece for i in range(4)):
                    return True
        for c in range(self.COLS - 3):
            for r in range(self.ROWS - 3):
                if all(self.board[r + i][c + i] == piece for i in range(4)):
                    return True
        for c in range(self.COLS - 3):
            for r in range(3, self.ROWS):
                if all(self.board[r - i][c + i] == piece for i in range(4)):
                    return True
        return False

if __name__ == "__main__":
    root = tk.Tk()
    app = ConnectFourGUI(root)
    root.mainloop()
