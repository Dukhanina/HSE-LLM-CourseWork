import tkinter as tk
from tkinter import messagebox

class RussianCheckersGUI:
    def __init__(self, master):
        self.master = master
        master.title("Русские шашки")
        
        self.game = RussianCheckers()
        self.selected_piece = None
        
        # Создаем фреймы
        control_frame = tk.Frame(master)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        board_frame = tk.Frame(master)
        board_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        log_frame = tk.Frame(master)
        log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Элементы управления
        self.new_game_btn = tk.Button(control_frame, text="Новая игра", command=self.new_game)
        self.new_game_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.status_label = tk.Label(control_frame, text="Ход: Белые", font=("Arial", 12))
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # Логи
        self.log_text = tk.Text(log_frame, height=20, width=40)
        self.log_scroll = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=self.log_scroll.set)
        
        self.log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.log("Игра началась. Ходят белые.")
        
        # Доска
        self.canvas = tk.Canvas(board_frame, width=400, height=400)
        self.canvas.pack()
        self.draw_board()
        
        # Привязка событий
        self.canvas.bind("<Button-1>", self.on_click)
        
    def new_game(self):
        self.game = RussianCheckers()
        self.selected_piece = None
        self.update_status()
        self.draw_board()
        self.log("\n=== Новая игра ===")
        self.log("Ходят белые.")
        
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        
    def update_status(self):
        player = "Белые" if self.game.current_player == 'w' else "Черные"
        status = f"Ход: {player}"
        if self.game.chain_capture:
            status += " (цепное взятие)"
        self.status_label.config(text=status)
        
    def draw_board(self):
        self.canvas.delete("all")
        cell_size = 50
        colors = ["#f0d9b5", "#b58863"]
        
        # Рисуем доску
        for row in range(8):
            for col in range(8):
                x1, y1 = col * cell_size, row * cell_size
                x2, y2 = x1 + cell_size, y1 + cell_size
                color_idx = (row + col) % 2
                color = colors[color_idx]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                
                # Рисуем шашки
                piece = self.game.board[row][col]
                if piece != ' ':
                    cx, cy = x1 + cell_size//2, y1 + cell_size//2
                    radius = 20
                    
                    # Цвет шашки
                    fill_color = "white" if piece.lower() == 'w' else "black"
                    outline = "red" if (self.selected_piece == (row, col)) else "black"
                    
                    # Рисуем шашку
                    self.canvas.create_oval(
                        cx - radius, cy - radius,
                        cx + radius, cy + radius,
                        fill=fill_color, outline=outline, width=2
                    )
                    
                    # Дамка (корона)
                    if piece.isupper():
                        crown_size = 10
                        self.canvas.create_oval(
                            cx - crown_size, cy - crown_size,
                            cx + crown_size, cy + crown_size,
                            fill="gold", outline=""
                        )
    
    def on_click(self, event):
        if self.game.game_over:
            return
            
        col = event.x // 50
        row = event.y // 50
        
        # Проверка границ
        if not (0 <= row < 8 and 0 <= col < 8):
            return
            
        piece = self.game.board[row][col]
        player = self.game.current_player
        
        # Режим цепного взятия
        if self.game.chain_capture:
            if (row, col) == self.game.chain_piece:
                return
                
            start = self.game.chain_piece
            moves = self.game.get_valid_moves(*start)
            move = next((m for m in moves if m[0] == row and m[1] == col), None)
            
            if move:
                self.make_move(start, (row, col), move[2])
            else:
                messagebox.showwarning("Недопустимый ход", 
                    "Продолжите цепное взятие или завершите ход")
            return
            
        # Выбор шашки
        if self.selected_piece is None:
            if piece != ' ' and piece.lower() == player:
                # Проверка обязательного взятия
                if self.game.has_any_capture(player):
                    moves = self.game.get_valid_moves(row, col)
                    if not any(m[2] for m in moves):
                        messagebox.showwarning("Обязательное взятие", 
                            "Вы должны выбрать шашку, которая может бить")
                        return
                        
                self.selected_piece = (row, col)
                self.draw_board()
            return
            
        # Попытка хода
        start = self.selected_piece
        moves = self.game.get_valid_moves(*start)
        move = next((m for m in moves if m[0] == row and m[1] == col), None)
        
        if move:
            self.make_move(start, (row, col), move[2])
        else:
            # Попытка выбрать другую шашку
            if piece != ' ' and piece.lower() == player:
                self.selected_piece = (row, col)
                self.draw_board()
            else:
                messagebox.showwarning("Недопустимый ход", 
                    "Выбран недопустимый ход")
    
    def make_move(self, start, end, captures):
        start_row, start_col = start
        end_row, end_col = end
        piece = self.game.board[start_row][start_col]
        player = self.game.current_player
        player_name = "Белые" if player == 'w' else "Черные"
        
        # Логирование
        move_desc = f"{player_name}: {start} -> {end}"
        if captures:
            move_desc += f" (взято: {len(captures)})"
        self.log(move_desc)
        
        # Выполнение хода
        if captures:
            self.game.execute_capture(start, end, captures)
            
            # Проверка цепного взятия
            if self.game.find_captures(end_row, end_col, piece, set()):
                self.game.chain_capture = True
                self.game.chain_piece = end
                self.selected_piece = end
                self.log(f"{player_name} продолжают взятие")
            else:
                self.game.chain_capture = False
                self.game.chain_piece = None
                self.selected_piece = None
                self.game.current_player = 'b' if player == 'w' else 'w'
        else:
            self.game.move_piece(start, end)
            self.selected_piece = None
            self.game.current_player = 'b' if player == 'w' else 'w'
        
        # Проверка на превращение в дамку
        piece_after_move = self.game.board[end_row][end_col]
        if piece_after_move == 'w' and end_row == 0:
            self.game.board[end_row][end_col] = 'W'
            self.log("Белая шашка стала дамкой!")
        elif piece_after_move == 'b' and end_row == 7:
            self.game.board[end_row][end_col] = 'B'
            self.log("Черная шашка стала дамкой!")
        
        # Проверка победы
        winner = self.game.check_winner()
        if winner:
            winner_name = "Белые" if winner == 'w' else "Черные"
            self.log(f"Победили {winner_name}!")
            messagebox.showinfo("Игра окончена", f"Победили {winner_name}!")
            self.game.game_over = True
        
        self.update_status()
        self.draw_board()

