import tkinter as tk
from tkinter import messagebox
import random

class Game:
    def __init__(self):
        self.current_player = 1
        self.positions = {1: 0, 2: 0}  # Позиции игроков

    def roll_dice(self):
        return random.randint(1, 6)

    def move_player(self, player, steps):
        self.positions[player] += steps
        if self.positions[player] == 100:  # Условие победы (пример)
            return True
        return False

class GameGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Простая игра")
        self.game = None

        # Интерфейс
        self.label = tk.Label(self.root, text="Нажмите 'Новая игра' для начала")
        self.label.pack()

        self.new_game_btn = tk.Button(self.root, text="Новая игра", command=self.new_game)
        self.new_game_btn.pack()

        self.roll_btn = tk.Button(self.root, text="Бросить кубик", command=self.make_move, state="disabled")
        self.roll_btn.pack()

        self.log = tk.Text(self.root, height=10, width=50)
        self.log.pack()

    def new_game(self):
        self.game = Game()
        self.roll_btn.config(state="normal")
        self.new_game_btn.config(state="disabled")
        self.log.delete(1.0, tk.END)
        self.log.insert(tk.END, "Игра началась! Текущий игрок: 1\n")
        self.label.config(text="Текущий игрок: 1")

    def make_move(self):
        if not self.game:
            return

        roll = self.game.roll_dice()
        self.log.insert(tk.END, f"Игрок {self.game.current_player} выбросил {roll}\n")
        
        if self.game.move_player(self.game.current_player, roll):
            messagebox.showinfo("Победа!", f"Игрок {self.game.current_player} победил!")
            self.reset_game()
            return

        # Смена игрока
        self.game.current_player = 2 if self.game.current_player == 1 else 1
        self.label.config(text=f"Текущий игрок: {self.game.current_player}")

    def reset_game(self):
        self.roll_btn.config(state="disabled")
        self.new_game_btn.config(state="normal")
        self.label.config(text="Нажмите 'Новая игра' для начала")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = GameGUI()
    gui.run()
