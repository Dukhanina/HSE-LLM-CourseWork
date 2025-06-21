import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import random
import math
from collections import defaultdict
from PIL import Image, ImageTk, ImageDraw
import os

class Tile:
    def __init__(self, north, east, south, west, center=None, shield=False):
        self.edges = {'N': north, 'E': east, 'S': south, 'W': west}
        self.center = center  # 'MONASTERY' or None
        self.shield = shield
        self.rotation = 0
        self.image = None
    
    def rotate(self, times=1):
        for _ in range(times % 4):
            n = self.edges['N']
            self.edges['N'] = self.edges['W']
            self.edges['W'] = self.edges['S']
            self.edges['S'] = self.edges['E']
            self.edges['E'] = n
        self.rotation = (self.rotation + times) % 4
        return self
    
    def create_image(self, size=100):
        """Create a visual representation of the tile"""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw tile background
        draw.rectangle([0, 0, size, size], fill="#F0E68C", outline="black")
        
        # Define colors
        colors = {
            'FIELD': "#7CFC00",
            'ROAD': "#A9A9A9",
            'CITY': "#4169E1"
        }
        
        # Draw edges
        edge_size = size // 3
        edge_positions = {
            'N': (0, 0, size, edge_size),
            'E': (size - edge_size, 0, size, size),
            'S': (0, size - edge_size, size, size),
            'W': (0, 0, edge_size, size)
        }
        
        for edge, pos in edge_positions.items():
            color = colors.get(self.edges[edge], "#7CFC00")
            draw.rectangle(pos, fill=color, outline="black")
            
            # Draw road indicator
            if self.edges[edge] == 'ROAD':
                road_width = size // 6
                center_x = size // 2
                center_y = size // 2
                
                if edge == 'N':
                    draw.rectangle([center_x - road_width//2, 0, 
                                   center_x + road_width//2, center_y], 
                                  fill="#A9A9A9", outline="black")
                elif edge == 'E':
                    draw.rectangle([center_x, center_y - road_width//2, 
                                   size, center_y + road_width//2], 
                                  fill="#A9A9A9", outline="black")
                elif edge == 'S':
                    draw.rectangle([center_x - road_width//2, center_y, 
                                   center_x + road_width//2, size], 
                                  fill="#A9A9A9", outline="black")
                elif edge == 'W':
                    draw.rectangle([0, center_y - road_width//2, 
                                   center_x, center_y + road_width//2], 
                                  fill="#A9A9A9", outline="black")
        
        # Draw center for monastery
        if self.center == 'MONASTERY':
            draw.rectangle([size//2-15, size//2-15, size//2+15, size//2+15], 
                          fill="#8B4513", outline="black")
            draw.ellipse([size//2-10, size//2-10, size//2+10, size//2+10], 
                        fill="#DAA520", outline="black")
        
        # Draw shield if present
        if self.shield:
            draw.rectangle([size//2-10, size//2-10, size//2+10, size//2+10], 
                          fill="gold", outline="black")
            draw.text((size//2-5, size//2-5), "S", fill="black")
        
        # Draw connection points
        connection_size = size // 8
        connection_points = [
            (size//2, size//4),    # North
            (3*size//4, size//2),   # East
            (size//2, 3*size//4),   # South
            (size//4, size//2)       # West
        ]
        
        for point in connection_points:
            draw.ellipse([point[0]-connection_size, point[1]-connection_size,
                         point[0]+connection_size, point[1]+connection_size],
                        fill="#F0E68C", outline="black")
        
        return ImageTk.PhotoImage(img)

class Player:
    def __init__(self, player_id, color):
        self.id = player_id
        self.color = color
        self.meeples = 7
        self.score = 0
        self.active_meeples = {}  # (x, y): feature

class CarcassonneGame:
    def __init__(self, num_players=2):
        self.num_players = num_players
        colors = ['red', 'blue', 'green', 'yellow', 'purple']
        self.players = [Player(i, colors[i]) for i in range(num_players)]
        self.current_player = 0
        self.board = {}
        self.features = defaultdict(list)  # feature_type: [(x, y, player_id)]
        self.remaining_tiles = self.create_tiles()
        random.shuffle(self.remaining_tiles)
        self.start_tile = Tile('CITY', 'ROAD', 'FIELD', 'ROAD')
        self.board[(0, 0)] = self.start_tile
        self.game_over = False
        self.current_tile = None
        self.selected_position = None
        self.selected_rotation = 0
        self.selected_feature = None
    
    def create_tiles(self):
        tiles = [
            Tile('CITY', 'ROAD', 'ROAD', 'ROAD'),  # 3-way road
            Tile('CITY', 'FIELD', 'FIELD', 'CITY', shield=True),  # City with shield
            Tile('ROAD', 'ROAD', 'FIELD', 'FIELD'),  # Straight road
            Tile('ROAD', 'FIELD', 'ROAD', 'FIELD'),  # Curved road
            Tile('FIELD', 'FIELD', 'FIELD', 'FIELD', center='MONASTERY'),  # Monastery
            Tile('CITY', 'CITY', 'CITY', 'CITY', shield=True),  # Full city
            Tile('CITY', 'ROAD', 'ROAD', 'CITY'),  # City with road through
            Tile('ROAD', 'FIELD', 'FIELD', 'ROAD'),  # Curved road
            Tile('CITY', 'ROAD', 'FIELD', 'ROAD'),  # City with road
            Tile('ROAD', 'ROAD', 'ROAD', 'ROAD'),  # Crossroads
        ]
        return tiles * 8  # Replicate to have enough tiles
    
    def draw_tile(self):
        if not self.remaining_tiles:
            return None
        self.current_tile = self.remaining_tiles.pop()
        return self.current_tile
    
    def get_valid_placements(self):
        valid_placements = []
        if not self.board:
            return [(0, 0, 0)]  # Only position for first tile
        
        for (x, y), existing_tile in self.board.items():
            for dx, dy, direction in [(0, 1, 'S'), (1, 0, 'W'), (0, -1, 'N'), (-1, 0, 'E')]:
                new_pos = (x + dx, y + dy)
                if new_pos in self.board:
                    continue
                
                # Check compatibility with neighbors
                for rot in range(4):
                    test_tile = Tile(
                        self.current_tile.edges['N'],
                        self.current_tile.edges['E'],
                        self.current_tile.edges['S'],
                        self.current_tile.edges['W'],
                        self.current_tile.center,
                        self.current_tile.shield
                    ).rotate(rot)
                    
                    valid = True
                    
                    # Check north neighbor
                    north_pos = (new_pos[0], new_pos[1] + 1)
                    if north_pos in self.board:
                        if test_tile.edges['N'] != self.board[north_pos].edges['S']:
                            valid = False
                    
                    # Check east neighbor
                    east_pos = (new_pos[0] + 1, new_pos[1])
                    if east_pos in self.board:
                        if test_tile.edges['E'] != self.board[east_pos].edges['W']:
                            valid = False
                    
                    # Check south neighbor
                    south_pos = (new_pos[0], new_pos[1] - 1)
                    if south_pos in self.board:
                        if test_tile.edges['S'] != self.board[south_pos].edges['N']:
                            valid = False
                    
                    # Check west neighbor
                    west_pos = (new_pos[0] - 1, new_pos[1])
                    if west_pos in self.board:
                        if test_tile.edges['W'] != self.board[west_pos].edges['E']:
                            valid = False
                    
                    if valid:
                        valid_placements.append((new_pos[0], new_pos[1], rot))
        
        return valid_placements
    
    def place_tile(self, x, y, rotation):
        if not self.current_tile:
            return False, "No tile to place"
        
        tile = Tile(
            self.current_tile.edges['N'],
            self.current_tile.edges['E'],
            self.current_tile.edges['S'],
            self.current_tile.edges['W'],
            self.current_tile.center,
            self.current_tile.shield
        ).rotate(rotation)
        
        self.board[(x, y)] = tile
        self.current_tile = None
        return True, f"Tile placed at ({x}, {y})"
    
    def place_meeple(self, player_id, x, y, feature):
        player = self.players[player_id]
        if player.meeples <= 0:
            return False, "No meeples left"
        
        # Check if there's already a meeple on this tile
        for p in self.players:
            if (x, y) in p.active_meeples:
                return False, "Tile already has a meeple"
        
        # Place meeple
        player.meeples -= 1
        player.active_meeples[(x, y)] = feature
        self.features[feature].append((x, y, player_id))
        return True, f"Player {player_id} placed meeple on {feature}"
    
    def score_road(self, x, y):
        # Simplified scoring: count connected road tiles
        return 1
    
    def score_city(self, x, y):
        tile = self.board[(x, y)]
        points = 2
        if tile.shield:
            points += 2
        return points
    
    def score_monastery(self, x, y):
        # Count surrounding tiles
        count = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (dx, dy) != (0, 0) and (x + dx, y + dy) in self.board:
                    count += 1
        return count
    
    def check_completed_features(self, x, y):
        tile = self.board[(x, y)]
        scored = []
        
        # Check all features on this tile
        if any(edge == 'ROAD' for edge in tile.edges.values()):
            scored.append(('ROAD', self.score_road(x, y)))
        if any(edge == 'CITY' for edge in tile.edges.values()):
            scored.append(('CITY', self.score_city(x, y)))
        if tile.center == 'MONASTERY':
            score = self.score_monastery(x, y)
            if score == 8:  # Fully surrounded
                scored.append(('MONASTERY', score))
        
        # Award points and return meeples
        for feature_type, points in scored:
            if feature_type in self.features:
                for pos in self.features[feature_type][:]:
                    if pos[0] == x and pos[1] == y:
                        player_id = pos[2]
                        self.players[player_id].score += points
                        self.players[player_id].meeples += 1
                        # Remove meeple from player's active meeples
                        if (x, y) in self.players[player_id].active_meeples:
                            del self.players[player_id].active_meeples[(x, y)]
                        self.features[feature_type].remove(pos)
        
        return scored
    
    def final_scoring(self):
        # Score incomplete features
        for feature_type, positions in self.features.items():
            for x, y, player_id in positions:
                if feature_type == 'ROAD':
                    self.players[player_id].score += 1
                elif feature_type == 'CITY':
                    self.players[player_id].score += 1
                elif feature_type == 'MONASTERY':
                    count = 0
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            if (dx, dy) != (0, 0) and (x + dx, y + dy) in self.board:
                                count += 1
                    self.players[player_id].score += count
        
        # Return all meeples
        for player in self.players:
            for pos in list(player.active_meeples.keys()):
                player.meeples += 1
            player.active_meeples.clear()
        
        self.features.clear()
        self.game_over = True

class CarcassonneGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Carcassonne")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2c3e50")
        
        # Game variables
        self.game = None
        self.tile_size = 70
        self.board_offset = (350, 150)
        self.selected_pos = None
        self.selected_rot = 0
        self.valid_placements = []
        self.meeple_placement_mode = False
        self.current_tile_pos = None
        self.meeple_features = []
        
        # Create UI elements
        self.create_widgets()
        
        # Start with a new game dialog
        self.start_new_game()
        
        self.root.mainloop()
    
    def create_widgets(self):
        # Main frames
        main_frame = tk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - controls and info
        left_panel = tk.Frame(main_frame, bg="#34495e", bd=2, relief=tk.RAISED)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=10)
        
        # Player info
        player_frame = tk.LabelFrame(left_panel, text="Players", bg="#34495e", fg="white", font=("Arial", 10, "bold"))
        player_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.player_labels = []
        for i in range(5):  # Max players
            frame = tk.Frame(player_frame, bg="#34495e")
            frame.pack(fill=tk.X, padx=5, pady=2)
            color_box = tk.Canvas(frame, width=20, height=20, bg="#34495e", highlightthickness=0)
            color_box.pack(side=tk.LEFT, padx=(0, 5))
            color_box.create_rectangle(2, 2, 18, 18, fill="gray", outline="white")
            label = tk.Label(frame, text=f"Player {i}: 0 pts, 7 meeples", 
                           bg="#34495e", fg="white", anchor="w")
            label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.player_labels.append((color_box, label))
        
        # Current tile frame
        tile_frame = tk.LabelFrame(left_panel, text="Current Tile", bg="#34495e", fg="white", font=("Arial", 10, "bold"))
        tile_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.tile_canvas = tk.Canvas(tile_frame, width=120, height=120, bg="#2c3e50", highlightthickness=0)
        self.tile_canvas.pack(padx=10, pady=5)
        
        # Rotation controls
        rot_frame = tk.Frame(tile_frame, bg="#34495e")
        rot_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(rot_frame, text="↺ Rotate Left", command=lambda: self.rotate_tile(1),
                 bg="#3498db", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(rot_frame, text="↻ Rotate Right", command=lambda: self.rotate_tile(3),
                 bg="#3498db", fg="white", relief=tk.FLAT).pack(side=tk.LEFT)
        
        # Action buttons
        btn_frame = tk.Frame(left_panel, bg="#34495e")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.place_tile_btn = tk.Button(btn_frame, text="Place Tile", command=self.place_tile,
                                      bg="#2ecc71", fg="white", font=("Arial", 10, "bold"),
                                      state=tk.DISABLED, width=12)
        self.place_tile_btn.pack(pady=5)
        
        self.place_meeple_btn = tk.Button(btn_frame, text="Place Meeple", command=self.place_meeple,
                                        bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
                                        state=tk.DISABLED, width=12)
        self.place_meeple_btn.pack(pady=5)
        
        self.skip_btn = tk.Button(btn_frame, text="Skip Turn", command=self.skip_meeple,
                                 bg="#f39c12", fg="white", font=("Arial", 10, "bold"), width=12)
        self.skip_btn.pack(pady=5)
        
        # Game log
        log_frame = tk.LabelFrame(left_panel, text="Game Log", bg="#34495e", fg="white", font=("Arial", 10, "bold"))
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, bg="#2c3e50", fg="white")
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)
        
        # Board canvas
        board_frame = tk.Frame(main_frame, bg="#2c3e50")
        board_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(board_frame, bg="#2c3e50", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.canvas_click)
        
        # Status bar
        status_bar = tk.Frame(self.root, bg="#34495e", height=25)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = tk.Label(status_bar, text="Start a new game", 
                                   bg="#34495e", fg="white", anchor="w")
        self.status_label.pack(fill=tk.X, padx=10)
    
    def log_message(self, message, player_id=None):
        self.log_text.config(state=tk.NORMAL)
        
        if player_id is not None and self.game and player_id < len(self.game.players):
            color = self.game.players[player_id].color
            self.log_text.tag_config(f"player{player_id}", foreground=color)
            self.log_text.insert(tk.END, message + "\n", f"player{player_id}")
        else:
            self.log_text.insert(tk.END, message + "\n")
            
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def start_new_game(self):
        # Create dialog for game setup
        setup_dialog = tk.Toplevel(self.root)
        setup_dialog.title("New Game Setup")
        setup_dialog.geometry("300x200")
        setup_dialog.transient(self.root)
        setup_dialog.grab_set()
        setup_dialog.configure(bg="#2c3e50")
        
        tk.Label(setup_dialog, text="Carcassonne", font=("Arial", 16, "bold"), 
                bg="#2c3e50", fg="white").pack(pady=(20, 10))
        
        tk.Label(setup_dialog, text="Number of players (2-5):", 
                bg="#2c3e50", fg="white").pack(pady=5)
        
        num_players_var = tk.StringVar(value="2")
        num_players_combo = ttk.Combobox(setup_dialog, textvariable=num_players_var, 
                                         values=["2", "3", "4", "5"], width=5, state="readonly")
        num_players_combo.pack(pady=5)
        
        def on_submit():
            try:
                num_players = int(num_players_var.get())
                if num_players < 2 or num_players > 5:
                    raise ValueError("Number of players must be between 2 and 5")
                
                self.game = CarcassonneGame(num_players)
                setup_dialog.destroy()
                self.draw_board()
                self.update_player_info()
                self.draw_current_tile()
                self.log_message("New game started!")
                self.log_message(f"Player {self.game.current_player}'s turn", self.game.current_player)
                self.update_status()
            except ValueError as e:
                messagebox.showerror("Invalid Input", str(e))
        
        btn_frame = tk.Frame(setup_dialog, bg="#2c3e50")
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="Start Game", command=on_submit,
                 bg="#2ecc71", fg="white", width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Cancel", command=setup_dialog.destroy,
                 bg="#e74c3c", fg="white", width=10).pack(side=tk.LEFT)
    
    def draw_board(self):
        self.canvas.delete("all")
        
        # Draw grid
        grid_color = "#3d566e"
        for x in range(-10, 11):
            for y in range(-10, 11):
                screen_x, screen_y = self.board_to_screen(x, y)
                self.canvas.create_rectangle(
                    screen_x, screen_y,
                    screen_x + self.tile_size, screen_y + self.tile_size,
                    outline=grid_color, fill=""
                )
        
        # Draw placed tiles
        for (x, y), tile in self.game.board.items():
            self.draw_tile_at(x, y, tile)
        
        # Highlight valid placements
        if self.game.current_tile and not self.meeple_placement_mode:
            self.valid_placements = self.game.get_valid_placements()
            for x, y, _ in self.valid_placements:
                screen_x, screen_y = self.board_to_screen(x, y)
                self.canvas.create_rectangle(
                    screen_x, screen_y,
                    screen_x + self.tile_size, screen_y + self.tile_size,
                    outline="#2ecc71", width=2, dash=(2, 2)
                )
        
        # Highlight current tile for meeple placement
        if self.meeple_placement_mode and self.current_tile_pos:
            x, y = self.current_tile_pos
            screen_x, screen_y = self.board_to_screen(x, y)
            self.canvas.create_rectangle(
                screen_x, screen_y,
                screen_x + self.tile_size, screen_y + self.tile_size,
                outline="#e74c3c", width=3
            )
    
    def draw_tile_at(self, x, y, tile):
        screen_x, screen_y = self.board_to_screen(x, y)
        
        # Create tile image if not exists
        if not hasattr(tile, 'image') or tile.image is None:
            tile.image = tile.create_image(self.tile_size)
        
        # Draw tile
        self.canvas.create_image(
            screen_x + self.tile_size // 2, 
            screen_y + self.tile_size // 2, 
            image=tile.image
        )
        
        # Draw meeples
        for player in self.game.players:
            if (x, y) in player.active_meeples:
                cx = screen_x + self.tile_size // 2
                cy = screen_y + self.tile_size // 2
                feature = player.active_meeples[(x, y)]
                
                # Position meeple based on feature
                if feature == 'MONASTERY':
                    meeple_x, meeple_y = cx, cy
                elif feature == 'CITY':
                    # Position on one of the city edges
                    if tile.edges['N'] == 'CITY':
                        meeple_x, meeple_y = cx, screen_y + self.tile_size // 4
                    elif tile.edges['E'] == 'CITY':
                        meeple_x, meeple_y = screen_x + 3 * self.tile_size // 4, cy
                    elif tile.edges['S'] == 'CITY':
                        meeple_x, meeple_y = cx, screen_y + 3 * self.tile_size // 4
                    else:  # West
                        meeple_x, meeple_y = screen_x + self.tile_size // 4, cy
                else:  # ROAD
                    # Position at intersection
                    meeple_x, meeple_y = cx, cy
                
                self.canvas.create_oval(
                    meeple_x - 10, meeple_y - 10,
                    meeple_x + 10, meeple_y + 10,
                    fill=player.color, outline="black", width=2
                )
    
    def draw_current_tile(self):
        self.tile_canvas.delete("all")
        
        if not self.game or not self.game.current_tile:
            return
        
        # Create tile image if not exists
        if not hasattr(self.game.current_tile, 'image') or self.game.current_tile.image is None:
            self.game.current_tile.image = self.game.current_tile.create_image(100)
        
        # Draw tile
        self.tile_canvas.create_image(60, 60, image=self.game.current_tile.image)
    
    def board_to_screen(self, x, y):
        screen_x = self.board_offset[0] + x * self.tile_size
        screen_y = self.board_offset[1] + y * self.tile_size
        return screen_x, screen_y
    
    def screen_to_board(self, screen_x, screen_y):
        x = round((screen_x - self.board_offset[0]) / self.tile_size)
        y = round((screen_y - self.board_offset[1]) / self.tile_size)
        return x, y
    
    def canvas_click(self, event):
        if not self.game or self.game.game_over:
            return
        
        x, y = self.screen_to_board(event.x, event.y)
        
        # Meeple placement mode
        if self.meeple_placement_mode:
            # Check if click is on the current tile
            if (x, y) == self.current_tile_pos:
                # Determine which feature was clicked
                tile = self.game.board[(x, y)]
                screen_x, screen_y = self.board_to_screen(x, y)
                
                # Calculate relative position within tile
                rel_x = event.x - screen_x
                rel_y = event.y - screen_y
                tile_center = self.tile_size / 2
                
                # Determine which feature was clicked
                if tile.center == 'MONASTERY':
                    # Check if clicked near center
                    if (abs(rel_x - tile_center) < 20 and 
                        abs(rel_y - tile_center) < 20):
                        self.selected_feature = 'MONASTERY'
                
                # Check for city edges
                city_edges = []
                if tile.edges['N'] == 'CITY':
                    city_edges.append('N')
                if tile.edges['E'] == 'CITY':
                    city_edges.append('E')
                if tile.edges['S'] == 'CITY':
                    city_edges.append('S')
                if tile.edges['W'] == 'CITY':
                    city_edges.append('W')
                
                # Check if clicked on a city edge
                for edge in city_edges:
                    if edge == 'N' and rel_y < self.tile_size / 3:
                        self.selected_feature = 'CITY'
                    elif edge == 'E' and rel_x > 2 * self.tile_size / 3:
                        self.selected_feature = 'CITY'
                    elif edge == 'S' and rel_y > 2 * self.tile_size / 3:
                        self.selected_feature = 'CITY'
                    elif edge == 'W' and rel_x < self.tile_size / 3:
                        self.selected_feature = 'CITY'
                
                # Check for road
                if not self.selected_feature and any(edge == 'ROAD' for edge in tile.edges.values()):
                    # Check if clicked near the center or along a road
                    if (abs(rel_x - tile_center) < 15 or 
                        abs(rel_y - tile_center) < 15):
                        self.selected_feature = 'ROAD'
                
                if self.selected_feature:
                    self.place_meeple()
                else:
                    messagebox.showinfo("Invalid Placement", "Please click on a valid feature (city, road, or monastery)")
            else:
                messagebox.showinfo("Invalid Tile", "You can only place a meeple on the tile you just placed")
            return
        
        # Tile placement mode
        if self.game.current_tile:
            # Check if position is valid
            for px, py, rot in self.valid_placements:
                if px == x and py == y:
                    self.selected_pos = (x, y)
                    self.selected_rot = self.selected_rot  # Use current rotation
                    self.place_tile()
                    return
            messagebox.showinfo("Invalid Placement", "Cannot place tile here")
    
    def rotate_tile(self, times=1):
        if self.game and self.game.current_tile:
            self.selected_rot = (self.selected_rot + times) % 4
            self.game.current_tile.rotate(times)
            self.draw_current_tile()
    
    def place_tile(self):
        if not self.selected_pos:
            return
        
        x, y = self.selected_pos
        success, message = self.game.place_tile(x, y, self.selected_rot)
        if success:
            self.log_message(f"Player {self.game.current_player} placed tile at ({x}, {y})", 
                            self.game.current_player)
            
            # Check for completed features
            scored = self.game.check_completed_features(x, y)
            if scored:
                self.log_message(f"Scored features: {scored}")
            
            # Update board and player info
            self.draw_board()
            self.update_player_info()
            self.update_status()
            
            # Enable meeple placement
            player = self.game.players[self.game.current_player]
            self.current_tile_pos = (x, y)
            
            # Determine available features
            self.meeple_features = []
            tile = self.game.board[(x, y)]
            if any(edge == 'ROAD' for edge in tile.edges.values()):
                self.meeple_features.append('ROAD')
            if any(edge == 'CITY' for edge in tile.edges.values()):
                self.meeple_features.append('CITY')
            if tile.center == 'MONASTERY':
                self.meeple_features.append('MONASTERY')
            
            if player.meeples > 0 and self.meeple_features:
                self.meeple_placement_mode = True
                self.place_tile_btn.config(state=tk.DISABLED)
                self.place_meeple_btn.config(state=tk.DISABLED)
                self.skip_btn.config(state=tk.NORMAL)
                self.status_label.config(text=f"Click on a feature to place your meeple")
                self.draw_board()
            else:
                self.next_turn()
        else:
            messagebox.showerror("Placement Error", message)
    
    def place_meeple(self):
        if not self.selected_feature:
            return
        
        x, y = self.current_tile_pos
        success, message = self.game.place_meeple(self.game.current_player, x, y, self.selected_feature)
        if success:
            self.log_message(message, self.game.current_player)
            self.update_player_info()
            self.draw_board()
            self.next_turn()
        else:
            messagebox.showerror("Placement Error", message)
    
    def skip_meeple(self):
        self.log_message(f"Player {self.game.current_player} skipped meeple placement", 
                        self.game.current_player)
        self.next_turn()
    
    def next_turn(self):
        # Reset UI
        self.meeple_placement_mode = False
        self.selected_feature = None
        self.current_tile_pos = None
        self.place_tile_btn.config(state=tk.DISABLED)
        self.place_meeple_btn.config(state=tk.DISABLED)
        self.skip_btn.config(state=tk.DISABLED)
        
        # Check if game is over
        if not self.game.remaining_tiles:
            self.game.final_scoring()
            self.log_message("Game over! Final scoring completed.")
            self.update_player_info()
            self.draw_board()
            
            max_score = max(p.score for p in self.game.players)
            winners = [i for i, p in enumerate(self.game.players) if p.score == max_score]
            
            if len(winners) == 1:
                messagebox.showinfo("Game Over", f"Player {winners[0]} wins with {max_score} points!")
            else:
                messagebox.showinfo("Game Over", f"Tie between players {', '.join(map(str, winners))} with {max_score} points!")
            
            return
        
        # Move to next player
        self.game.current_player = (self.game.current_player + 1) % self.game.num_players
        
        # Draw new tile
        self.game.draw_tile()
        self.selected_rot = 0
        self.draw_current_tile()
        self.draw_board()
        
        # Update status
        self.update_status()
    
    def update_player_info(self):
        if not self.game:
            return
        
        for i, player in enumerate(self.game.players):
            if i < len(self.player_labels):
                color_box, label = self.player_labels[i]
                color_box.delete("all")
                color_box.create_rectangle(2, 2, 18, 18, fill=player.color, outline="white")
                
                active = " (Active)" if i == self.game.current_player else ""
                label.config(text=f"Player {i}: {player.score} pts, {player.meeples} meeples{active}",
                           fg="white" if i != self.game.current_player else "yellow")
                label.pack()
    
    def update_status(self):
        if not self.game:
            return
        
        player = self.game.players[self.game.current_player]
        status = f"Player {self.game.current_player}'s turn ({player.color})"
        
        if self.game.current_tile:
            status += " - Place a tile on the board"
        elif self.meeple_placement_mode:
            status += " - Click on a feature to place your meeple"
        
        self.status_label.config(text=status)

if __name__ == "__main__":
    app = CarcassonneGUI()
