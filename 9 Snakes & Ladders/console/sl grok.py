import random

class SnakesAndLadders:
    def __init__(self, num_players):
        self.players = [1] * num_players
        self.current_player = 0
        self.snakes = {16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 98: 78}
        self.ladders = {2: 38, 7: 14, 8: 31, 15: 26, 21: 42, 28: 84, 36: 44, 51: 67, 71: 91, 78: 98, 87: 94}
        self.board_size = 100

    def roll_dice(self):
        return random.randint(1, 6)

    def move(self, player, steps):
        new_position = self.players[player] + steps
        if new_position > self.board_size:
            return
        if new_position in self.ladders:
            new_position = self.ladders[new_position]
        elif new_position in self.snakes:
            new_position = self.snakes[new_position]
        self.players[player] = new_position

    def check_win(self, player):
        return self.players[player] == self.board_size

    def play_turn(self):
        player = self.current_player
        roll = self.roll_dice()
        print(f"Игрок {player + 1} выбросил {roll}")
        self.move(player, roll)
        print(f"Игрок {player + 1} переместился на клетку {self.players[player]}")
        if self.check_win(player):
            print(f"Игрок {player + 1} победил!")
            return True
        if roll == 6:
            print("Игрок получает дополнительный ход за выпадение шестерки!")
        else:
            self.current_player = (self.current_player + 1) % len(self.players)
        return False

def main():
    num_players = int(input("Введите количество игроков (2-4): "))
    if num_players < 2 or num_players > 4:
        print("Неверное количество игроков. Должно быть от 2 до 4.")
        return
    game = SnakesAndLadders(num_players)
    while True:
        if game.play_turn():
            break

if __name__ == "__main__":
    main()
