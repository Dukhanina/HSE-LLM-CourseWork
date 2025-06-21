import random

class Domino:
    def __init__(self, side1, side2):
        self.sides = tuple(sorted((side1, side2)))

    def __str__(self):
        return f"[{self.sides[0]}|{self.sides[1]}]"

    def __repr__(self):
        return self.__str__()

    def is_double(self):
        return self.sides[0] == self.sides[1]

    def get_ends(self):
        return self.sides[0], self.sides[1]

class DominoGame:
    def __init__(self, num_players=2, max_pips=6):
        if not (2 <= num_players <= 4):
            raise ValueError("Number of players must be between 2 and 4.")
        self.num_players = num_players
        self.max_pips = max_pips

        self.boneyard = self._create_dominoes()
        self.players = [[] for _ in range(self.num_players)]
        self.table = []
        self.current_player_index = 0
        self.game_over = False
        self.consecutive_passes = 0

    def _create_dominoes(self):
        dominoes = []
        for i in range(self.max_pips + 1):
            for j in range(i, self.max_pips + 1):
                dominoes.append(Domino(i, j))
        random.shuffle(dominoes)
        return dominoes

    def _deal_dominoes(self):
        num_to_deal = 7 if self.num_players == 2 else 5
        for i in range(self.num_players):
            for _ in range(num_to_deal):
                if not self.boneyard:
                    print("Warning: Boneyard empty during dealing, not all players received full hand.")
                    break
                self.players[i].append(self.boneyard.pop(0))

    def _determine_first_player(self):
        starting_tile = None
        player_with_starting_tile = -1
        highest_double_value = -1

        candidates = []
        for p_idx, hand in enumerate(self.players):
            for domino in hand:
                if domino.is_double():
                    if domino.sides[0] > highest_double_value:
                        highest_double_value = domino.sides[0]
                        starting_tile = domino
                        player_with_starting_tile = p_idx
                        candidates = [(p_idx, domino)]
                    elif domino.sides[0] == highest_double_value:
                        candidates.append((p_idx, domino))

        if candidates:
            best_player_idx, best_domino = sorted(candidates, key=lambda x: x[0])[0]
            starting_tile = best_domino
            player_with_starting_tile = best_player_idx

            print(f"Player {player_with_starting_tile + 1} has the highest double ({starting_tile}) and plays first.")
            self.current_player_index = player_with_starting_tile
            self.players[player_with_starting_tile].remove(starting_tile)
            self.table.append(starting_tile)
        else:
            self.current_player_index = random.randint(0, self.num_players - 1)
            if not self.players[self.current_player_index]:
                print("Error: Player hand empty during first player determination. Dealing might have failed.")
                self.game_over = True
                return

            starting_tile = self.players[self.current_player_index].pop(0)
            self.table.append(starting_tile)
            print(f"No doubles among players. Player {self.current_player_index + 1} plays the first domino: {starting_tile}.")

    def start_game(self):
        self.game_over = False
        self.consecutive_passes = 0
        self.boneyard = self._create_dominoes()
        self.players = [[] for _ in range(self.num_players)]
        self.table = []
        
        self._deal_dominoes()
        self._determine_first_player()
        if self.game_over:
            print("Game could not start due to an error during first player determination.")
            return

        print("\n--- Game Started ---")
        self.run_game_loop()

    def _get_table_ends(self):
        if not self.table:
            return None, None
        
        left_end = self.table[0].sides[0]
        right_end = self.table[-1].sides[1]
        
        return left_end, right_end

    def get_playable_dominoes(self, player_hand):
        playable_moves = []
        left_end, right_end = self._get_table_ends()

        if not self.table:
            for i, domino in enumerate(player_hand):
                playable_moves.append((i, 'start', None))
            return playable_moves

        for i, domino in enumerate(player_hand):
            d_side1, d_side2 = domino.get_ends()
            
            if d_side1 == left_end:
                playable_moves.append((i, 'left', d_side1))
            if d_side2 == left_end:
                playable_moves.append((i, 'left', d_side2))
            
            if d_side1 == right_end:
                playable_moves.append((i, 'right', d_side1))
            if d_side2 == right_end:
                playable_moves.append((i, 'right', d_side2))
        
        return playable_moves

    def play_domino(self, player_index, domino_index, side_to_attach):
        player_hand = self.players[player_index]
        
        if not (0 <= domino_index < len(player_hand)):
            print("Error: Invalid domino index received by play_domino function.")
            return False

        domino_to_play = player_hand[domino_index]
        d1, d2 = domino_to_play.get_ends()

        if not self.table:
            self.table.append(domino_to_play)
            player_hand.pop(domino_index)
            print(f"Player {player_index + 1} played {domino_to_play} to start the game.")
            return True

        left_end, right_end = self._get_table_ends()
        valid_move = False
        
        if side_to_attach == 'left':
            if d1 == left_end:
                self.table.insert(0, domino_to_play)
                valid_move = True
            elif d2 == left_end:
                self.table.insert(0, Domino(d2, d1))
                valid_move = True
        elif side_to_attach == 'right':
            if d1 == right_end:
                self.table.append(domino_to_play)
                valid_move = True
            elif d2 == right_end:
                self.table.append(Domino(d2, d1))
                valid_move = True
        
        if valid_move:
            player_hand.pop(domino_index)
            print(f"Player {player_index + 1} played {domino_to_play} on the {side_to_attach} end.")
            self.consecutive_passes = 0
            return True
        else:
            print(f"Internal Error: Failed to play {domino_to_play} on {side_to_attach} end. Does not match {left_end}/{right_end}.")
            return False

    def draw_from_boneyard(self, player_index):
        if not self.boneyard:
            print("Boneyard is empty. Cannot draw.")
            return None
        drawn_domino = self.boneyard.pop(0)
        self.players[player_index].append(drawn_domino)
        print(f"Player {player_index + 1} drew {drawn_domino} from the boneyard.")
        return drawn_domino

    def check_for_winner(self):
        if not self.players[self.current_player_index]:
            self.game_over = True
            print(f"\n--- Player {self.current_player_index + 1} wins the round! ---")
            return True
        return False

    def _handle_blocked_game(self):
        print("\n--- Game Blocked! No player can make a move. ---")
        min_pips = float('inf')
        winner_player_index = -1
        
        pip_counts = []
        for p_idx, hand in enumerate(self.players):
            current_pips = sum(d.sides[0] + d.sides[1] for d in hand)
            pip_counts.append((current_pips, p_idx))
            print(f"Player {p_idx + 1} hand: {hand} (Total pips: {current_pips})")

        sorted_pip_counts = sorted(pip_counts, key=lambda x: x[0])
        min_pips = sorted_pip_counts[0][0]
        
        tied_players = [p_idx for pips, p_idx in sorted_pip_counts if pips == min_pips]

        if len(tied_players) > 1:
            tied_player_nums = [idx + 1 for idx in tied_players]
            print(f"It's a tie among players {tied_player_nums} with {min_pips} pips.")
            winner_player_index = tied_players[0]
        else:
            winner_player_index = sorted_pip_counts[0][1]
            print(f"Player {winner_player_index + 1} wins the round with the lowest pip count of {min_pips}!")
        
        self.game_over = True

    def run_game_loop(self):
        while not self.game_over:
            current_player_hand = self.players[self.current_player_index]
            
            print(f"\n--- Player {self.current_player_index + 1}'s Turn ---")
            print(f"Table: {self.table}")
            left_end, right_end = self._get_table_ends()
            print(f"Open ends: {left_end} | {right_end}")
            print(f"Your hand (Player {self.current_player_index + 1}): {current_player_hand}")
            print(f"Boneyard has {len(self.boneyard)} dominoes.")

            playable_moves = self.get_playable_dominoes(current_player_hand)
            
            if not playable_moves:
                print("No playable dominoes in hand.")
                if self.boneyard:
                    print("Drawing from boneyard...")
                    drawn_count = 0
                    while not playable_moves and self.boneyard:
                        drawn_domino = self.draw_from_boneyard(self.current_player_index)
                        if drawn_domino:
                            drawn_count += 1
                            playable_moves = self.get_playable_dominoes(current_player_hand)
                        else:
                            break
                    
                    if not playable_moves:
                        print("No playable dominoes after drawing.")
                        print("Passing turn.")
                        self.consecutive_passes += 1
                    else:
                        print(f"Drew {drawn_count} domino(es) and now have playable moves.")
                        print(f"Your updated hand (Player {self.current_player_index + 1}): {current_player_hand}")
                        self.consecutive_passes = 0
                else:
                    print("Boneyard is empty. No playable dominoes. Passing turn.")
                    self.consecutive_passes += 1

                if self.consecutive_passes >= self.num_players:
                    self._handle_blocked_game()
                    break

                if not self.game_over:
                    self._next_player_turn()
                continue

            self.consecutive_passes = 0

            while True:
                try:
                    print("Playable options:")
                    if not playable_moves:
                        print("No moves available. This is an error state.")
                        break
                        
                    for idx, (d_idx, side, match_val) in enumerate(playable_moves):
                        domino = current_player_hand[d_idx]
                        if self.table:
                            print(f"{idx}. Play {domino} on {side} end (matching {match_val}).")
                        else:
                            print(f"{idx}. Play {domino} to start the game.")

                    prompt_range = f" (0 to {len(playable_moves)-1})" if len(playable_moves) > 0 else ""
                    choice_input = input(f"Enter the number of the move to make{prompt_range}: ")

                    choice = int(choice_input)

                    if not (0 <= choice < len(playable_moves)):
                        print("Invalid choice. Please enter a valid number within the given range.")
                        continue

                    domino_in_hand_idx, side_to_attach, _ = playable_moves[choice]
                    
                    if self.play_domino(self.current_player_index, domino_in_hand_idx, side_to_attach):
                        break
                    else:
                        print("Failed to play domino. Please re-check your choice or table state.")
                        continue

                except ValueError:
                    print("Invalid input. Please enter a whole number.")
                except IndexError:
                    print("Invalid choice. The index is out of range for playable options. This might indicate an internal error or a race condition if playing multi-threaded.")
                    continue

            if self.check_for_winner():
                break
            
            if not self.game_over:
                self._next_player_turn()

    def _next_player_turn(self):
        self.current_player_index = (self.current_player_index + 1) % self.num_players

def main():
    while True:
        try:
            num_players_input = input("Enter number of players (2-4): ")
            num_players = int(num_players_input)
            if 2 <= num_players <= 4:
                break
            else:
                print("Number of players must be between 2 and 4.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    game = DominoGame(num_players)
    game.start_game()

if __name__ == "__main__":
    main()
