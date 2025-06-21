import random
import tkinter as tk
from tkinter import messagebox

class UnionFind:
    def __init__(self):
        self.parent = {}
    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    def union(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x != root_y:
            self.parent[root_x] = root_y

class Board:
    def __init__(self):
        self.grid = {(0, 0): START_TILE}
        self.uf = UnionFind()
        self.feature_tiles = {}
        self.next_id = 0
    def place_tile(self, x, y, tile, rotation):
        if (x, y) in self.grid:
            return False
        adj_dirs = {'north': (0, -1, 'south'), 'south': (0, 1, 'north'), 'east': (1, 0, 'west'), 'west': (-1, 0, 'east')}
        for dir, (dx, dy, opp_dir) in adj_dirs.items():
            ax, ay = x + dx, y + dy
            if (ax, ay) in self.grid:
                adj_tile = self.grid[(ax, ay)]
                if tile[dir] and adj_tile[opp_dir] and tile[dir] != adj_tile[opp_dir]:
                    return False
        self.grid[(x, y)] = tile
        for dir in ['north', 'south', 'east', 'west', 'center']:
            feature_type = tile[dir]
            if feature_type:
                new_id = self.next_id
                self.next_id += 1
                self.uf.parent[new_id] = new_id
                self.feature_tiles[new_id] = [(x, y, dir)]
                if dir != 'center':
                    dx, dy, opp_dir = adj_dirs[dir]
                    ax, ay = x + dx, y + dy
                    if (ax, ay) in self.grid:
                        adj_tile = self.grid[(ax, ay)]
                        if adj_tile[opp_dir] == feature_type:
                            for fid, tiles in self.feature_tiles.items():
                                if (ax, ay, opp_dir) in tiles:
                                    adj_id = self.uf.find(fid)
                                    self.uf.union(new_id, adj_id)
                                    root_id = self.uf.find(new_id)
                                    if root_id != new_id:
                                        self.feature_tiles[root_id] = self.feature_tiles.get(root_id, []) + self.feature_tiles.pop(new_id, [])
                                    break
        return True

class Player:
    def __init__(self, id):
        self.id = id
        self.score = 0
        self.meeples = 7

class Game:
    def __init__(self, num_players):
        self.board = Board()
        self.players = [Player(i) for i in range(num_players)]
        self.current_player = 0
        self.tiles = TILE_TYPES * (84 // len(TILE_TYPES))
        random.shuffle(self.tiles)
        self.meeples_placed = {}
    def draw_tile(self):
        if self.tiles:
            return self.tiles.pop()
        return None
    def place_tile(self, x, y, tile, rotation):
        if self.board.place_tile(x, y, tile, rotation):
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in self.board.grid and self.board.grid[(nx, ny)]['center'] == 'monastery':
                        if self.is_monastery_completed(nx, ny):
                            self.score_monastery(nx, ny)
            return True
        return False
    def is_monastery_completed(self, x, y):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if (x + dx, y + dy) not in self.board.grid:
                    return False
        return True
    def score_monastery(self, x, y):
        if (x, y, 'center') in self.meeples_placed:
            player_id = self.meeples_placed[(x, y, 'center')]
            self.players[player_id].score += 9
            self.players[player_id].meeples += 1
            del self.meeples_placed[(x, y, 'center')]
    def place_meeple(self, x, y, direction, player_id):
        if (x, y, direction) in self.meeples_placed or self.players[player_id].meeples <= 0:
            return False
        tile = self.board.grid[(x, y)]
        if tile[direction] is None:
            return False
        for fid, tiles in self.board.feature_tiles.items():
            if (x, y, direction) in tiles:
                root_id = self.board.uf.find(fid)
                break
        for pos, pid in self.meeples_placed.items():
            if pos[2] != 'center':
                for ffid, ftiles in self.board.feature_tiles.items():
                    if pos in ftiles and self.board.uf.find(ffid) == root_id:
                        return False
        self.meeples_placed[(x, y, direction)] = player_id
        self.players[player_id].meeples -= 1
        return True
    def final_scoring(self):
        for (x, y, direction), player_id in list(self.meeples_placed.items()):
            if direction == 'center':
                score = 1
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if (x + dx, y + dy) in self.board.grid:
                            score += 1
                self.players[player_id].score += score
                self.players[player_id].meeples += 1
                del self.meeples_placed[(x, y, direction)]
            else:
                for fid, tiles in self.board.feature_tiles.items():
                    if (x, y, direction) in tiles:
                        root_id = self.board.uf.find(fid)
                        break
                tiles_in_feature = [t for t in self.board.feature_tiles[root_id] if t[2] != 'center']
                num_tiles = len(set((t[0], t[1]) for t in tiles_in_feature))
                self.players[player_id].score += num_tiles
                self.players[player_id].meeples += 1
                del self.meeples_placed[(x, y, direction)]

TILE_TYPES = [
    {'code': 'A', 'north': 'road', 'south': 'road', 'east': 'field', 'west': 'field', 'center': None},
    {'code': 'B', 'north': 'city', 'south': 'field', 'east': 'road', 'west': 'road', 'center': None},
    {'code': 'C', 'north': 'field', 'south': 'field', 'east': 'field', 'west': 'field', 'center': 'monastery'},
    {'code': 'D', 'north': 'city', 'south': 'city', 'east': 'field', 'west': 'field', 'center': None},
    {'code': 'E', 'north': 'road', 'south': 'field', 'east': 'road', 'west': 'field', 'center': None},
]
START_TILE = {'code': 'S', 'north': 'field', 'south': 'field', 'east': 'field', 'west': 'field', 'center': None}

class CarcassonneGUI:
    def __init__(self, master):
        self.master = master
        master.title("Carcassonne")
        self.game = None
        self.current_tile = None
        
        # Текстовое поле для логов
        self.log_text = tk.Text(master, height=10, width=50, font=("Arial", 12))
        self.log_text.pack(pady=10)
        
        # Кнопка "Новая игра"
        self.new_game_button = tk.Button(master, text="Новая игра", command=self.new_game, font=("Arial", 12))
        self.new_game_button.pack(pady=5)
        
        # Фрейм для ввода хода
        self.input_frame = tk.Frame(master)
        self.input_frame.pack(pady=10)
        
        # Поля ввода координат и направления
        self.x_label = tk.Label(self.input_frame, text="x:", font=("Arial", 12))
        self.x_label.grid(row=0, column=0, padx=5)
        self.x_entry = tk.Entry(self.input_frame, width=5, font=("Arial", 12))
        self.x_entry.grid(row=0, column=1, padx=5)
        
        self.y_label = tk.Label(self.input_frame, text="y:", font=("Arial", 12))
        self.y_label.grid(row=0, column=2, padx=5)
        self.y_entry = tk.Entry(self.input_frame, width=5, font=("Arial", 12))
        self.y_entry.grid(row=0, column=3, padx=5)
        
        self.dir_label = tk.Label(self.input_frame, text="Направление (north/south/east/west/center):", font=("Arial", 12))
        self.dir_label.grid(row=1, column=0, columnspan=4, pady=5)
        self.dir_entry = tk.Entry(self.input_frame, width=15, font=("Arial", 12))
        self.dir_entry.grid(row=1, column=4, padx=5)
        
        # Кнопка "Сделать ход"
        self.move_button = tk.Button(self.input_frame, text="Сделать ход", command=self.make_move, font=("Arial", 12))
        self.move_button.grid(row=2, column=0, columnspan=5, pady=10)
        
    def new_game(self):
        self.game = Game(2)
        self.current_tile = self.game.draw_tile()
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "Новая игра началась.\n")
        self.log_text.insert(tk.END, f"Текущая плитка: {self.current_tile['code']}\n")
        self.log_text.insert(tk.END, f"Игрок {self.game.current_player + 1}, ваш ход.\n")
    
    def make_move(self):
        if not self.game:
            messagebox.showerror("Ошибка", "Начните новую игру.")
            return
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            direction = self.dir_entry.get().strip()
            if direction not in ['north', 'south', 'east', 'west', 'center', '']:
                messagebox.showerror("Ошибка", "Недопустимое направление. Используйте north, south, east, west или center.")
                return
            if self.game.place_tile(x, y, self.current_tile, 0):
                self.log_text.insert(tk.END, f"Плитка размещена на ({x}, {y})\n")
                if direction:
                    if self.game.place_meeple(x, y, direction, self.game.current_player):
                        self.log_text.insert(tk.END, f"Мипл размещен на ({x}, {y}, {direction})\n")
                    else:
                        messagebox.showerror("Ошибка", "Недопустимое размещение мипла.")
                        return
                self.game.current_player = (self.game.current_player + 1) % len(self.game.players)
                self.current_tile = self.game.draw_tile()
                if self.current_tile:
                    self.log_text.insert(tk.END, f"Текущая плитка: {self.current_tile['code']}\n")
                    self.log_text.insert(tk.END, f"Игрок {self.game.current_player + 1}, ваш ход.\n")
                else:
                    self.game.final_scoring()
                    max_score = max(p.score for p in self.game.players)
                    winners = [i + 1 for i, p in enumerate(self.game.players) if p.score == max_score]
                    self.log_text.insert(tk.END, f"Игра окончена. Победитель(и): {winners}\n")
                    self.log_text.insert(tk.END, f"Очки: {[p.score for p in self.game.players]}\n")
            else:
                messagebox.showerror("Ошибка", "Недопустимое размещение плитки.")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный ввод координат. Введите целые числа.")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x400")
    gui = CarcassonneGUI(root)
    root.mainloop()
