import random

class LudoGame:
    def __init__(self, num_players):
        self.num_players = num_players
        self.board = [[] for _ in range(52)]  # Основная доска с 52 клетками
        self.home_zones = [[] for _ in range(num_players)]  # Домашние зоны игроков
        self.players = [[-1, -1, -1, -1] for _ in range(num_players)]  # -1 означает в стартовой зоне
        self.current_player = 0
        self.consecutive_sixes = 0
        self.start_positions = [0, 13, 26, 39]  # Начальные позиции для каждого игрока

    def roll_dice(self):
        roll = random.randint(1, 6)
        if roll == 6:
            self.consecutive_sixes += 1
        else:
            self.consecutive_sixes = 0
        return roll

    def can_move(self, player, pawn, steps):
        pos = self.players[player][pawn]
        if pos == -1 and steps == 6:  # Вывод пешки из стартовой зоны только при 6
            return True
        elif pos == -1:  # Если не 6, пешку нельзя вывести
            return False
        elif pos >= 52:  # В домашней зоне
            new_pos = pos + steps
            return new_pos <= 58 and all(new_pos - 52 != p for p in self.home_zones[player])
        else:  # На доске
            new_pos = (pos + steps)
            if new_pos >= 52:  # Переход в домашнюю зону
                return new_pos <= 58
            return True

    def move_pawn(self, player, pawn, steps):
        pos = self.players[player][pawn]
        if pos == -1:  # Вывод из стартовой зоны
            start_pos = self.start_positions[player]
            if self.board[start_pos]:
                opp_player, opp_pawn = self.board[start_pos]
                if opp_player != player:
                    self.players[opp_player][opp_pawn] = -1
            self.board[start_pos] = (player, pawn)
            self.players[player][pawn] = start_pos
        elif pos >= 52:  # Движение в домашней зоне
            new_pos = pos + steps
            if new_pos == 58:  # Пешка достигла конца домашней зоны
                self.home_zones[player].append(6)
                self.players[player][pawn] = -1
            else:
                self.players[player][pawn] = new_pos
        else:  # Движение по доске
            new_pos = pos + steps
            self.board[pos] = []  # Очищаем текущую позицию
            if new_pos >= 52:  # Вход в домашнюю зону
                self.players[player][pawn] = new_pos
            else:
                if self.board[new_pos]:
                    opp_player, opp_pawn = self.board[new_pos]
                    if opp_player != player:
                        self.players[opp_player][opp_pawn] = -1
                self.board[new_pos] = (player, pawn)
                self.players[player][pawn] = new_pos

    def check_win(self, player):
        return len(self.home_zones[player]) == 4  # Победа, если все 4 пешки в домашней зоне

    def play_turn(self):
        player = self.current_player
        roll = self.roll_dice()
        print(f"Игрок {player + 1} выбросил {roll}")
        if self.consecutive_sixes == 3:
            print("Три шестерки подряд! Ход пропущен.")
            self.consecutive_sixes = 0
            self.current_player = (self.current_player + 1) % self.num_players
            return False
        movable_pawns = [i for i, pos in enumerate(self.players[player]) if self.can_move(player, i, roll)]
        if not movable_pawns:
            print("Нет доступных пешек для хода.")
            self.current_player = (self.current_player + 1) % self.num_players
            return False
        pawn = random.choice(movable_pawns)
        print(f"Двигаем пешку {pawn + 1}")
        self.move_pawn(player, pawn, roll)
        if self.check_win(player):
            print(f"Игрок {player + 1} победил!")
            return True
        if roll != 6:
            self.current_player = (self.current_player + 1) % self.num_players
        return False

    def print_board(self):
        print("Состояние доски:")
        for i, cell in enumerate(self.board):
            if cell:
                print(f"Позиция {i}: Игрок {cell[0] + 1}, Пешка {cell[1] + 1}")
            else:
                print(f"Позиция {i}: Пусто")
        for player in range(self.num_players):
            print(f"Пешки игрока {player + 1}: {self.players[player]}")
            print(f"Домашняя зона игрока {player + 1}: {self.home_zones[player]}")

def main():
    num_players = int(input("Введите количество игроков (2-4): "))
    if num_players < 2 or num_players > 4:
        print("Неверное количество игроков.")
        return
    game = LudoGame(num_players)
    while True:
        game.print_board()
        if game.play_turn():
            break

if __name__ == "__main__":
    main()
