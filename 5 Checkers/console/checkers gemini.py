class RussianCheckers:
    def __init__(self):
        self.board = self._create_initial_board()
        self.current_player = 'w'  # 'w' for white, 'b' for black
        self.game_over = False

    def _create_initial_board(self):
        board = [['.' for _ in range(8)] for _ in range(8)]
        for r in range(3):
            for c in range(8):
                if (r + c) % 2 == 1:
                    board[r][c] = 'b'
        for r in range(5, 8):
            for c in range(8):
                if (r + c) % 2 == 1:
                    board[r][c] = 'w'
        return board

    def display_board(self):
        print("  0 1 2 3 4 5 6 7")
        for r_idx, row in enumerate(self.board):
            print(f"{r_idx} {' '.join(row)}")

    def _is_valid_move(self, start_pos, end_pos):
        sr, sc = start_pos
        er, ec = end_pos

        if not (0 <= sr < 8 and 0 <= sc < 8 and 0 <= er < 8 and 0 <= ec < 8):
            return False, "Invalid board coordinates."
        if self.board[sr][sc] == '.':
            return False, "No piece at starting position."
        if self.board[sr][sc].lower() != self.current_player:
            return False, "Not your piece."
        if self.board[er][ec] != '.':
            return False, "Target square is not empty."
        if (sr + sc) % 2 == 0 or (er + ec) % 2 == 0:
            return False, "Moves are only allowed on black squares."

        piece = self.board[sr][sc]
        dr = er - sr
        dc = ec - sc

        if piece == 'w':
            if dr >= 0: # White moves forward (down in array indices)
                return False, "White pieces can only move forward."
            if abs(dr) == 1 and abs(dc) == 1: # Regular move
                return True, ""
            return False, "Invalid move for regular checker."
        elif piece == 'b':
            if dr <= 0: # Black moves forward (up in array indices)
                return False, "Black pieces can only move forward."
            if abs(dr) == 1 and abs(dc) == 1: # Regular move
                return True, ""
            return False, "Invalid move for regular checker."
        elif piece == 'W' or piece == 'B': # King (Damka)
            if abs(dr) == abs(dc) and abs(dr) > 0:
                # Check if path is clear for king move
                step_r = 1 if dr > 0 else -1
                step_c = 1 if dc > 0 else -1
                for i in range(1, abs(dr)):
                    if self.board[sr + i * step_r][sc + i * step_c] != '.':
                        return False, "Path blocked for king."
                return True, ""
            return False, "Invalid move for king."
        return False, "Unknown piece type."

    def _is_valid_capture(self, start_pos, end_pos):
        sr, sc = start_pos
        er, ec = end_pos

        if not (0 <= sr < 8 and 0 <= sc < 8 and 0 <= er < 8 and 0 <= ec < 8):
            return False, "Invalid board coordinates for capture."
        if self.board[sr][sc] == '.':
            return False, "No piece at starting position for capture."
        if self.board[sr][sc].lower() != self.current_player:
            return False, "Not your piece for capture."
        if self.board[er][ec] != '.':
            return False, "Target square for capture is not empty."
        if (sr + sc) % 2 == 0 or (er + ec) % 2 == 0:
            return False, "Captures are only allowed on black squares."

        piece = self.board[sr][sc]
        dr = er - sr
        dc = ec - sc

        if abs(dr) != 2 or abs(dc) != 2: # Must jump exactly 2 squares diagonally
            return False, "Capture must be a 2-square diagonal jump."

        # Position of the jumped piece
        jr, jc = sr + dr // 2, sc + dc // 2

        jumped_piece = self.board[jr][jc]
        if jumped_piece == '.':
            return False, "No piece to capture."
        
        # Check if the jumped piece is an opponent's piece
        if piece.lower() == 'w' and jumped_piece.lower() != 'b':
            return False, "Can only capture opponent's pieces."
        if piece.lower() == 'b' and jumped_piece.lower() != 'w':
            return False, "Can only capture opponent's pieces."

        return True, ""

    def _get_possible_moves_for_piece(self, r, c):
        moves = []
        piece = self.board[r][c]
        
        directions = []
        if piece == 'w':
            directions = [(-1, -1), (-1, 1)] # White moves up
        elif piece == 'b':
            directions = [(1, -1), (1, 1)] # Black moves down
        elif piece == 'W' or piece == 'B': # King (Damka)
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] # All 4 diagonal directions

        for dr, dc in directions:
            # Check regular moves
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8 and self.board[nr][nc] == '.':
                if piece.isupper(): # Kings can move any length
                    # For kings, we need to check all empty squares along the diagonal
                    temp_r, temp_c = r + dr, c + dc
                    while 0 <= temp_r < 8 and 0 <= temp_c < 8 and self.board[temp_r][temp_c] == '.':
                        moves.append(((r, c), (temp_r, temp_c)))
                        temp_r += dr
                        temp_c += dc
                else:
                    moves.append(((r, c), (nr, nc)))

        return moves

    def _get_possible_captures_for_piece(self, r, c):
        captures = []
        piece = self.board[r][c]
        
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] # All 4 diagonal directions for captures

        for dr, dc in directions:
            jr, jc = r + dr, c + dc # Jumped piece position
            er, ec = r + 2 * dr, c + 2 * dc # End position after capture

            if not (0 <= er < 8 and 0 <= ec < 8):
                continue
            if self.board[er][ec] != '.': # Target square must be empty
                continue
            if self.board[jr][jc] == '.': # Must be a piece to jump over
                continue

            # Check if the jumped piece is an opponent's piece
            is_opponent = False
            if piece.lower() == 'w' and self.board[jr][jc].lower() == 'b':
                is_opponent = True
            elif piece.lower() == 'b' and self.board[jr][jc].lower() == 'w':
                is_opponent = True

            if is_opponent:
                if piece.isupper(): # King (Damka) captures
                    # For kings, can jump multiple pieces if there are empty squares in between and after each
                    temp_r, temp_c = r + dr, c + dc
                    capture_path = []
                    while 0 <= temp_r < 8 and 0 <= temp_c < 8:
                        if self.board[temp_r][temp_c] == '.':
                            # Can stop at any empty square after a capture
                            # This is a simplification; actual rules for multi-jump kings are complex.
                            # Here, we only check for a single jump for simplicity.
                            if len(capture_path) > 0: # If we've already captured a piece, this is a valid endpoint
                                captures.append(((r, c), (temp_r, temp_c), capture_path[0]))
                                # A more robust solution would involve recursion for multi-captures
                                break
                            else: # If no capture yet, this is just empty space, not a capture
                                temp_r += dr
                                temp_c += dc
                                continue
                        elif self.board[temp_r][temp_c].lower() == piece.lower(): # Own piece
                            break
                        else: # Opponent's piece
                            if len(capture_path) > 0: # Cannot jump over two pieces in a row without empty space
                                break
                            capture_path.append((temp_r, temp_c))
                            # After capturing, can stop at any subsequent empty square
                            temp_r_after_jump = temp_r + dr
                            temp_c_after_jump = temp_c + dc
                            while 0 <= temp_r_after_jump < 8 and 0 <= temp_c_after_jump < 8 and self.board[temp_r_after_jump][temp_c_after_jump] == '.':
                                captures.append(((r, c), (temp_r_after_jump, temp_c_after_jump), capture_path[0]))
                                temp_r_after_jump += dr
                                temp_c_after_jump += dc
                            break # Once a piece is encountered, either captured or own, stop this path
                else: # Regular checker captures
                    captures.append(((r, c), (er, ec), (jr, jc)))
        return captures

    def get_all_possible_captures(self):
        all_captures = []
        for r in range(8):
            for c in range(8):
                if self.board[r][c].lower() == self.current_player:
                    all_captures.extend(self._get_possible_captures_for_piece(r, c))
        return all_captures

    def make_move(self, start_pos, end_pos):
        sr, sc = start_pos
        er, ec = end_pos
        
        piece = self.board[sr][sc]
        dr = er - sr
        dc = ec - sc

        if abs(dr) == 2 and abs(dc) == 2: # This is a capture
            jr, jc = sr + dr // 2, sc + dc // 2 # Position of captured piece
            self.board[er][ec] = piece
            self.board[sr][sc] = '.'
            self.board[jr][jc] = '.' # Remove captured piece
            
            # Check for sequential captures
            if piece.islower(): # Regular checker
                if (piece == 'w' and er == 0) or (piece == 'b' and er == 7): # Promote to king
                    self.board[er][ec] = piece.upper()
                else: # Check for further captures for this piece
                    if self._get_possible_captures_for_piece(er, ec):
                        return True, "capture_again" # Signal for another turn
            else: # King (Damka)
                # After a king capture, check for more captures.
                # Simplification: A king can change direction to capture.
                # For this CLI, we will allow sequential captures if available in any direction from new position.
                if self._get_possible_captures_for_piece(er, ec):
                    return True, "capture_again" # Signal for another turn
            
            return True, "capture"
        elif abs(dr) == 1 and abs(dc) == 1: # Regular move
            self.board[er][ec] = piece
            self.board[sr][sc] = '.'
            if (piece == 'w' and er == 0) or (piece == 'b' and er == 7):
                self.board[er][ec] = piece.upper() # Promote to king
            return True, "normal"
        elif piece.isupper() and abs(dr) == abs(dc) and abs(dr) > 0: # King move
            self.board[er][ec] = piece
            self.board[sr][sc] = '.'
            return True, "normal"
        return False, "invalid"

    def check_for_win(self):
        white_pieces = 0
        black_pieces = 0
        for r in range(8):
            for c in range(8):
                if self.board[r][c].lower() == 'w':
                    white_pieces += 1
                elif self.board[r][c].lower() == 'b':
                    black_pieces += 1
        
        if white_pieces == 0:
            self.game_over = True
            return "Black wins!"
        if black_pieces == 0:
            self.game_over = True
            return "White wins!"
        
        # Check for stalemate/no legal moves
        all_possible_moves = []
        for r in range(8):
            for c in range(8):
                if self.board[r][c].lower() == self.current_player:
                    all_possible_moves.extend(self._get_possible_captures_for_piece(r, c))
                    if not all_possible_moves: # If no captures, check for regular moves
                        all_possible_moves.extend(self._get_possible_moves_for_piece(r, c))
        
        if not all_possible_moves:
            self.game_over = True
            return f"No legal moves for {self.current_player_name()}. Stalemate! {self.opposite_player_name()} wins!"
        
        return None

    def _get_player_input(self, prompt):
        while True:
            try:
                s = input(prompt)
                parts = s.split(',')
                if len(parts) != 2:
                    raise ValueError
                row, col = int(parts[0].strip()), int(parts[1].strip())
                return row, col
            except ValueError:
                print("Invalid input. Please enter coordinates as 'row,col' (e.g., 5,2).")

    def current_player_name(self):
        return "White" if self.current_player == 'w' else "Black"

    def opposite_player_name(self):
        return "Black" if self.current_player == 'w' else "White"

    def play_game(self):
        print("Russian Checkers Game")
        print("White ('w') starts. 'W'/'B' are kings (damka).")
        
        while not self.game_over:
            self.display_board()
            print(f"\n{self.current_player_name()}'s turn ({self.current_player}).")

            possible_captures = self.get_all_possible_captures()
            must_capture = bool(possible_captures)

            move_made = False
            while not move_made:
                start_pos = self._get_player_input("Enter start position (row,col): ")
                end_pos = self._get_player_input("Enter end position (row,col): ")

                is_capture_attempt = abs(start_pos[0] - end_pos[0]) == 2 and abs(start_pos[1] - end_pos[1]) == 2
                is_king_long_capture_attempt = self.board[start_pos[0]][start_pos[1]].isupper() and \
                                              abs(start_pos[0] - end_pos[0]) > 2 and \
                                              abs(start_pos[1] - end_pos[1]) > 2

                if must_capture and not (is_capture_attempt or is_king_long_capture_attempt):
                    print("You must capture an opponent's piece if possible.")
                    continue

                if is_capture_attempt or is_king_long_capture_attempt:
                    valid_capture, capture_msg = self._is_valid_capture(start_pos, end_pos)
                    if valid_capture:
                        success, move_type = self.make_move(start_pos, end_pos)
                        if success:
                            if move_type == "capture_again":
                                print("You made a capture. Check for more captures with this piece!")
                                # To implement sequential captures properly, we'd need to loop on the same piece
                                # This simple CLI version only allows one capture per input for now.
                                # A more advanced implementation would require tracking the current piece
                                # and forcing subsequent moves from its new position if captures are available.
                                # For this basic CLI, we'll just indicate it and switch turns.
                                move_made = True # For now, end turn after one capture
                            else:
                                move_made = True
                        else:
                            print(f"Invalid capture: {move_type}")
                    else:
                        print(f"Invalid capture attempt: {capture_msg}")
                else: # Regular move
                    valid_move, move_msg = self._is_valid_move(start_pos, end_pos)
                    if valid_move:
                        if must_capture:
                            print("You must capture a piece. Regular moves are not allowed if captures are available.")
                            continue
                        success, move_type = self.make_move(start_pos, end_pos)
                        if success:
                            move_made = True
                        else:
                            print(f"Invalid move: {move_type}")
                    else:
                        print(f"Invalid move: {move_msg}")

            win_status = self.check_for_win()
            if win_status:
                print(win_status)
                self.game_over = True
            elif move_made and move_type != "capture_again": # Only switch player if no sequential capture
                self.current_player = 'b' if self.current_player == 'w' else 'w'


def main():
    game = RussianCheckers()
    game.play_game()

if __name__ == "__main__":
    main()
