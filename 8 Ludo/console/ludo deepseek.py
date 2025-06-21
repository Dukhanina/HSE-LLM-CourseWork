import random

class Player:
    __slots__ = ('id', 'pawns', 'start_pos', 'home_pos')
    def __init__(self, player_id, start_pos):
        self.id = player_id
        self.pawns = [0] * 4
        self.start_pos = start_pos
        self.home_pos = (start_pos + 52) % 52

class LudoGame:
    def __init__(self, num_players=2):
        self.num_players = num_players
        self.players = []
        start_positions = [0, 13, 26, 39]
        for i in range(num_players):
            self.players.append(Player(i, start_positions[i]))
        self.current_player = 0
        self.game_over = False
        self.consecutive_sixes = 0

    def roll_dice(self):
        return random.randint(1, 6)

    def get_absolute_position(self, player_id, steps):
        return (self.players[player_id].start_pos + steps) % 52

    def is_safe_zone(self, position):
        return position in [0, 13, 26, 39]

    def is_block(self, position):
        for player in self.players:
            count = 0
            for pawn in player.pawns:
                abs_pos = self.get_absolute_position(player.id, pawn)
                if abs_pos == position and pawn < 52:
                    count += 1
            if count >= 2:
                return True
        return False

    def get_available_pawns(self, player_id, dice):
        available = []
        player = self.players[player_id]
        for idx, steps in enumerate(player.pawns):
            if steps == 57:
                continue
            new_steps = steps + dice
            if new_steps > 57:
                continue
            if steps < 52 and new_steps >= 52:
                new_steps = 52 + (new_steps - 52)
            elif steps < 52:
                new_pos = self.get_absolute_position(player_id, new_steps)
                if not self.is_safe_zone(new_pos) and self.is_block(new_pos):
                    continue
            available.append(idx)
        return available

    def move_pawn(self, player_id, pawn_idx, dice):
        player = self.players[player_id]
        old_steps = player.pawns[pawn_idx]
        new_steps = old_steps + dice
        captured = False
        
        if new_steps > 57:
            return False, "Cannot move beyond home"
        
        if old_steps < 52 and new_steps >= 52:
            new_steps = 52 + (new_steps - 52)
        
        player.pawns[pawn_idx] = new_steps
        
        if old_steps < 52 and new_steps < 52:
            new_abs_pos = self.get_absolute_position(player_id, new_steps)
            if not self.is_safe_zone(new_abs_pos) and not self.is_block(new_abs_pos):
                for other_player in self.players:
                    if other_player.id == player_id:
                        continue
                    for other_idx, other_steps in enumerate(other_player.pawns):
                        if other_steps < 52:
                            other_abs = self.get_absolute_position(other_player.id, other_steps)
                            if other_abs == new_abs_pos:
                                other_player.pawns[other_idx] = 0
                                captured = True
                                break
        return True, captured

    def check_win(self, player_id):
        return all(steps == 57 for steps in self.players[player_id].pawns)

    def play_turn(self):
        if self.game_over:
            return
        
        player_id = self.current_player
        player = self.players[player_id]
        dice = self.roll_dice()
        print(f"\nPlayer {player_id} rolled: {dice}")
        
        available_pawns = self.get_available_pawns(player_id, dice)
        if not available_pawns:
            print("No available moves. Turn skipped.")
            self.next_player()
            return
        
        print("Available pawns:", available_pawns)
        while True:
            try:
                pawn_idx = int(input(f"Player {player_id}, choose pawn (0-3): "))
                if pawn_idx in available_pawns:
                    break
            except ValueError:
                pass
            print("Invalid pawn selection. Try again.")
        
        valid, message = self.move_pawn(player_id, pawn_idx, dice)
        if not valid:
            print(message)
            self.next_player()
            return
        
        if isinstance(message, bool) and message:
            print(f"Player {player_id} captured an opponent's pawn!")
        
        if self.check_win(player_id):
            print(f"Player {player_id} wins the game!")
            self.game_over = True
            return
        
        if dice == 6:
            self.consecutive_sixes += 1
            if self.consecutive_sixes == 3:
                print("Three sixes! Turn ends.")
                self.consecutive_sixes = 0
                self.next_player()
            else:
                print("Rolled a 6! Extra turn.")
        else:
            self.consecutive_sixes = 0
            self.next_player()
    
    def next_player(self):
        self.current_player = (self.current_player + 1) % self.num_players

    def display_board(self):
        print("\nCurrent Board:")
        for player in self.players:
            print(f"Player {player.id} pawns:")
            for idx, steps in enumerate(player.pawns):
                if steps == 57:
                    status = "HOME"
                elif steps >= 52:
                    status = f"Home path: {steps-51}"
                else:
                    abs_pos = self.get_absolute_position(player.id, steps)
                    status = f"Position: {abs_pos}"
                print(f"  Pawn {idx}: {status}")

def main():
    print("Welcome to CLI Ludo!")
    print("Rules:")
    print("- 2-4 players, each with 4 pawns")
    print("- Roll dice to move pawns clockwise")
    print("- Land on opponent to send them back to start")
    print("- Form blocks with 2+ pawns on same tile")
    print("- Roll 6 for extra turn (max 2 extra)")
    print("- Three consecutive 6s skips turn")
    print("- First to get all pawns home wins\n")
    
    while True:
        try:
            num_players = int(input("Number of players (2-4): "))
            if 2 <= num_players <= 4:
                break
        except ValueError:
            pass
    
    game = LudoGame(num_players)
    
    while not game.game_over:
        game.display_board()
        game.play_turn()

if __name__ == "__main__":
    main()
