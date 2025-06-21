import tkinter as tk
from tkinter import messagebox

class RussianCheckers:
    def __init__(self):
        self.board = self.create_board()
        self.player = 'w'
        self.pending_capture = None

    def create_board(self):
        board = [[None for _ in range(8)] for _ in range(8)]
        for i in range(3):
            for j in range(8):
                if (i + j) % 2 == 1:
                    board[i][j] = 'w'
        for i in range(5, 8):
            for j in range(8):
                if (i + j) % 2 == 1:
                    board[i][j] = 'b'
        return board

    def is_valid_position(self, pos):
        return 0 <= pos[0] < 8 and 0 <= pos[1] < 8

    def get_capture_moves(self, pos):
        moves = []
        r, c = pos
        piece = self.board[r][c]
        if not piece:
            return []
        player = piece.lower()
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] if piece in ('W', 'B') else [(-1, -1), (-1, 1)] if player == 'w' else [(1, -1), (1, 1)]
        for dr, dc in directions:
            r1, c1 = r + dr, c + dc
            r2, c2 = r + 2 * dr, c + 2 * dc
            if (self.is_valid_position((r1, c1)) and self.is_valid_position((r2, c2)) and
                self.board[r1][c1] in ('b', 'B') if player == 'w' else self.board[r1][c1] in ('w', 'W') and
                self.board[r2][c2] is None):
                moves.append((r2, c2))
        if piece in ('W', 'B'):
            for dr, dc in directions:
                r1, c1 = r + dr, c + dc
                while self.is_valid_position((r1, c1)):
                    if self.board[r1][c1] in ('b', 'B') if player == 'w' else self.board[r1][c1] in ('w', 'W'):
                        r2, c2 = r1 + dr, c1 + dc
                        if self.is_valid_position((r2, c2)) and self.board[r2][c2] is None:
                            moves.append((r2, c2))
                        break
                    elif self.board[r1][c1] is not None:
                        break
                    r1, c1 = r1 + dr, c1 + dc
        return moves

    def has_capture_moves(self):
        for i in range(8):
            for j in range(8):
                if self.board[i][j] in (self.player, self.player.upper()) and self.get_capture_moves((i, j)):
                    return True
        return False

    def get_non_capture_moves(self, pos):
        moves = []
        r, c = pos
        piece = self.board[r][c]
        if not piece:
            return []
        directions = [(-1, -1), (-1, 1)] if piece == 'w' else [(1, -1), (1, 1)] if piece == 'b' else [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            if piece in ('W', 'B'):
                r1, c1 = r + dr, c + dc
                while self.is_valid_position((r1, c1)) and self.board[r1][c1] is None:
                    moves.append((r1, c1))
                    r1, c1 = r1 + dr, c1 + dc
            else:
                r1, c1 = r + dr, c + dc
                if self.is_valid_position((r1, c1)) and self.board[r1][c1] is None:
                    moves.append((r1, c1))
        return moves

    def is_valid_move(self, start, end):
        if not (self.is_valid_position(start) and self.is_valid_position(end)):
            return False, "Неверные координаты."
        piece = self.board[start[0]][start[1]]
        if not piece or piece.lower() != self.player:
            return False, "Выберите свою шашку."
        if self.board[end[0]][end[1]] is not None:
            return False, "Конечное поле занято."
        if self.has_capture_moves():
            return False, "Необходимо выполнить взятие."
        moves = self.get_non_capture_moves(start)
        if end not in moves:
            return False, "Ход не по диагонали или неправильное направление."
        return True, ""

    def is_valid_capture(self, start, end):
        if not (self.is_valid_position(start) and self.is_valid_position(end)):
            return False, "Неверные координаты."
        piece = self.board[start[0]][start[1]]
        if not piece or piece.lower() != self.player:
            return False, "Выберите свою шашку."
        if self.board[end[0]][end[1]] is not None:
            return False, "Конечное поле занято."
        moves = self.get_capture_moves(start)
        if end not in moves:
            return False, "Недопустимое взятие."
        return True, ""

    def make_move(self, start, end):
        piece = self.board[start[0]][start[1]]
        self.board[start[0]][start[1]] = None
        self.board[end[0]][end[1]] = piece
        if piece == 'w' and end[0] == 0:
            self.board[end[0]][end[1]] = 'W'
        if piece == 'b' and end[0] == 7:
            self.board[end[0]][end[1]] = 'B'

    def make_capture(self, start, end):
        piece = self.board[start[0]][start[1]]
        self.board[start[0]][start[1]] = None
        self.board[end[0]][end[1]] = piece
        dr = -1 if end[0] < start[0] else 1
        dc = -1 if end[1] < start[1] else 1
        r, c = start[0] + dr, start[1] + dc
        while (r, c) != (end[0], end[1]):
            if self.board[r][c] is not None:
                self.board[r][c] = None
            r += dr
            c += dc
        if piece == 'w' and end[0] == 0:
            self.board[end[0]][end[1]] = 'W'
        if piece == 'b' and end[0] == 7:
            self.board[end[0]][end[1]] = 'B'

    def check_for_win(self):
        white_pieces = sum(row.count('w') + row.count('W') for row in self.board)
        black_pieces = sum(row.count('b') + row.count('B') for row in self.board)
        if white_pieces == 0:
            return 'b'
        if black_pieces == 0:
            return 'w'
        all_possible_moves = []
        for r in range(8):
            for c in range(8):
                if self.board[r][c] in (self.player, self.player.upper()):
                    all_possible_moves.extend(self.get_non_capture_moves((r, c)) if not self.has_capture_moves() else self.get_capture_moves((r, c)))
        if not all_possible_moves:
            return 'b' if self.player == 'w' else 'w'
        return None

class CheckersGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Русские шашки")
        self.game = RussianCheckers()
        self.game_over = False
        self.dragging_piece = None
        self.dragging_start = None
        self.dragging_items = None
        self.valid_moves = []
        self.canvas = tk.Canvas(self, width=400, height=400)
        self.canvas.pack(pady=10)
        self.log_text = tk.Text(self, height=5, width=50, state='disabled')
        self.log_text.pack(pady=5)
        self.status_label = tk.Label(self, text=f"Ход игрока {self.game.player}")
        self.status_label.pack(pady=5)
        self.new_game_button = tk.Button(self, text="Новая игра", command=self.new_game)
        self.new_game_button.pack(pady=5)
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag_piece)
        self.canvas.bind("<ButtonRelease-1>", self.drop_piece)
        self.draw_board()
        self.update_log(f"Ход игрока {self.game.player}")

    def draw_board(self):
        self.canvas.delete("all")
        square_size = 50
        for r in range(8):
            for c in range(8):
                x1 = c * square_size
                y1 = r * square_size
                x2 = x1 + square_size
                y2 = y1 + square_size
                color = "#8B4513" if (r + c) % 2 == 1 else "#F5F5DC"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags=f"square_{r}_{c}")
                piece = self.game.board[r][c]
                if piece:
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    radius = square_size // 3
                    fill = "white" if piece in ('w', 'W') else "black"
                    self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, 
                                            fill=fill, tags=f"piece_{r}_{c}")
                    if piece in ('W', 'B'):
                        self.canvas.create_text(cx, cy, text="D", fill="red", font=("Arial", 12, "bold"), 
                                                tags=f"piece_{r}_{c}")

    def update_log(self, message):
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state='disabled')

    def start_drag(self, event):
        if self.game_over:
            messagebox.showinfo("Игра окончена", "Начните новую игру.")
            return
        x, y = event.x, event.y
        square_size = 50
        col = x // square_size
        row = y // square_size
        if not self.is_valid_position((row, col)):
            return
        piece = self.game.board[row][col]
        if not piece:
            return
        if piece.lower() != self.game.player:
            messagebox.showerror("Ошибка", "Выберите свою шашку.")
            return
        if self.game.pending_capture and (row, col) != self.game.pending_capture:
            messagebox.showerror("Ошибка", "Продолжите взятие с последней позиции.")
            return
        items = self.canvas.find_withtag(f"piece_{row}_{col}")
        if not items:
            return
        self.dragging_start = (row, col)
        self.dragging_piece = piece
        self.dragging_items = items
        for item in items:
            self.canvas.tag_raise(item)
        self.valid_moves = self.game.get_capture_moves((row, col)) if self.game.has_capture_moves() else self.game.get_non_capture_moves((row, col))
        for move in self.valid_moves:
            self.canvas.itemconfig(f"square_{move[0]}_{move[1]}", outline="green", width=2)

    def drag_piece(self, event):
        if self.dragging_items:
            x, y = event.x, event.y
            for item in self.dragging_items:
                if "oval" in self.canvas.gettags(item):
                    self.canvas.coords(item, x - 20, y - 20, x + 20, y + 20)
                elif "text" in self.canvas.gettags(item):
                    self.canvas.coords(item, x, y)

    def drop_piece(self, event):
        if not self.dragging_piece:
            return
        x, y = event.x, event.y
        square_size = 50
        col = x // square_size
        row = y // square_size
        if not self.is_valid_position((row, col)):
            self.reset_drag()
            return
        end = (row, col)
        if end == self.dragging_start:
            self.reset_drag()
            return
        self.process_move(self.dragging_start, end)
        self.reset_drag()

    def reset_drag(self):
        for r in range(8):
            for c in range(8):
                self.canvas.itemconfig(f"square_{r}_{c}", outline="")
        self.dragging_piece = None
        self.dragging_start = None
        self.dragging_items = None
        self.valid_moves = []
        self.draw_board()

    def is_valid_position(self, pos):
        return 0 <= pos[0] < 8 and 0 <= pos[1] < 8

    def process_move(self, start, end):
        if self.game.has_capture_moves():
            valid, msg = self.game.is_valid_capture(start, end)
            if valid:
                self.game.make_capture(start, end)
                self.update_log(f"Игрок {self.game.player} взял шашку.")
                if self.game.get_capture_moves(end):
                    messagebox.showinfo("Продолжайте", "Вы должны продолжить взятие!")
                    self.game.pending_capture = end
                    self.draw_board()
                    return
                self.game.pending_capture = None
                self.game.player = 'b' if self.game.player == 'w' else 'w'
                self.status_label.config(text=f"Ход игрока {self.game.player}")
            else:
                messagebox.showerror("Ошибка", msg)
                return
        else:
            valid, msg = self.game.is_valid_move(start, end)
            if valid:
                self.game.make_move(start, end)
                self.update_log(f"Игрок {self.game.player} сделал ход.")
                self.game.player = 'b' if self.game.player == 'w' else 'w'
                self.status_label.config(text=f"Ход игрока {self.game.player}")
            else:
                messagebox.showerror("Ошибка", msg)
                return
        self.draw_board()
        win_status = self.game.check_for_win()
        if win_status:
            messagebox.showinfo("Игра окончена", f"Игрок {win_status} победил!")
            self.game_over = True

    def new_game(self):
        self.game = RussianCheckers()
        self.game_over = False
        self.dragging_piece = None
        self.dragging_start = None
        self.dragging_items = None
        self.valid_moves = []
        self.status_label.config(text=f"Ход игрока {self.game.player}")
        self.draw_board()
        self.update_log(f"Ход игрока {self.game.player}")

if __name__ == "__main__":
    game = CheckersGame()
    game.mainloop()
