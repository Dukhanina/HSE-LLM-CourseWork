import random

class Domino:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return f"[{self.left}|{self.right}]"

    def dot_count(self):
        return self.left + self.right

class DominoGame:
    def __init__(self, num_players):
        self.num_players = num_players
        self.players = [[] for _ in range(num_players)]
        self.boneyard = []
        self.board = []
        self.current_player = 0
        self.passes = 0
        self.create_dominoes()
        self.shuffle_dominoes()
        self.deal_dominoes()

    def create_dominoes(self):
        for i in range(7):
            for j in range(i, 7):
                self.boneyard.append(Domino(i, j))

    def shuffle_dominoes(self):
        random.shuffle(self.boneyard)

    def deal_dominoes(self):
        tiles_per_player = 7 if self.num_players == 2 else 5
        for _ in range(tiles_per_player):
            for player in self.players:
                player.append(self.boneyard.pop())

    def can_play(self, domino):
        if not self.board:
            return True
        left_end = self.board[0].left
        right_end = self.board[-1].right
        return domino.left == left_end or domino.right == left_end or domino.left == right_end or domino.right == right_end

    def is_valid_move(self, domino, position):
        if not self.board:
            return True
        if position == "left":
            return domino.left == self.board[0].left or domino.right == self.board[0].left
        if position == "right":
            return domino.left == self.board[-1].right or domino.right == self.board[-1].right
        return False

    def play_domino(self, domino, position):
        if not self.board:
            self.board.append(domino)
        elif position == "left":
            if domino.right == self.board[0].left:
                self.board.insert(0, domino)
            elif domino.left == self.board[0].left:
                flipped = Domino(domino.right, domino.left)
                self.board.insert(0, flipped)
            else:
                raise ValueError("Invalid move")
        elif position == "right":
            if domino.left == self.board[-1].right:
                self.board.append(domino)
            elif domino.right == self.board[-1].right:
                flipped = Domino(domino.left, domino.right)
                self.board.append(flipped)
            else:
                raise ValueError("Invalid move")
        self.players[self.current_player].remove(domino)

    def player_turn(self):
        print(f"Player {self.current_player}'s turn")
        print(f"Board: {' '.join(str(d) for d in self.board)}")
        print(f"Your dominoes: {' '.join(str(d) for d in self.players[self.current_player])}")
        if not self.board:
            print("Board is empty, play any domino")
            while True:
                try:
                    index = int(input("Enter domino index to play: "))
                    domino = self.players[self.current_player][index]
                    self.play_domino(domino, None)
                    self.passes = 0
                    return True
                except (ValueError, IndexError):
                    print("Invalid input")
        else:
            possible_moves = []
            left_end = self.board[0].left
            right_end = self.board[-1].right
            for i, domino in enumerate(self.players[self.current_player]):
                if domino.left == left_end or domino.right == left_end:
                    possible_moves.append((i, "left"))
                if domino.left == right_end or domino.right == right_end:
                    possible_moves.append((i, "right"))
            if not possible_moves:
                print("No playable dominoes, passing turn")
                self.passes += 1
                return False
            print("Possible moves:")
            for move in possible_moves:
                print(f"- {move[0]} on {move[1]}")
            while True:
                try:
                    choice = input("Enter domino index and position (e.g., '0 left'): ").split()
                    if len(choice) != 2:
                        raise ValueError
                    index = int(choice[0])
                    position = choice[1].lower()
                    if position not in ["left", "right"]:
                        raise ValueError
                    domino = self.players[self.current_player][index]
                    if (index, position) not in possible_moves:
                        print("Invalid move")
                        continue
                    self.play_domino(domino, position)
                    self.passes = 0
                    return True
                except (ValueError, IndexError):
                    print("Invalid input")

    def play(self):
        while True:
            if not self.players[self.current_player]:
                print(f"Player {self.current_player} wins!")
                return
            if self.player_turn():
                self.passes = 0
            else:
                self.passes += 1
            if self.passes == self.num_players:
                print("Game is blocked")
                dot_counts = [sum(d.dot_count() for d in player) for player in self.players]
                min_count = min(dot_counts)
                winners = [i for i, count in enumerate(dot_counts) if count == min_count]
                if len(winners) == 1:
                    print(f"Player {winners[0]} wins with the lowest dot count {min_count}")
                else:
                    print(f"Tie between players {', '.join(map(str, winners))} with dot count {min_count}")
                return
            self.current_player = (self.current_player + 1) % self.num_players

def main():
    num_players = int(input("Enter number of players (2-4): "))
    if num_players < 2 or num_players > 4:
        print("Number of players must be between 2 and 4")
        return
    game = DominoGame(num_players)
    game.play()

if __name__ == "__main__":
    main()
