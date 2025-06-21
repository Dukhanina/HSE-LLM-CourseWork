import tkinter as tk
from tkinter import messagebox, simpledialog
import random

TILE_TYPES = [
    {'name':'road_straight','edges':{'N':'road','E':'field','S':'road','W':'field'},'monastery':False,'shields':0},
    {'name':'road_curve','edges':{'N':'road','E':'road','S':'field','W':'field'},'monastery':False,'shields':0},
    {'name':'city_1','edges':{'N':'city','E':'field','S':'field','W':'field'},'monastery':False,'shields':1},
    {'name':'monastery','edges':{'N':'field','E':'field','S':'field','W':'field'},'monastery':True,'shields':0}
]

def rotate(tile, r):
    dirs = ['N','E','S','W']
    e = tile['edges']
    ne = {}
    for i, d in enumerate(dirs):
        ne[d] = e[dirs[(i - r) % 4]]
    return {'name':tile['name'], 'edges':ne, 'monastery':tile['monastery'], 'shields':tile['shields']}

def init_deck():
    deck = []
    for t in TILE_TYPES:
        deck += [t.copy() for _ in range(10)]
    random.shuffle(deck)
    return deck

def valid_placement(board, x, y, t):
    if (x, y) in board:
        return False
    dirs = {'N':(0,1), 'E':(1,0), 'S':(0,-1), 'W':(-1,0)}
    has_neighbor = False
    for d, (dx,dy) in dirs.items():
        nx, ny = x + dx, y + dy
        if (nx, ny) in board:
            has_neighbor = True
            opposite = {'N':'S','S':'N','E':'W','W':'E'}
            ne = board[(nx,ny)]['edges'][opposite[d]]
            if ne != t['edges'][d]:
                return False
    return has_neighbor

def get_road_cluster(board, start):
    dirs = {'N':(0,1), 'E':(1,0), 'S':(0,-1), 'W':(-1,0)}
    seen = {start}
    stack = [start]
    while stack:
        x, y = stack.pop()
        t = board[(x,y)]
        for d, (dx,dy) in dirs.items():
            if t['edges'][d] == 'road':
                nx, ny = x+dx, y+dy
                if (nx,ny) in board:
                    ot = board[(nx,ny)]['edges'][{'N':'S','S':'N','E':'W','W':'E'}[d]]
                    if ot == 'road' and (nx,ny) not in seen:
                        seen.add((nx,ny))
                        stack.append((nx,ny))
    return seen

def road_complete(board, cluster):
    dirs = {'N':(0,1), 'E':(1,0), 'S':(0,-1), 'W':(-1,0)}
    for x, y in cluster:
        t = board[(x,y)]
        for d, (dx,dy) in dirs.items():
            if t['edges'][d] == 'road':
                nx, ny = x+dx, y+dy
                if (nx,ny) not in cluster and (nx,ny) not in board:
                    return False
    return True

def check_monastery(board, x, y):
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            if dx==0 and dy==0:
                continue
            if (x+dx, y+dy) not in board:
                return False
    return True

def score_features(board, meeples, scores):
    for m in meeples[:]:
        x, y = m['pos']
        if m['feature'] == 'road':
            cluster = get_road_cluster(board, (x,y))
            if road_complete(board, cluster):
                scores[m['player']] += len(cluster)
                meeples.remove(m)
        if m['feature'] == 'monastery':
            if check_monastery(board, x, y):
                scores[m['player']] += 9
                meeples.remove(m)

def final_scoring(board, meeples, scores):
    for m in meeples:
        x, y = m['pos']
        if m['feature'] == 'road':
            cluster = get_road_cluster(board, (x,y))
            scores[m['player']] += len(cluster) // 2
        if m['feature'] == 'monastery':
            cnt = 1
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    if dx==0 and dy==0:
                        continue
                    if (x+dx, y+dy) in board:
                        cnt += 1
            scores[m['player']] += cnt