class RussianCheckers:
    def __init__(self):
        self.board = self.create_board()
        self.current_player = 'w'
        self.game_over = False
        self.chain_capture = False
        self.chain_piece = None

    def create_board(self):
        board = [[' ' for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    if row < 3:
                        board[row][col] = 'b'
                    elif row > 4:
                        board[row][col] = 'w'
        return board

    def get_valid_moves(self, row, col):
        piece = self.board[row][col]
        if piece == ' ': 
            return []
            
        captures = self.find_captures(row, col, piece, set())
        if captures:
            return captures
            
        moves = []
        player = piece.lower()
        is_king = piece.isupper()
        
        # Определяем направления движения
        directions = []
        if player == 'w' or is_king:
            directions.extend([(-1, -1), (-1, 1)])  # Вверх для белых
        if player == 'b' or is_king:
            directions.extend([(1, -1), (1, 1)])    # Вниз для черных
        
        # Для дамок - длинные ходы
        if is_king:
            for dr, dc in directions:
                r, c = row + dr, col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    if self.board[r][c] == ' ':
                        moves.append((r, c, []))
                        r += dr
                        c += dc
                    else:
                        break
        else:
            # Для обычных шашек - только на 1 клетку
            for dr, dc in directions:
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == ' ':
                    moves.append((r, c, []))
        
        return moves

    def find_captures(self, row, col, piece, visited, path=None):
        if path is None:
            path = []
        captures = []
        player = piece.lower()
        is_king = piece.isupper()
        directions = [(-1,-1), (-1,1), (1,-1), (1,1)]
        
        for dr, dc in directions:
            # Для обычных шашек проверяем только ближайшую клетку
            if not is_king:
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    target = self.board[r][c]
                    if target != ' ' and target.lower() != player:
                        # Проверяем клетку за целью
                        r2, c2 = r + dr, c + dc
                        if 0 <= r2 < 8 and 0 <= c2 < 8 and self.board[r2][c2] == ' ':
                            # Проверяем, не брали ли уже эту шашку
                            if (r, c) not in visited:
                                new_visited = visited | {(r, c)}
                                new_path = path + [(r, c)]
                                
                                # Рекурсивно ищем продолжение взятия
                                extended = self.find_captures(r2, c2, piece, new_visited, new_path)
                                if extended:
                                    captures.extend(extended)
                                else:
                                    captures.append((r2, c2, new_path))
            else:
                # Для дамки сканируем всю диагональ
                r, c = row + dr, col + dc
                found_opponent = None
                while 0 <= r < 8 and 0 <= c < 8:
                    target = self.board[r][c]
                    if target == ' ':
                        if found_opponent:
                            # Проверяем, не брали ли уже эту шашку
                            if found_opponent not in visited:
                                new_visited = visited | {found_opponent}
                                new_path = path + [found_opponent]
                                
                                # Рекурсивно ищем продолжение взятия
                                extended = self.find_captures(r, c, piece, new_visited, new_path)
                                if extended:
                                    captures.extend(extended)
                                else:
                                    captures.append((r, c, new_path))
                    elif target.lower() == player:
                        # Своя шашка - преграда
                        break
                    else:
                        if found_opponent:
                            # Уже нашли противника ранее - второй на пути
                            break
                        found_opponent = (r, c)
                    r += dr
                    c += dc
                    
        return captures

    def has_any_capture(self, player):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != ' ' and piece.lower() == player:
                    captures = self.find_captures(r, c, piece, set())
                    if captures:
                        return True
        return False

    def move_piece(self, start, end):
        sr, sc = start
        er, ec = end
        piece = self.board[sr][sc]
        self.board[sr][sc] = ' '
        self.board[er][ec] = piece

    def execute_capture(self, start, end, captures):
        self.move_piece(start, end)
        for r, c in captures:
            self.board[r][c] = ' '

    def check_winner(self):
        w_count, b_count = 0, 0
        w_moves, b_moves = False, False
        
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece == ' ': 
                    continue
                    
                if piece.lower() == 'w':
                    w_count += 1
                    if not w_moves and self.get_valid_moves(r, c):
                        w_moves = True
                else:
                    b_count += 1
                    if not b_moves and self.get_valid_moves(r, c):
                        b_moves = True
        
        if w_count == 0 or (self.current_player == 'w' and not w_moves and not self.chain_capture):
            return 'b'
        if b_count == 0 or (self.current_player == 'b' and not b_moves and not self.chain_capture):
            return 'w'
        return None

if __name__ == "__main__":
    root = tk.Tk()
    app = RussianCheckersGUI(root)
    root.mainloop()
