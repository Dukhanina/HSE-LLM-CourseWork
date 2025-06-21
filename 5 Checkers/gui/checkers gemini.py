import tkinter as tk
from tkinter import messagebox, scrolledtext

class RussianCheckers:
    def __init__(self, gui_app):
        self.gui_app = gui_app
        self.board = self._create_initial_board()
        self.current_player = 'w'  # 'w' for white, 'b' for black
        self.game_over = False
        self.forced_capture_piece = None  # (r, c) of the piece that must continue capturing if applicable

    def _create_initial_board(self):
        board = [['.' for _ in range(8)] for _ in range(8)]
        for r in range(3):
            for c in range(8):
                if (r + c) % 2 == 1:  # Black squares
                    board[r][c] = 'b'
        for r in range(5, 8):
            for c in range(8):
                if (r + c) % 2 == 1:  # Black squares
                    board[r][c] = 'w'
        return board

    def display_board(self):
        self.gui_app.update_board_display(self.board)

    def _is_valid_square(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def _get_piece_at(self, r, c):
        if self._is_valid_square(r, c):
            return self.board[r][c]
        return None

    def _is_opponent_piece(self, r, c, current_player):
        piece = self._get_piece_at(r, c)
        if piece == '.':
            return False
        return piece.lower() != current_player

    def get_all_possible_moves_for_piece(self, r, c):
        moves = []
        piece = self._get_piece_at(r, c)
        if piece == '.' or piece.lower() != self.current_player:
            return moves

        directions = []
        if piece.islower():  # Regular checker
            if self.current_player == 'w':
                directions = [(-1, -1), (-1, 1)]  # White moves up
            else:
                directions = [(1, -1), (1, 1)]  # Black moves down
        else:  # King (Damka)
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # All 4 diagonal directions

        for dr_step, dc_step in directions:
            nr, nc = r + dr_step, c + dc_step
            if piece.islower():
                if self._is_valid_square(nr, nc) and self._get_piece_at(nr, nc) == '.':
                    moves.append(((r, c), (nr, nc)))
            else: # King
                while self._is_valid_square(nr, nc) and self._get_piece_at(nr, nc) == '.':
                    moves.append(((r, c), (nr, nc)))
                    nr += dr_step
                    nc += dc_step
        return moves

    def _get_possible_captures_for_piece(self, r, c):
        captures = []
        piece = self._get_piece_at(r, c)
        if piece == '.' or piece.lower() != self.current_player:
            return captures

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr_step, dc_step in directions:
            if piece.islower():  # Regular checker captures
                jr, jc = r + dr_step, c + dc_step  # Position of potential jumped piece
                er, ec = r + 2 * dr_step, c + 2 * dc_step  # End position after jump

                if (self._is_valid_square(er, ec) and self._get_piece_at(er, ec) == '.' and
                    self._is_valid_square(jr, jc) and self._get_piece_at(jr, jc) != '.' and
                    self._get_piece_at(jr, jc).lower() != piece.lower()):
                    captures.append(((r, c), (er, ec), (jr, jc)))
            else:  # King (Damka) captures
                temp_r, temp_c = r + dr_step, c + dc_step
                captured_piece_pos = None
                
                while self._is_valid_square(temp_r, temp_c):
                    current_spot_piece = self._get_piece_at(temp_r, temp_c)
                    if current_spot_piece == '.':
                        if captured_piece_pos: # If a piece was captured, any empty square after is a valid landing spot
                            captures.append(((r, c), (temp_r, temp_c), captured_piece_pos))
                        temp_r += dr_step
                        temp_c += dc_step
                    elif current_spot_piece.lower() == piece.lower(): # Own piece blocks
                        break
                    else: # Opponent's piece
                        if captured_piece_pos: # Already captured one, cannot capture another
                            break
                        captured_piece_pos = (temp_r, temp_c) # Mark as captured
                        temp_r += dr_step
                        temp_c += dc_step
                        # Continue to find landing spot after capturing
                        while self._is_valid_square(temp_r, temp_c) and self._get_piece_at(temp_r, temp_c) == '.':
                            captures.append(((r, c), (temp_r, temp_c), captured_piece_pos))
                            temp_r += dr_step
                            temp_c += dc_step
                        break # Found landing spots for this capture, stop searching in this direction
        return captures

    def get_all_possible_captures(self):
        all_captures = []
        for r in range(8):
            for c in range(8):
                if self._get_piece_at(r, c).lower() == self.current_player:
                    all_captures.extend(self._get_possible_captures_for_piece(r, c))
        return all_captures

    def is_valid_move_attempt(self, start_pos, end_pos):
        sr, sc = start_pos
        er, ec = end_pos
        piece = self._get_piece_at(sr, sc)

        if not self._is_valid_square(sr, sc) or not self._is_valid_square(er, ec):
            return False, "Invalid board coordinates."
        if piece == '.':
            return False, "No piece at starting position."
        if piece.lower() != self.current_player:
            return False, "Not your piece."
        if self._get_piece_at(er, ec) != '.':
            return False, "Target square is not empty."
        if (sr + sc) % 2 == 0 or (er + ec) % 2 == 0:
            return False, "Moves are only allowed on black squares."

        # Check for forced capture
        possible_captures = self.get_all_possible_captures()
        must_capture = bool(possible_captures) # Define must_capture here

        if self.forced_capture_piece and start_pos != self.forced_capture_piece:
             return False, "You must continue capturing with the previously captured piece."
        elif not self.forced_capture_piece and must_capture:
            # If there are captures available but no forced capture piece yet, check if this move is a valid capture
            move_is_a_capture = False
            for capture_start, capture_end, _ in possible_captures:
                if capture_start == start_pos and capture_end == end_pos:
                    move_is_a_capture = True
                    break
            if not move_is_a_capture:
                return False, "You must make a capture if available."

        # Validate the specific move type (normal move vs. capture)
        dr = er - sr
        dc = ec - sc

        # Check if it's a capture move
        is_capture_attempt = False
        if abs(dr) == abs(dc) and abs(dr) > 1: # Could be a capture
            if piece.islower(): # Regular checker capture
                if abs(dr) == 2:
                    jr, jc = sr + dr // 2, sc + dc // 2
                    if self._is_opponent_piece(jr, jc, self.current_player):
                        is_capture_attempt = True
            else: # King capture
                step_r = 1 if dr > 0 else -1
                step_c = 1 if dc > 0 else -1
                temp_r, temp_c = sr + step_r, sc + step_c
                captured_count = 0
                while temp_r != er:
                    if self._is_opponent_piece(temp_r, temp_c, self.current_player):
                        captured_count += 1
                    if captured_count > 1: # Kings can only capture one piece per jump
                        return False, "King cannot jump over more than one piece."
                    temp_r += step_r
                    temp_c += step_c
                if captured_count == 1:
                    is_capture_attempt = True
        
        if is_capture_attempt:
            # The capture path is validated within _get_possible_captures_for_piece
            # We just need to check if this specific capture is in the list of valid captures
            valid_captures_for_piece = self._get_possible_captures_for_piece(sr, sc)
            for s, e, j in valid_captures_for_piece:
                if s == start_pos and e == end_pos:
                    return True, "capture"
            return False, "Invalid capture path."
        else: # Regular move
            if must_capture: # If captures are available, normal moves are disallowed
                return False, "You must make a capture if available."
            # Validate regular move rules
            if piece.islower():
                if abs(dr) != 1 or abs(dc) != 1:
                    return False, "Regular checkers move one diagonal step."
                if (self.current_player == 'w' and dr >= 0) or \
                   (self.current_player == 'b' and dr <= 0):
                    return False, f"{self.current_player_name()} pieces can only move forward."
            else: # King normal move
                if abs(dr) != abs(dc) or abs(dr) == 0:
                    return False, "King must move along a diagonal."
                step_r = 1 if dr > 0 else -1
                step_c = 1 if dc > 0 else -1
                r_check, c_check = sr + step_r, sc + step_c
                while r_check != er:
                    if self._get_piece_at(r_check, c_check) != '.':
                        return False, "Path blocked for king."
                    r_check += step_r
                    c_check += dc_step # Corrected: should be dc_step here
            return True, "normal"

    def execute_move(self, start_pos, end_pos):
        sr, sc = start_pos
        er, ec = end_pos
        
        piece = self._get_piece_at(sr, sc)
        dr = er - sr
        dc = ec - sc

        move_success_type = "normal" # Default

        # Determine if it's a capture move
        is_capture = False
        if abs(dr) == abs(dc) and abs(dr) > 1:
            if piece.islower(): # Regular checker capture
                if abs(dr) == 2:
                    jr, jc = sr + dr // 2, sc + dc // 2
                    if self._is_opponent_piece(jr, jc, self.current_player):
                        is_capture = True
                        self.board[jr][jc] = '.' # Remove captured piece
            else: # King capture
                step_r = 1 if dr > 0 else -1
                step_c = 1 if dc > 0 else -1
                temp_r, temp_c = sr + step_r, sc + step_c
                captured_piece_pos = None
                while temp_r != er:
                    if self._is_opponent_piece(temp_r, temp_c, self.current_player):
                        captured_piece_pos = (temp_r, temp_c)
                        break
                    temp_r += step_r
                    temp_c += step_c
                if captured_piece_pos:
                    is_capture = True
                    self.board[captured_piece_pos[0]][captured_piece_pos[1]] = '.' # Remove captured piece

        self.board[er][ec] = piece
        self.board[sr][sc] = '.'

        if is_capture:
            # Check for promotion after capture
            if piece.islower() and ((piece == 'w' and er == 0) or (piece == 'b' and er == 7)):
                self.board[er][ec] = piece.upper()
                self.forced_capture_piece = None
                move_success_type = "promoted"
            else:
                # Check for sequential captures
                if self._get_possible_captures_for_piece(er, ec):
                    self.forced_capture_piece = (er, ec)
                    move_success_type = "capture_again"
                else:
                    self.forced_capture_piece = None
                    move_success_type = "capture"
        else: # Normal move
            # Check for promotion after normal move
            if piece.islower() and ((piece == 'w' and er == 0) or (piece == 'b' and er == 7)):
                self.board[er][ec] = piece.upper()
            self.forced_capture_piece = None
            move_success_type = "normal"
            
        return True, move_success_type

    def check_for_win(self):
        white_pieces = sum(1 for r in range(8) for c in range(8) if self._get_piece_at(r, c).lower() == 'w')
        black_pieces = sum(1 for r in range(8) for c in range(8) if self._get_piece_at(r, c).lower() == 'b')
        
        if white_pieces == 0:
            self.game_over = True
            return "Black wins!"
        if black_pieces == 0:
            self.game_over = True
            return "White wins!"
        
        # Check for stalemate (no legal moves for current player)
        all_possible_moves = self.get_all_possible_captures()
        if not all_possible_moves:
            for r in range(8):
                for c in range(8):
                    if self._get_piece_at(r, c).lower() == self.current_player:
                        # Iterate through all possible normal moves for this piece
                        for move_start, move_end in self.get_all_possible_moves_for_piece(r, c):
                            # Temporarily set forced_capture_piece to None to check normal moves
                            # as is_valid_move_attempt relies on it to determine if normal moves are allowed
                            original_forced_capture_piece = self.forced_capture_piece
                            self.forced_capture_piece = None
                            is_valid, _ = self.is_valid_move_attempt(move_start, move_end)
                            self.forced_capture_piece = original_forced_capture_piece # Restore
                            if is_valid:
                                return None # Has moves, not a stalemate
            self.game_over = True
            return f"No legal moves for {self.current_player_name()}. Stalemate! {self.opposite_player_name()} wins!"
        
        return None

    def current_player_name(self):
        return "White" if self.current_player == 'w' else "Black"

    def opposite_player_name(self):
        return "Black" if self.current_player == 'w' else "White"

class CheckersGUI:
    def __init__(self, master):
        self.master = master
        master.title("Russian Checkers")

        self.game = None
        self.selected_piece = None # (r, c) of the currently selected piece
        
        # Widgets
        self.log_text = scrolledtext.ScrolledText(master, state='disabled', width=60, height=10)
        self.log_text.grid(row=0, column=0, columnspan=8, padx=5, pady=5)

        self.board_frame = tk.Frame(master, borderwidth=2, relief="groove")
        self.board_frame.grid(row=1, column=0, columnspan=8, padx=5, pady=5)
        self.board_buttons = {} # {(row, col): button_widget}

        self.create_board_buttons()

        self.current_player_label = tk.Label(master, text="Current Player: ")
        self.current_player_label.grid(row=9, column=0, columnspan=8)

        self.message_label = tk.Label(master, text="", fg="red")
        self.message_label.grid(row=10, column=0, columnspan=8)

        self.new_game_button = tk.Button(master, text="New Game", command=self.start_new_game)
        self.new_game_button.grid(row=11, column=0, columnspan=8, pady=5)

        self.start_new_game() # Start game immediately on launch

    def create_board_buttons(self):
        # Column labels (0-7)
        for c in range(8):
            tk.Label(self.board_frame, text=str(c), width=4).grid(row=0, column=c + 1)
        # Row labels (0-7) and buttons
        for r in range(8):
            tk.Label(self.board_frame, text=str(r), width=2).grid(row=r + 1, column=0)
            for c in range(8):
                # Ensure the lambda captures the current values of r and c
                button = tk.Button(self.board_frame, text="", width=4, height=2,
                                   bg="darkgray" if (r + c) % 2 == 1 else "lightgray",
                                   command=lambda row=r, col=c: self.on_square_click(row, col))
                button.grid(row=r + 1, column=c + 1, padx=0, pady=0) # Remove padding for tighter grid
                self.board_buttons[(r, c)] = button

    def update_board_display(self, board):
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                button = self.board_buttons[(r, c)]
                
                # Reset background color first
                bg_color = "darkgray" if (r + c) % 2 == 1 else "lightgray"
                button.config(bg=bg_color, relief=tk.RAISED, borderwidth=2)

                # Set piece text and color
                if piece == 'w':
                    button.config(text="o", fg="white", font=("Arial", 12, "bold"))
                elif piece == 'b':
                    button.config(text="o", fg="black", font=("Arial", 12, "bold"))
                elif piece == 'W':
                    button.config(text="♕", fg="white", font=("Arial", 12, "bold"))
                elif piece == 'B':
                    button.config(text="♛", fg="black", font=("Arial", 12, "bold"))
                else:
                    button.config(text="", fg="white") # Empty square, no text

        # Highlight selected piece if any
        if self.selected_piece:
            r, c = self.selected_piece
            self.board_buttons[(r, c)].config(relief=tk.SUNKEN, borderwidth=2, bg="lightblue")

    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def show_error(self, message):
        messagebox.showerror("Invalid Move", message)
        self.message_label.config(text=message)
        self.master.after(3000, lambda: self.message_label.config(text="")) # Clear message after 3 seconds

    def disable_player_input(self):
        for button in self.board_buttons.values():
            button.config(state=tk.DISABLED)

    def enable_player_input(self):
        for button in self.board_buttons.values():
            button.config(state=tk.NORMAL)

    def start_new_game(self):
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        self.log_message("Starting a new game...")
        self.game = RussianCheckers(self)
        self.selected_piece = None
        self.new_game_button.config(state=tk.DISABLED)
        self.enable_player_input()
        self.game.display_board()
        self.current_player_label.config(text=f"Current Player: {self.game.current_player_name()}")
        self.log_message("White ('o') starts. '♕'/'♛' are kings (damka).")

    def on_square_click(self, r, c):
        if self.game.game_over:
            return

        # If a piece is already selected, this click is for the end position
        if self.selected_piece:
            start_pos = self.selected_piece
            end_pos = (r, c)
            self.process_move(start_pos, end_pos)
        else: # No piece selected, this click is for the start position
            piece_at_click = self.game._get_piece_at(r,c)
            if piece_at_click == '.' or piece_at_click.lower() != self.game.current_player:
                self.show_error("Please select one of your pieces.")
            elif self.game.forced_capture_piece and self.game.forced_capture_piece != (r,c):
                self.show_error(f"You must continue capturing with the piece at {self.game.forced_capture_piece[0]},{self.game.forced_capture_piece[1]}.")
            else:
                self.selected_piece = (r, c)
                self.game.display_board() # Redraw to highlight selected piece

    def process_move(self, start_pos, end_pos):
        self.message_label.config(text="") # Clear previous error message

        valid_move_result, msg = self.game.is_valid_move_attempt(start_pos, end_pos)

        if valid_move_result:
            success, move_type = self.game.execute_move(start_pos, end_pos)
            if success:
                self.log_message(f"{self.game.current_player_name()} moved from {start_pos} to {end_pos}.")
                self.game.display_board()
                win_status = self.game.check_for_win()
                if win_status:
                    self.log_message(win_status)
                    self.game.game_over = True
                    self.disable_player_input()
                    self.new_game_button.config(state=tk.NORMAL)
                else:
                    if move_type != "capture_again":
                        self.game.current_player = 'b' if self.game.current_player == 'w' else 'w'
                        self.game.forced_capture_piece = None 
                    else:
                        self.log_message(f"{self.game.current_player_name()} must make another capture!")
                    self.current_player_label.config(text=f"Current Player: {self.game.current_player_name()}")
            else:
                self.show_error(f"Move execution failed: {move_type}")
        else:
            self.show_error(f"Invalid move: {msg}")
        
        self.selected_piece = None
        self.game.display_board() # Ensure board is updated after move attempt and selection reset

def main():
    root = tk.Tk()
    gui = CheckersGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
