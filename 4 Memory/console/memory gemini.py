import random

class MemoryGame:
    def __init__(self, pairs=8):
        self.cards = self._create_cards(pairs)
        self.board = ['*' for _ in range(len(self.cards))]
        self.matched_pairs = 0
        self.player_scores = {}
        self.current_player_index = 0
        self.players = []

    def _create_cards(self, pairs):
        values = [str(i) for i in range(1, pairs + 1)]
        cards = (values * 2)
        random.shuffle(cards)
        return cards

    def add_player(self, player_name):
        self.players.append(player_name)
        self.player_scores[player_name] = 0

    def display_board(self):
        print("\n" + " ".join(self.board))
        print("Indices: " + " ".join([str(i) for i in range(len(self.board))]))

    def is_game_over(self):
        return self.matched_pairs == len(self.cards) // 2

    def get_current_player(self):
        return self.players[self.current_player_index]

    def switch_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def player_turn(self, player_name):
        print(f"\n{player_name}'s turn.")
        self.display_board()

        first_card_index = self._get_valid_input("Enter index of first card to flip: ")
        self.board[first_card_index] = self.cards[first_card_index]
        self.display_board()

        second_card_index = self._get_valid_input("Enter index of second card to flip: ", first_card_index)
        self.board[second_card_index] = self.cards[second_card_index]
        self.display_board()

        if self.cards[first_card_index] == self.cards[second_card_index]:
            print("Match found!")
            self.matched_pairs += 1
            self.player_scores[player_name] += 1
        else:
            print("No match. Cards will be flipped back.")
            input("Press Enter to continue...")
            self.board[first_card_index] = '*'
            self.board[second_card_index] = '*'
            self.switch_player()

    def _get_valid_input(self, prompt, exclude_index=None):
        while True:
            try:
                index = int(input(prompt))
                if not (0 <= index < len(self.cards)):
                    print("Invalid index. Please enter a number within the board range.")
                elif self.board[index] != '*':
                    print("This card is already matched or flipped. Choose another.")
                elif index == exclude_index:
                    print("You selected the same card twice. Choose a different card.")
                else:
                    return index
            except ValueError:
                print("Invalid input. Please enter a number.")

    def determine_winner(self):
        if not self.player_scores:
            print("No players in the game.")
            return

        highest_score = -1
        winners = []

        for player, score in self.player_scores.items():
            if score > highest_score:
                highest_score = score
                winners = [player]
            elif score == highest_score:
                winners.append(player)

        if highest_score == 0:
            print("No pairs were matched. It's a draw!")
        elif len(winners) > 1:
            print(f"It's a tie! Winners: {', '.join(winners)} with {highest_score} pairs.")
        else:
            print(f"The winner is {winners[0]} with {highest_score} pairs!")

def main():
    num_players = 0
    while num_players < 1:
        try:
            num_players = int(input("Enter number of players: "))
            if num_players < 1:
                print("Please enter at least 1 player.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    player_names = []
    for i in range(num_players):
        name = input(f"Enter name for player {i+1}: ")
        player_names.append(name)

    game = MemoryGame()
    for name in player_names:
        game.add_player(name)

    print("Welcome to Memory Game!")
    print("Instructions:")
    print("1. Mix up the cards (done automatically).")
    print("2. Place each card upside down on the table or floor in rows (represented by '*' on board).")
    print("3. Each player will take turns flipping over two cards.")
    print("4. If the two cards match, the player will keep the cards and get another turn.")
    print("5. If they don't match, flip them back over in the same spot.")
    print("6. The goal is to watch closely and remember where the cards are.")
    print("7. Whoever has the most pairs at the end, wins!")

    while not game.is_game_over():
        current_player = game.get_current_player()
        game.player_turn(current_player)

    print("\nGame Over!")
    game.determine_winner()

if __name__ == "__main__":
    main()