class CarcassonneApp:
    def __init__(self, master):
        self.master = master
        master.title("Carcassonne")
        self.new_button = tk.Button(master, text="Новая игра", command=self.new_game)
        self.new_button.pack(pady=5)
        self.log = tk.Text(master, height=20, state=tk.DISABLED)
        self.log.pack(pady=5)
        self.entry = tk.Entry(master)
        self.entry.pack(pady=5)
        self.entry.bind('<Return>', self.on_input)
        self.move_button = tk.Button(master, text="Далее", command=self.on_input)
        self.move_button.pack(pady=5)
        self.state = 'draw'
        self.new_game()

    def new_game(self):
        self.players = 2
        self.deck = init_deck()
        self.board = {(0,0): TILE_TYPES[2].copy()}
        self.meeples = []
        self.scores = [0] * self.players
        self.current = 0
        self.current_tile = None
        self.log.config(state=tk.NORMAL)
        self.log.delete('1.0', tk.END)
        self.log.insert(tk.END, "Новая игра\n")
        self.display_board()
        self.state = 'draw'
        self.log.insert(tk.END, f"Игрок {self.current+1}: нажмите Далее для взятия тайла\n")
        self.log.config(state=tk.DISABLED)
        self.entry.delete(0, tk.END)
        self.entry.focus()

    def display_board(self):
        self.log.insert(tk.END, "Позиции тайлов:\n")
        for (x,y),tile in sorted(self.board.items()):
            self.log.insert(tk.END, f" ({x},{y}): {tile['name']} edges={tile['edges']}\n")
        self.log.insert(tk.END, "\n")

    def on_input(self, event=None):
        inp = self.entry.get().strip()
        if self.state == 'draw':
            if inp:
                messagebox.showerror("Ошибка", "Нажмите Далее без ввода")
                return
            if not self.deck:
                final_scoring(self.board, self.meeples, self.scores)
                winner = max(range(self.players), key=lambda i:self.scores[i])
                self.log.config(state=tk.NORMAL)
                self.log.insert(tk.END, f"Игра окончена. Счета: {self.scores}\n")
                self.log.insert(tk.END, f"Победил игрок {winner+1}\n")
                self.entry.config(state=tk.DISABLED)
                self.move_button.config(state=tk.DISABLED)
                self.log.config(state=tk.DISABLED)
                return
            self.current_tile = self.deck.pop()
            self.log.config(state=tk.NORMAL)
            self.log.insert(tk.END, f"Игрок {self.current+1} берет тайл {self.current_tile['name']} edges={self.current_tile['edges']}\n")
            self.log.insert(tk.END, "Введите x y rot (например: 1 0 2)\n")
            self.log.config(state=tk.DISABLED)
            self.state = 'place'
            self.entry.delete(0, tk.END)
            return
        if self.state == 'place':
            parts = inp.split()
            if len(parts) != 3:
                messagebox.showerror("Ошибка","Введите x y rot")
                return
            try:
                x = int(parts[0]); y = int(parts[1]); rot = int(parts[2])
            except ValueError:
                messagebox.showerror("Ошибка","Координаты и поворот - числа")
                return
            if rot < 0 or rot > 3:
                messagebox.showerror("Ошибка","Ротация 0-3")
                return
            t = rotate(self.current_tile, rot)
            if not valid_placement(self.board, x, y, t):
                messagebox.showerror("Ошибка","Нельзя разместить здесь")
                return
            self.board[(x,y)] = t
            self.log.config(state=tk.NORMAL)
            self.log.insert(tk.END, f"Размещен тайл на ({x},{y})\n")
            place = messagebox.askyesno("Мипл", "Установить мипла?")
            if place:
                feat = simpledialog.askstring("Мипл","Укажите фичу N/E/S/W/C:").upper()
                if feat in t['edges'] and ((feat!='C') or t['monastery']):
                    self.meeples.append({'pos':(x,y),'feature': feat if feat!='C' else 'monastery','player':self.current})
            score_features(self.board, self.meeples, self.scores)
            self.log.insert(tk.END, f"Счета: {self.scores}\n\n")
            self.state = 'draw'
            self.current = (self.current+1) % self.players
            self.display_board()
            self.log.insert(tk.END, f"Игрок {self.current+1}: нажмите Далее\n")
            self.log.config(state=tk.DISABLED)
            self.entry.delete(0, tk.END)

if __name__ == '__main__':
    root = tk.Tk()
    app = CarcassonneApp(root)
    root.mainloop()
