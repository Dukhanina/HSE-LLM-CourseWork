import sys

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

    def print_board(self):
        print("  0 1 2 3 4 5 6 7")
        for i, row in enumerate(self.board):
            print(f"{i} {' '.join(cell if cell != ' ' else '.' for cell in row)}")

    def get_valid_moves(self, row, col):
        piece = self.board[row][col]
        if piece == ' ': return []
        moves = []
        player = piece.lower()
        is_king = piece.isupper()
        directions = []
        
        if piece in ['w', 'W'] or is_king:
            directions.extend([(1, 1), (1, -1)])
        if piece in ['b', 'B'] or is_king:
            directions.extend([(-1, 1), (-1, -1)])
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == ' ':
                moves.append((r, c, []))
        
        captures = self.find_captures(row, col, piece, set())
        return captures if captures else moves

    def find_captures(self, row, col, piece, visited, path=None):
        if path is None:
            path = []
        captures = []
        player = piece.lower()
        is_king = piece.isupper()
        directions = [(-1,-1), (-1,1), (1,-1), (1,1)] if is_king else []
        
        if piece in ['w', 'W']:
            directions.extend([(1,-1), (1,1)])
        if piece in ['b', 'B']:
            directions.extend([(-1,-1), (-1,1)])
        
        for dr, dc in directions:
            found = False
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8 and not found:
                target = self.board[r][c]
                if target == ' ':
                    r += dr
                    c += dc
                    continue
                if target.lower() == player:
                    break
                opp = (r, c)
                r += dr
                c += dc
                while 0 <= r < 8 and 0 <= c < 8:
                    if self.board[r][c] == ' ':
                        if (r, c) not in visited:
                            new_visited = visited | {opp}
                            new_path = path + [opp]
                            extended = self.find_captures(r, c, piece, new_visited, new_path)
                            if extended:
                                captures.extend(extended)
                            captures.append((r, c, new_path))
                        found = True
                        break
                    else:
                        break
                r += dr
                c += dc
        return captures

    def has_any_capture(self, player):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != ' ' and piece.lower() == player:
                    if self.find_captures(r, c, piece, set()):
                        return True
        return False

    def move_piece(self, start, end):
        sr, sc = start
        er, ec = end
        piece = self.board[sr][sc]
        self.board[sr][sc] = ' '
        self.board[er][ec] = piece
        
        if (piece == 'w' and er == 0) or (piece == 'b' and er == 7):
            self.board[er][ec] = piece.upper()

    def execute_capture(self, start, end, captures):
        self.move_piece(start, end)
        for r, c in captures:
            self.board[r][c] = ' '

    def play(self):
        while not self.game_over:
            self.print_board()
            player_name = "Белые (w)" if self.current_player == 'w' else "Черные (b)"
            print(f"Ход: {player_name}")
            
            if self.chain_capture:
                print(f"Продолжение взятия для фигуры на {self.chain_piece}")
                start = self.chain_piece
            else:
                try:
                    coords = input("Введите начальную позицию (ряд столбец): ").split()
                    if not coords:
                        continue
                    sr, sc = map(int, coords[:2])
                    if not (0 <= sr < 8 and 0 <= sc < 8) or self.board[sr][sc].lower() != self.current_player:
                        print("Неверная позиция")
                        continue
                    start = (sr, sc)
                except:
                    print("Ошибка ввода")
                    continue
            
            piece = self.board[start[0]][start[1]]
            moves = self.get_valid_moves(*start)
            must_capture = self.has_any_capture(self.current_player)
            
            if must_capture and not any(m[2] for m in moves):
                print("Обязательное взятие!")
                moves = []
            
            if not moves:
                print("Нет доступных ходов")
                if self.chain_capture:
                    self.chain_capture = False
                    self.current_player = 'b' if self.current_player == 'w' else 'w'
                continue
            
            try:
                coords = input("Введите конечную позицию (ряд столбец): ").split()
                if not coords:
                    continue
                er, ec = map(int, coords[:2])
                end = (er, ec)
                move = next((m for m in moves if m[0] == er and m[1] == ec), None)
                if not move:
                    print("Недопустимый ход")
                    continue
            except:
                print("Ошибка ввода")
                continue
            
            captures = move[2]
            if captures:
                self.execute_capture(start, end, captures)
                self.chain_piece = end
                if self.find_captures(*end, piece, set()):
                    self.chain_capture = True
                else:
                    self.chain_capture = False
                    self.current_player = 'b' if self.current_player == 'w' else 'w'
            else:
                if must_capture:
                    print("Пропущено обязательное взятие!")
                    continue
                self.move_piece(start, end)
                self.chain_capture = False
                self.current_player = 'b' if self.current_player == 'w' else 'w'
            
            if self.check_winner():
                self.print_board()
                print(f"Победили {player_name}!")
                self.game_over = True

    def check_winner(self):
        w_count, b_count = 0, 0
        w_moves, b_moves = False, False
        
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece == ' ': continue
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
    game = RussianCheckers()
    game.play()
