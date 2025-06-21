import random
from collections import defaultdict

class Tile:
    def __init__(self, north, east, south, west, center=None, shield=False):
        self.edges = {'N': north, 'E': east, 'S': south, 'W': west}
        self.center = center  # 'MONASTERY' or None
        self.shield = shield
        self.rotation = 0
    
    def rotate(self, times=1):
        for _ in range(times % 4):
            n = self.edges['N']
            self.edges['N'] = self.edges['W']
            self.edges['W'] = self.edges['S']
            self.edges['S'] = self.edges['E']
            self.edges['E'] = n
        self.rotation = (self.rotation + times) % 4
        return self
    
    def __str__(self):
        return f"Tile(N:{self.edges['N']}, E:{self.edges['E']}, S:{self.edges['S']}, W:{self.edges['W']}" + \
               (f", Center:{self.center}" if self.center else "") + (", Shield" if self.shield else "")

class Player:
    def __init__(self, player_id):
        self.id = player_id
        self.meeples = 7
        self.score = 0
        self.active_meeples = defaultdict(list)  # (x, y): [features]

class CarcassonneGame:
    def __init__(self, num_players=2):
        self.num_players = num_players
        self.players = [Player(i) for i in range(num_players)]
        self.current_player = 0
        self.board = {}
        self.features = defaultdict(list)  # feature_type: [(x, y, player_id)]
        self.remaining_tiles = self.create_tiles()
        random.shuffle(self.remaining_tiles)
        self.start_tile = Tile('CITY', 'ROAD', 'FIELD', 'ROAD')
        self.board[(0, 0)] = self.start_tile
        self.game_over = False
    
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
    
    def get_valid_placements(self, tile):
        valid_placements = []
        if not self.board:
            return [(0, 0, 0)]  # Only position for first tile
        
        for (x, y), existing_tile in self.board.items():
            for dx, dy, direction in [(0, 1, 'S'), (1, 0, 'W'), (0, -1, 'N'), (-1, 0, 'E')]:
                new_pos = (x + dx, y + dy)
                if new_pos in self.board:
                    continue
                
                # Check compatibility with neighbors
                valid = True
                for rot in range(4):
                    test_tile = Tile(tile.edges['N'], tile.edges['E'], tile.edges['S'], tile.edges['W'], tile.center, tile.shield).rotate(rot)
                    
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
                    valid = True  # Reset for next rotation
        
        return valid_placements
    
    def place_tile(self, x, y, rotation, tile):
        tile = Tile(tile.edges['N'], tile.edges['E'], tile.edges['S'], tile.edges['W'], tile.center, tile.shield).rotate(rotation)
        self.board[(x, y)] = tile
        return tile
    
    def place_meeple(self, player_id, x, y, feature):
        player = self.players[player_id]
        if player.meeples <= 0:
            return False, "No meeples left"
        
        # Check if feature is already occupied
        for _, positions in self.features.items():
            for pos in positions:
                if pos[0] == x and pos[1] == y and pos[2] == feature:
                    return False, "Feature already occupied"
        
        # Place meeple
        player.meeples -= 1
        self.features[feature].append((x, y, player_id))
        player.active_meeples[(x, y)].append(feature)
        return True, f"Player {player_id} placed meeple on {feature}"
    
    def score_road(self, x, y):
        # Simplified scoring: count connected road tiles
        # In real Carcassonne, this would use graph traversal
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
                if (x + dx, y + dy) in self.board:
                    count += 1
        return count
    
    def check_completed_features(self, x, y):
        tile = self.board[(x, y)]
        scored = []
        
        # Check all features on this tile
        for feature in ['ROAD', 'CITY']:
            # Simplified: just check if the feature is complete
            # In real game, this would require graph traversal
            if tile.edges['N'] == feature:
                scored.append(('ROAD', self.score_road(x, y)))
            if tile.edges['E'] == feature:
                scored.append(('ROAD', self.score_road(x, y)))
            if tile.edges['S'] == feature:
                scored.append(('ROAD', self.score_road(x, y)))
            if tile.edges['W'] == feature:
                scored.append(('ROAD', self.score_road(x, y)))
            if any(edge == 'CITY' for edge in tile.edges.values()):
                scored.append(('CITY', self.score_city(x, y)))
        
        if tile.center == 'MONASTERY':
            score = self.score_monastery(x, y)
            if score == 9:  # Fully surrounded
                scored.append(('MONASTERY', score))
        
        # Award points and return meeples
        for feature_type, points in scored:
            if feature_type in self.features:
                for pos in self.features[feature_type][:]:
                    if pos[0] == x and pos[1] == y:
                        player_id = pos[2]
                        self.players[player_id].score += points
                        self.players[player_id].meeples += 1
                        self.features[feature_type].remove(pos)
                        if (x, y) in self.players[player_id].active_meeples:
                            if feature_type in self.players[player_id].active_meeples[(x, y)]:
                                self.players[player_id].active_meeples[(x, y)].remove(feature_type)
        
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
                            if (x + dx, y + dy) in self.board:
                                count += 1
                    self.players[player_id].score += count
        
        # Return all meeples
        for player in self.players:
            player.meeples += sum(len(features) for features in player.active_meeples.values())
            player.active_meeples.clear()
        
        self.features.clear()
    
    def play_turn(self):
        if not self.remaining_tiles or self.game_over:
            self.final_scoring()
            self.game_over = True
            return False
        
        player = self.players[self.current_player]
        tile = self.remaining_tiles.pop()
        
        # Get valid placements
        valid_placements = self.get_valid_placements(tile)
        if not valid_placements:
            print("No valid placements available. Discarding tile.")
            return True
        
        # Player chooses placement
        print(f"\nPlayer {self.current_player}'s turn")
        print(f"Tile to place: {tile}")
        print(f"Valid positions: {valid_placements}")
        
        while True:
            try:
                x = int(input("Enter x coordinate: "))
                y = int(input("Enter y coordinate: "))
                rotation = int(input("Enter rotation (0-3): "))
                if (x, y, rotation) in valid_placements:
                    break
            except ValueError:
                pass
            print("Invalid placement. Try again.")
        
        # Place tile
        placed_tile = self.place_tile(x, y, rotation, tile)
        print(f"Placed tile at ({x}, {y}) with rotation {rotation*90}°")
        
        # Check for completed features
        scored = self.check_completed_features(x, y)
        if scored:
            print(f"Scored features: {scored}")
        
        # Place meeple if possible
        if player.meeples > 0:
            features = []
            if any(edge == 'ROAD' for edge in placed_tile.edges.values()):
                features.append('ROAD')
            if any(edge == 'CITY' for edge in placed_tile.edges.values()):
                features.append('CITY')
            if placed_tile.center == 'MONASTERY':
                features.append('MONASTERY')
            
            if features:
                print(f"Available features: {features}")
                place_meeple = input("Place meeple? (y/n): ").lower() == 'y'
                if place_meeple:
                    feature = input(f"Choose feature ({', '.join(features)}): ").upper()
                    if feature in features:
                        success, message = self.place_meeple(self.current_player, x, y, feature)
                        print(message)
                    else:
                        print("Invalid feature")
        
        # Update scores
        for i, p in enumerate(self.players):
            print(f"Player {i} score: {p.score}, Meeples: {p.meeples}")
        
        # Next player
        self.current_player = (self.current_player + 1) % self.num_players
        return True

def main():
    print("Welcome to CLI Carcassonne!")
    print("Rules:")
    print("- Place tiles to build roads, cities and monasteries")
    print("- Place meeples to claim features")
    print("- Complete features to score points")
    print("- First player to place all tiles wins the game\n")
    
    while True:
        try:
            num_players = int(input("Number of players (2-5): "))
            if 2 <= num_players <= 5:
                break
        except ValueError:
            pass
    
    game = CarcassonneGame(num_players)
    
    while game.play_turn():
        pass
    
    # Game over, determine winner
    max_score = max(p.score for p in game.players)
    winners = [i for i, p in enumerate(game.players) if p.score == max_score]
    
    print("\nGame over! Final scores:")
    for i, player in enumerate(game.players):
        print(f"Player {i}: {player.score} points")
    
    if len(winners) == 1:
        print(f"Player {winners[0]} wins!")
    else:
        print(f"Tie between players {', '.join(map(str, winners))}")

if __name__ == "__main__":
    main()
