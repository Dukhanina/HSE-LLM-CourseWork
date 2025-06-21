import tkinter as tk
from tkinter import messagebox
import copy

ROWS = 8
COLS = 8
SQUARE = 60

def init_board():
    board = [[None] * COLS for _ in range(ROWS)]
    for r in range(ROWS):
        for c in range(COLS):
            if (r + c) % 2 == 1:
                if r < 3:
                    board[r][c] = 'w'
                elif r > 4:
                    board[r][c] = 'b'
                else:
                    board[r][c] = '.'
    return board

def opponent(p):
    return 'b' if p == 'w' else 'w'

def is_playable(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS and (r + c) % 2 == 1

def piece_color(p):
    return p.lower() if p and p != '.' else None

def get_capture_moves(b, r, c):
    p = b[r][c]
    col = piece_color(p)
    king = p.isupper()
    seqs = []
    def backtrack(board, cr, cc, path):
        found = False
        for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            if king:
                step = 1
                while True:
                    pr, pc = cr + dr * step, cc + dc * step
                    if not is_playable(pr, pc): break
                    if board[pr][pc] == '.':
                        step += 1
                        continue
                    if piece_color(board[pr][pc]) == opponent(col):
                        step2 = 1
                        while True:
                            lr, lc = pr + dr * step2, pc + dc * step2
                            if not is_playable(lr, lc) or board[lr][lc] != '.': break
                            nb = copy.deepcopy(board)
                            nb[pr][pc] = '.'
                            nb[cr][cc] = '.'
                            nb[lr][lc] = p
                            backtrack(nb, lr, lc, path + [(lr, lc)])
                            found = True
                            step2 += 1
                    break
            else:
                pr, pc = cr + dr, cc + dc
                lr, lc = cr + 2*dr, cc + 2*dc
                if is_playable(pr, pc) and is_playable(lr, lc) and piece_color(board[pr][pc]) == opponent(col) and board[lr][lc] == '.':
                    nb = copy.deepcopy(board)
                    nb[pr][pc] = '.'
                    nb[cr][cc] = '.'
                    nb[lr][lc] = p
                    backtrack(nb, lr, lc, path + [(lr, lc)])
                    found = True
        if not found and path:
            seqs.append([(r, c)] + path)
    backtrack(b, r, c, [])
    return seqs

def get_simple_moves(b, r, c):
    p = b[r][c]
    col = piece_color(p)
    moves = []
    for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
        if p.islower():
            if (col == 'w' and dr < 0) or (col == 'b' and dr > 0):
                continue
            nr, nc = r + dr, c + dc
            if is_playable(nr, nc) and b[nr][nc] == '.':
                moves.append([(r, c), (nr, nc)])
        else:
            step = 1
            while True:
                nr, nc = r + dr*step, c + dc*step
                if not is_playable(nr, nc) or b[nr][nc] != '.':
                    break
                moves.append([(r, c), (nr, nc)])
                step += 1
    return moves

def get_all_valid_moves(b, p):
    caps = {}
    for r in range(ROWS):
        for c in range(COLS):
            if piece_color(b[r][c]) == p:
                seqs = get_capture_moves(b, r, c)
                if seqs:
                    caps[(r, c)] = seqs
    if caps:
        return caps, True
    simples = {}
    for r in range(ROWS):
        for c in range(COLS):
            if piece_color(b[r][c]) == p:
                seqs = get_simple_moves(b, r, c)
                if seqs:
                    simples[(r, c)] = seqs
    return simples, False

def apply_move(b, path, p):
    r0, c0 = path[0]
    piece = b[r0][c0]
    b[r0][c0] = '.'
    for r1, c1 in path[1:]:
        if abs(r1 - r0) > 1:
            dr = (r1 - r0) // abs(r1 - r0)
            dc = (c1 - c0) // abs(c1 - c0)
            rr, cc = r0 + dr, c0 + dc
            while (rr, cc) != (r1, c1):
                if piece_color(b[rr][cc]) == opponent(p):
                    b[rr][cc] = '.'
                    break
                rr += dr; cc += dc
        r0, c0 = r1, c1
    if (p == 'w' and r0 == ROWS - 1) or (p == 'b' and r0 == 0):
        piece = piece.upper()
    b[r0][c0] = piece

def check_win(b, p):
    moves, _ = get_all_valid_moves(b, p)
    if any(piece_color(b[r][c]) == p for r in range(ROWS) for c in range(COLS)) and moves:
        return None
    return opponent(p)

class CheckersApp:
    def __init__(self, master):
        self.master = master
        master.title("Russian Checkers")
        self.new_button = tk.Button(master, text="Новая игра", command=self.new_game)
        self.new_button.pack()
        self.canvas = tk.Canvas(master, width=COLS*SQUARE, height=ROWS*SQUARE)
        self.canvas.pack()
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.selected_tag = None
        self.drag_data = {}
        self.new_game()

    def new_game(self):
        self.board = init_board()
        self.current = 'w'
        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        self.tag_map = {}
        for r in range(ROWS):
            for c in range(COLS):
                x1 = c * SQUARE
                y1 = r * SQUARE
                x2 = x1 + SQUARE
                y2 = y1 + SQUARE
                color = "#F0D9B5" if (r + c) % 2 == 0 else "#B58863"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                piece = self.board[r][c]
                if piece and piece != '.':
                    tag = f"p{r}_{c}"
                    fill = "white" if piece.lower() == 'w' else "black"
                    self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill=fill, tags=tag)
                    if piece.isupper():
                        self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text="K", font=("Arial", SQUARE//2), tags=tag)
                    self.tag_map[tag] = (r, c)

    def on_press(self, event):
        items = self.canvas.find_withtag("current")
        for item in items:
            for tag in self.canvas.gettags(item):
                if tag in self.tag_map:
                    r, c = self.tag_map[tag]
                    if piece_color(self.board[r][c]) == self.current:
                        self.selected_tag = tag
                        self.drag_data["items"] = self.canvas.find_withtag(tag)
                        self.drag_data["x"] = event.x
                        self.drag_data["y"] = event.y
                        self.drag_data["orig"] = {i: self.canvas.coords(i) for i in self.drag_data["items"]}
                    return

    def on_motion(self, event):
        if self.selected_tag:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            for i in self.drag_data["items"]:
                self.canvas.move(i, dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_release(self, event):
        if not self.selected_tag:
            return
        sr, sc = self.tag_map[self.selected_tag]
        dr = int(event.y // SQUARE)
        dc = int(event.x // SQUARE)
        moves, _ = get_all_valid_moves(self.board, self.current)
        path = None
        if (sr, sc) in moves:
            for seq in moves[(sr, sc)]:
                if seq[-1] == (dr, dc):
                    path = seq
                    break
        if path:
            apply_move(self.board, path, self.current)
            win = check_win(self.board, self.current)
            if not win:
                self.current = opponent(self.current)
            self.draw_board()
            if win:
                messagebox.showinfo("Игра окончена", f"{'White' if win == 'w' else 'Black'} wins")
        else:
            messagebox.showerror("Ошибка", "Недопустимый ход")
            for i, coords in self.drag_data["orig"].items():
                self.canvas.coords(i, *coords)
        self.selected_tag = None
        self.drag_data = {}

if __name__ == '__main__':
    root = tk.Tk()
    app = CheckersApp(root)
    root.mainloop()
