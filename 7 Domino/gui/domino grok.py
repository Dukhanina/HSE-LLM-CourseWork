import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
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

    def get_current_player(self):
        return self.current_player

    def get_player_dominoes(self, player):
        return self.players[player]

    def get_board_str(self):
        return " ".join(str(d) for d in self.board)

    def has_possible_moves(self, player):
        if not self.board:
            return True
        left_end = self.board[0].left
        right_end = self.board[-1].right
        for domino in self.players[player]:
            if domino.left == left_end or domino.right == left_end or domino.left == right_end or domino.right == right_end:
                return True
        return False

    def play_domino(self, domino, position):
        try:
            if not self.board:
                self.board.append(domino)
            elif position == "left":
                if domino.right == self.board[0].left:
                    self.board.insert(0, domino)
                elif domino.left == self.board[0].left:
                    flipped = Domino(domino.right, domino.left)
                    self.board.insert(0, flipped)
                else:
                    return False
            elif position == "right":
                if domino.left == self.board[-1].right:
                    self.board.append(domino)
                elif domino.right == self.board[-1].right:
                    flipped = Domino(domino.right, domino.left)
                    self.board.append(flipped)
                else:
                    return False
            self.players[self.current_player].remove(domino)
            return True
        except ValueError:
            return False

class DominoGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Domino Game")

        # Кнопка "Новая игра"
        self.new_game_btn = tk.Button(self.root, text="Новая игра", command=self.new_game)
        self.new_game_btn.pack()

        # Метка для текущего игрока
        self.turn_label = tk.Label(self.root, text="Нажмите 'Новая игра' для начала")
        self.turn_label.pack()

        # Текстовое поле для логов с прокруткой
        self.log_text = tk.Text(self.root, height=10, width=50)
        self.log_text.pack()
        self.log_scroll = tk.Scrollbar(self.root, command=self.log_text.yview)
        self.log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=self.log_scroll.set)

        # Фрейм для ввода хода
        self.move_frame = tk.Frame(self.root)
        self.move_frame.pack()

        tk.Label(self.move_frame, text="Ваши домино:").pack(side=tk.LEFT)
        self.domino_combo = ttk.Combobox(self.move_frame, state="readonly")
        self.domino_combo.pack(side=tk.LEFT)

        tk.Label(self.move_frame, text="Позиция:").pack(side=tk.LEFT)
        self.position_var = tk.StringVar(value="right")
        self.left_radio = tk.Radiobutton(self.move_frame, text="Слева", variable=self.position_var, value="left")
        self.left_radio.pack(side=tk.LEFT)
        self.right_radio = tk.Radiobutton(self.move_frame, text="Справа", variable=self.position_var, value="right")
        self.right_radio.pack(side=tk.LEFT)

        self.play_btn = tk.Button(self.move_frame, text="Сыграть", command=self.play_move)
        self.play_btn.pack(side=tk.LEFT)

        self.game = None

    def new_game(self):
        while True:
            num_players = tk.simpledialog.askinteger("Количество игроков", "Введите число игроков (2-4):", minvalue=2, maxvalue=4)
            if num_players is not None:
                break
            messagebox.showerror("Неверный ввод", "Число игроков должно быть от 2 до 4")
        self.game = DominoGame(num_players)
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, f"Игра началась с {num_players} игроками\n")
        self.update_gui()

    def update_gui(self):
        if self.game is None:
            self.turn_label.config(text="Нажмите 'Новая игра' для начала")
            self.domino_combo.config(values=[])
            self.play_btn.config(state=tk.DISABLED)
            return

        current_player = self.game.get_current_player()
        self.turn_label.config(text=f"Ход игрока {current_player}")

        # Обновление логов с текущей доской
        board_str = "Доска: " + self.game.get_board_str()
        self.log_text.insert(tk.END, board_str + "\n")

        # Проверка на возможные ходы
        if not self.game.has_possible_moves(current_player):
            self.log_text.insert(tk.END, f"Игрок {current_player} не имеет ходов, пропуск\n")
            self.game.passes += 1
            if self.game.passes == self.game.num_players:
                self.end_game_blocked()
            else:
                self.game.current_player = (self.game.current_player + 1) % self.game.num_players
                self.update_gui()
            return

        # Обновление выпадающего списка домино
        dominoes = self.game.get_player_dominoes(current_player)
        domino_strs = [str(d) for d in dominoes]
        self.domino_combo.config(values=domino_strs)
        if domino_strs:
            self.domino_combo.current(0)
        self.play_btn.config(state=tk.NORMAL)

    def play_move(self):
        if self.game is None:
            return
        current_player = self.game.get_current_player()
        dominoes = self.game.get_player_dominoes(current_player)
        selected_index = self.domino_combo.current()
        if selected_index < 0:
            messagebox.showerror("Неверный выбор", "Пожалуйста, выберите домино")
            return
        domino = dominoes[selected_index]
        position = self.position_var.get()
        success = self.game.play_domino(domino, position)
        if success:
            self.log_text.insert(tk.END, f"Игрок {current_player} сыграл {str(domino)} {position}\n")
            self.game.passes = 0
            if not self.game.players[current_player]:
                self.end_game_winner(current_player)
            else:
                self.game.current_player = (self.game.current_player + 1) % self.game.num_players
                self.update_gui()
        else:
            messagebox.showerror("Недопустимый ход", "Этот ход не разрешен")

    def end_game_winner(self, winner):
        messagebox.showinfo("Конец игры", f"Игрок {winner} победил!")
        self.game = None
        self.update_gui()

    def end_game_blocked(self):
        dot_counts = [sum(d.dot_count() for d in player) for player in self.game.players]
        min_count = min(dot_counts)
        winners = [i for i, count in enumerate(dot_counts) if count == min_count]
        if len(winners) == 1:
            messagebox.showinfo("Конец игры", f"Игра заблокирована. Игрок {winners[0]} победил с наименьшим числом очков {min_count}")
        else:
            winners_str = ", ".join(map(str, winners))
            messagebox.showinfo("Конец игры", f"Игра заблокирована. Ничья между игроками {winners_str} с числом очков {min_count}")
        self.game = None
        self.update_gui()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = DominoGUI()
    gui.run()
