import random

class LudoGame:
    def __init__(self, num_players=2):
        if num_players not in [2, 4]:
            raise ValueError("Number of players must be 2 or 4.")
        self.num_players = num_players
        self.players = []
        self.current_player_idx = 0
        self.game_over = False
        self.consecutive_sixes = 0

        self.TRACK_LENGTH = 52
        self.HOME_PATH_LENGTH = 6
        self.PAWNS_PER_PLAYER = 4

        self.PLAYER_START_POS = [0, 13, 26, 39]
        self.PLAYER_HOME_ENTRY_POS = [51, 12, 25, 38]
        
        self.FIXED_SAFE_ZONES = set([
            0, 13, 26, 39,
            8, 21, 34, 47
        ])
        
        self._init_players()

    def _init_players(self):
        for p_idx in range(self.num_players):
            player_pawns = []
            for i in range(self.PAWNS_PER_PLAYER):
                player_pawns.append({'id': i, 'state': 'nest', 'position': -1, 'player_idx': p_idx})
            self.players.append(player_pawns)

    def roll_dice(self):
        return random.randint(1, 6)

    def _is_safe_position(self, global_pos, checking_player_idx=None):
        if global_pos in self.FIXED_SAFE_ZONES:
            return True
        
        pawns_on_square = []
        for p_idx in range(self.num_players):
            for pawn in self.players[p_idx]:
                if pawn['state'] == 'track' and pawn['position'] == global_pos:
                    pawns_on_square.append(pawn)
        
        if len(pawns_on_square) >= 2:
            first_pawn_owner = pawns_on_square[0]['player_idx']
            if all(pawn['player_idx'] == first_pawn_owner for pawn in pawns_on_square):
                return True
            
        return False

    def get_possible_moves(self, player_idx, roll):
        possible_moves = []
        player_pawns = self.players[player_idx]

        for pawn in player_pawns:
            if pawn['state'] == 'nest':
                if roll == 6:
                    target_pos = self.PLAYER_START_POS[player_idx]
                    
                    pawns_on_target = [
                        p for p_list in self.players 
                        for p in p_list if p['state'] == 'track' and p['position'] == target_pos
                    ]
                    
                    if not (len(pawns_on_target) >= 2 and len(set(p['player_idx'] for p in pawns_on_target)) == 1):
                        possible_moves.append((pawn['id'], 'open', target_pos))
            
            elif pawn['state'] == 'track':
                current_pos = pawn['position']
                player_home_entry = self.PLAYER_HOME_ENTRY_POS[player_idx]
                
                dist_to_home_entry_from_current = (player_home_entry - current_pos + self.TRACK_LENGTH) % self.TRACK_LENGTH
                
                if roll <= dist_to_home_entry_from_current:
                    target_pos = (current_pos + roll) % self.TRACK_LENGTH
                    
                    pawns_on_target = [
                        p for p_list in self.players 
                        for p in p_list if p['state'] == 'track' and p['position'] == target_pos
                    ]
                    if not (len(pawns_on_target) >= 2 and len(set(p['player_idx'] for p in pawns_on_target)) == 1):
                         possible_moves.append((pawn['id'], 'move_on_track', target_pos))
                else:
                    steps_past_entry = roll - dist_to_home_entry_from_current
                    if steps_past_entry <= self.HOME_PATH_LENGTH:
                        target_home_path_idx = steps_past_entry - 1
                        
                        if target_home_path_idx == self.HOME_PATH_LENGTH - 1:
                            possible_moves.append((pawn['id'], 'finish', None))
                        else:
                            possible_moves.append((pawn['id'], 'move_home_path', target_home_path_idx))

            elif pawn['state'] == 'home_path':
                current_home_path_idx = pawn['position']
                remaining_steps = self.HOME_PATH_LENGTH - 1 - current_home_path_idx
                if roll <= remaining_steps:
                    target_home_path_idx = current_home_path_idx + roll
                    if target_home_path_idx == self.HOME_PATH_LENGTH - 1:
                        possible_moves.append((pawn['id'], 'finish', None))
                    else:
                        possible_moves.append((pawn['id'], 'move_home_path', target_home_path_idx))
        
        return possible_moves

    def execute_move(self, player_idx, pawn_id, roll, move_type, target_pos_info):
        pawn = self.players[player_idx][pawn_id]

        if move_type == 'open':
            target_global_pos = self.PLAYER_START_POS[player_idx]
            
            for opp_idx in range(self.num_players):
                if opp_idx == player_idx: continue
                for opp_pawn in self.players[opp_idx]:
                    if opp_pawn['state'] == 'track' and opp_pawn['position'] == target_global_pos:
                        if not self._is_safe_position(target_global_pos, opp_idx):
                            opp_pawn['state'] = 'nest'
                            opp_pawn['position'] = -1
                            print(f"Pawn P{player_idx+1}_{pawn_id+1} captured opponent P{opp_idx+1}_{opp_pawn['id']+1}!")
                            break
            
            pawn['state'] = 'track'
            pawn['position'] = target_global_pos
            print(f"Pawn P{player_idx+1}_{pawn_id+1} opened and moved to {target_global_pos}.")

        elif move_type == 'move_on_track':
            target_global_pos = target_pos_info
            
            for opp_idx in range(self.num_players):
                if opp_idx == player_idx: continue
                for opp_pawn in self.players[opp_idx]:
                    if opp_pawn['state'] == 'track' and opp_pawn['position'] == target_global_pos:
                        if not self._is_safe_position(target_global_pos, opp_idx):
                            opp_pawn['state'] = 'nest'
                            opp_pawn['position'] = -1
                            print(f"Pawn P{player_idx+1}_{pawn_id+1} captured opponent P{opp_idx+1}_{opp_pawn['id']+1}!")
                            break
            
            pawn['state'] = 'track'
            pawn['position'] = target_global_pos
            print(f"Pawn P{player_idx+1}_{pawn_id+1} moved to {target_global_pos}.")

        elif move_type == 'move_home_path':
            pawn['state'] = 'home_path'
            pawn['position'] = target_pos_info
            print(f"Pawn P{player_idx+1}_{pawn_id+1} moved to home path position {target_pos_info+1}.")

        elif move_type == 'finish':
            pawn['state'] = 'finished'
            pawn['position'] = self.HOME_PATH_LENGTH - 1
            print(f"Pawn P{player_idx+1}_{pawn_id+1} reached home!")
        
        self.check_winner()

    def check_winner(self):
        for p_idx, pawns in enumerate(self.players):
            if all(pawn['state'] == 'finished' for pawn in pawns):
                self.game_over = True
                print(f"\n--- Player {p_idx+1} wins the game! ---")
                return True
        return False

    def display_board(self):
        print("\n--- Current Board State ---")
        player_symbols = {0: 'R', 1: 'G', 2: 'Y', 3: 'B'}
        
        track_display = ['_'] * self.TRACK_LENGTH
        for p_idx in range(self.num_players):
            for pawn in self.players[p_idx]:
                if pawn['state'] == 'track':
                    current_content = track_display[pawn['position']]
                    if current_content == '_':
                        track_display[pawn['position']] = player_symbols[p_idx]
                    elif player_symbols[p_idx] not in current_content:
                        track_display[pawn['position']] += player_symbols[p_idx]

        print("Main Track (0-51):")
        print(" ".join(track_display))

        for p_idx in range(self.num_players):
            nest_pawns = [p for p in self.players[p_idx] if p['state'] == 'nest']
            home_path_pawns = [p for p in self.players[p_idx] if p['state'] == 'home_path']
            finished_pawns = [p for p in self.players[p_idx] if p['state'] == 'finished']

            home_path_str = ['_'] * self.HOME_PATH_LENGTH
            for p in home_path_pawns:
                home_path_str[p['position']] = player_symbols[p_idx]
            
            print(f"Player {p_idx+1} ({player_symbols[p_idx]}):")
            print(f"  Nest: {len(nest_pawns)} pawns")
            print(f"  Home Path ({player_symbols[p_idx]}): {' '.join(home_path_str)}")
            print(f"  Finished: {len(finished_pawns)} pawns")
        print("--------------------------")

    def _next_player_turn(self):
        self.current_player_idx = (self.current_player_idx + 1) % self.num_players

    def run_game(self):
        while not self.game_over:
            current_player_pawns = self.players[self.current_player_idx]
            player_symbol = {0: 'Red', 1: 'Green', 2: 'Yellow', 3: 'Blue'}[self.current_player_idx]

            self.display_board()
            print(f"\nPlayer {self.current_player_idx+1}'s ({player_symbol}) turn.")
            input("Press Enter to roll the dice...")
            
            roll = self.roll_dice()
            print(f"Player {self.current_player_idx+1} rolled a {roll}.")

            if roll == 6:
                self.consecutive_sixes += 1
                if self.consecutive_sixes == 3:
                    print(f"Player {self.current_player_idx+1} rolled three 6s! Turn lost.")
                    self.consecutive_sixes = 0
                    self._next_player_turn()
                    continue
            else:
                self.consecutive_sixes = 0

            possible_moves = self.get_possible_moves(self.current_player_idx, roll)

            if not possible_moves:
                print(f"No possible moves for Player {self.current_player_idx+1}. Passing turn.")
                if roll != 6:
                    self._next_player_turn()
                continue

            while True:
                print("Possible moves:")
                for i, move in enumerate(possible_moves):
                    pawn_id, move_type, target_pos_info = move
                    pawn_desc = f"Pawn {pawn_id+1}"
                    if move_type == 'open':
                        print(f"{i}: {pawn_desc} from nest to start.")
                    elif move_type == 'move_on_track':
                        print(f"{i}: {pawn_desc} from {self.players[self.current_player_idx][pawn_id]['position']} to {target_pos_info} (on main track).")
                    elif move_type == 'move_home_path':
                        print(f"{i}: {pawn_desc} to home path position {target_pos_info+1}.")
                    elif move_type == 'finish':
                        print(f"{i}: {pawn_desc} to finish home.")
                
                try:
                    choice = int(input("Enter the number of the move you want to make: "))
                    if 0 <= choice < len(possible_moves):
                        chosen_move = possible_moves[choice]
                        pawn_id, move_type, target_pos_info = chosen_move
                        self.execute_move(self.current_player_idx, pawn_id, roll, move_type, target_pos_info)
                        break
                    else:
                        print("Invalid choice. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            
            if self.game_over:
                break

            if roll != 6:
                self._next_player_turn()

def main():
    while True:
        try:
            num_players_input = input("Enter number of players (2 or 4): ")
            num_players = int(num_players_input)
            if num_players in [2, 4]:
                break
            else:
                print("Invalid number of players. Please enter 2 or 4.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    game = LudoGame(num_players)
    game.run_game()

if __name__ == "__main__":
    main()
