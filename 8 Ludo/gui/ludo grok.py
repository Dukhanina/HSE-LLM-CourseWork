import random
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class LudoGame:
    def __init__(self, num_players):
        self.num_players = num_players
        self.board = [[] for _ in range(52)]  # Основная доска с 52 клетками
        self.home_zones = [[] for _ in range(num_players)]  # Домашние зоны
        self.players = [[-1, -1, -1, -1] for _ in range(num_players)]  # -1: в стартовой зоне
        self.current_player = 0
        self.consecutive_sixes = 0
        self.start_positions = [0, 13, 26, 39]  # Начальные позиции игроков
        self.last_roll = 0

    def roll_dice(self):
        roll = random.randint(1, 6)
        self.last_roll = roll
        if roll == 6:
            self.consecutive_sixes += 1
        else:
            self.consecutive_sixes = 0
        return roll

    def can_move(self, player, pawn, steps):
        pos = self.players[player][pawn]
        if pos == -1 and steps == 6:  # Вывод пешки только при 6
            start_pos = self.start_positions[player]
            if self.board[start_pos]:
                opp_player, _ = self.board[start_pos]
                if opp_player == player:
                    return False  # Нельзя занять свою пешку
            return True
        elif pos == -1:
            return False
        elif pos >= 52:  # В домашней зоне
            new_pos = pos + steps
            return new_pos <= 58 and all(new_pos - 52 != p for p in self.home_zones[player])
        else:  # На доске
            new_pos = (pos + steps) % 52
            if new_pos >= 52:
                new_pos = 52 + (new_pos - 52)
                return new_pos <= 58
            if self.board[new_pos]:
                opp_player, _ = self.board[new_pos]
                if opp_player == player:
                    return False  # Нельзя занять свою пешку
            return True

    def move_pawn(self, player, pawn, steps):
        pos = self.players[player][pawn]
        if pos == -1:  # Вывод из стартовой зоны
            start_pos = self.start_positions[player]
            if self.board[start_pos]:
                opp_player, opp_pawn = self.board[start_pos]
                if opp_player != player:
                    self.players[opp_player][opp_pawn] = -1
                    self.board[start_pos] = []
            self.board[start_pos] = (player, pawn)
            self.players[player][pawn] = start_pos
        elif pos >= 52:  # Движение в домашней зоне
            new_pos = pos + steps
            if new_pos == 58:  # Достиг конца
                self.home_zones[player].append(6)
                self.players[player][pawn] = -1
            else:
                self.players[player][pawn] = new_pos
        else:  # Движение по доске
            new_pos = (pos + steps) % 52
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
        return len(self.home_zones[player]) == 4

    def get_movable_pawns(self, player, roll):
        return [i for i, pos in enumerate(self.players[player]) if self.can_move(player, i, roll)]

    def get_board_state(self):
        state = []
        for i, cell in enumerate(self.board):
            if cell:
                state.append(f"Позиция {i}: Игрок {cell[0] + 1}, Пешка {cell[1] + 1}")
            else:
                state.append(f"Позиция {i}: Пусто")
        for player in range(self.num_players):
            pawns = [f"Пешка {i + 1}: {'Старт' if pos == -1 else f'Поз.{pos}' if pos < 52 else f'Дом {pos - 52}'}" 
                     for i, pos in enumerate(self.players[player])]
            state.append(f"Игрок {player + 1}: {', '.join(pawns)}")
            state.append(f"Дом игрока {player + 1}: {len(self.home_zones[player])} пешек")
        return "\n".join(state)

class LudoGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ludo Game")
        self.game = None

        # Кнопка "Новая игра"
        self.new_game_btn = tk.Button(self.root, text="Новая игра", command=self.new_game)
        self.new_game_btn.pack(pady=5)

        # Метка текущего игрока
        self.turn_label = tk.Label(self.root, text="Нажмите 'Новая игра' для начала")
        self.turn_label.pack()

        # Кнопка броска кубика
        self.roll_btn = tk.Button(self.root, text="Бросить кубик", command=self.roll_dice, state=tk.DISABLED)
        self.roll_btn.pack(pady=5)

        # Текстовое поле логов
        self.log_text = tk.Text(self.root, height=15, width=60)
        self.log_text.pack(pady=5)
        self.log_scroll = tk.Scrollbar(self.root, command=self.log_text.yview)
        self.log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=self.log_scroll.set)

        # Фрейм для ввода хода
        self.move_frame = tk.Frame(self.root)
        self.move_frame.pack(pady=5)
        tk.Label(self.move_frame, text="Выберите пешку:").pack(side=tk.LEFT)
        self.pawn_combo = ttk.Combobox(self.move_frame, state="readonly", width=10)
        self.pawn_combo.pack(side=tk.LEFT, padx=5)
        self.move_btn = tk.Button(self.move_frame, text="Ход", command=self.make_move, state=tk.DISABLED)
        self.move_btn.pack(side=tk.LEFT)

    def new_game(self):
        num_players = simpledialog.askinteger("Игроки", "Введите количество игроков (2-4):", minvalue=2, maxvalue=4)
        if num_players is None:
            return
        self.game = LudoGame(num_players)
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, f"Начата новая игра с {num_players} игроками\n")
        self.roll_btn.config(state=tk.NORMAL)
        self.update_gui()

    def roll_dice(self):
        if not self.game:
            return
        roll = self.game.roll_dice()
        self.log_text.insert(tk.END, f"Игрок {self.game.current_player + 1} выбросил {roll}\n")
        if self.game.consecutive_sixes == 3:
            self.log_text.insert(tk.END, "Три шестерки подряд! Ход пропущен.\n")
            self.game.consecutive_sixes = 0
            self.game.current_player = (self.game.current_player + 1) % self.game.num_players
            self.update_gui()
            return
        movable_pawns = self.game.get_movable_pawns(self.game.current_player, roll)
        if not movable_pawns:
            self.log_text.insert(tk.END, "Нет доступных ходов. Ход переходит следующему игроку.\n")
            self.game.current_player = (self.game.current_player + 1) % self.game.num_players
            self.update_gui()
            return
        self.pawn_combo.config(values=[f"Пешка {i + 1}" for i in movable_pawns])
        self.pawn_combo.current(0)
        self.move_btn.config(state=tk.NORMAL)
        self.roll_btn.config(state=tk.DISABLED)

    def make_move(self):
        if not self.game:
            return
        selected = self.pawn_combo.get()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите пешку")
            return
        pawn_idx = int(selected.split()[1]) - 1
        if not self.game.can_move(self.game.current_player, pawn_idx, self.game.last_roll):
            messagebox.showerror("Недопустимый ход", "Этот ход невозможен")
            return
        self.game.move_pawn(self.game.current_player, pawn_idx, self.game.last_roll)
        self.log_text.insert(tk.END, f"Игрок {self.game.current_player + 1} переместил пешку {pawn_idx + 1}\n")
        self.log_text.insert(tk.END, self.game.get_board_state() + "\n")
        if self.game.check_win(self.game.current_player):
            messagebox.showinfo("Победа", f"Игрок {self.game.current_player + 1} победил!")
            self.game = None
            self.update_gui()
            return
        if self.game.last_roll != 6:
            self.game.current_player = (self.game.current_player + 1) % self.game.num_players
        self.update_gui()

    def update_gui(self):
        if not self.game:
            self.turn_label.config(text="Нажмите 'Новая игра' для начала")
            self.roll_btn.config(state=tk.DISABLED)
            self.move_btn.config(state=tk.DISABLED)
            self.pawn_combo.config(values=[])
            return
        self.turn_label.config(text=f"Ход игрока {self.game.current_player + 1}")
        self.move_btn.config(state=tk.DISABLED)
        self.roll_btn.config(state=tk.NORMAL)
        self.pawn_combo.config(values=[])

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = LudoGUI()
    gui.run()
