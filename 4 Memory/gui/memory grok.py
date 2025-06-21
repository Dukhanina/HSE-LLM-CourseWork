import tkinter as tk
from tkinter import messagebox
import random

class MemoryGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Memory Game")
        
        # Создание виджетов
        self.log_text = tk.Text(self, height=10, width=30, state='disabled')
        self.log_text.pack(pady=5)
        
        self.current_player_label = tk.Label(self, text="Player 1's turn")
        self.current_player_label.pack(pady=5)
        
        self.entry = tk.Entry(self)
        self.entry.pack(pady=5)
        
        self.move_button = tk.Button(self, text="Make Move", command=self.make_move)
        self.move_button.pack(pady=5)
        
        self.new_game_button = tk.Button(self, text="New Game", command=self.new_game)
        self.new_game_button.pack(pady=5)
        
        # Инициализация новой игры
        self.new_game()

    def create_board(self):
        """Создание игрового поля"""
        size = self.size
        cards = list(range(1, size * size // 2 + 1)) * 2
        random.shuffle(cards)
        board = [cards[i:i + size] for i in range(0, len(cards), size)]
        revealed = [[False] * size for _ in range(size)]
        return board, revealed

    def print_board(self):
        """Отображение игрового поля в текстовом поле"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        for i in range(self.size):
            for j in range(self.size):
                if self.revealed[i][j]:
                    self.log_text.insert(tk.END, f"{self.board[i][j]:2} ")
                else:
                    self.log_text.insert(tk.END, " X ")
            self.log_text.insert(tk.END, "\n")
        self.log_text.config(state='disabled')

    def make_move(self):
        """Обработка хода игрока"""
        if self.game_over:
            messagebox.showinfo("Game Over", "Игра окончена. Начните новую игру.")
            return
        
        move = self.entry.get().strip()
        self.entry.delete(0, tk.END)
        
        try:
            row, col = map(int, move.split())
            row -= 1  # Перевод в индексы, начинающиеся с 0
            col -= 1
            if row < 0 or col < 0 or row >= self.size or col >= self.size:
                raise ValueError
        except (ValueError, IndexError):
            messagebox.showerror("Недопустимый ход", f"Введите два числа от 1 до {self.size}, разделённых пробелом.")
            return
        
        if self.revealed[row][col]:
            messagebox.showerror("Недопустимый ход", "Эта карта уже открыта. Выберите другую.")
            return
        
        if self.first_card is None:
            # Первый ход: открываем первую карту
            self.first_card = (row, col)
            self.revealed[row][col] = True
            self.print_board()
        else:
            # Второй ход: открываем вторую карту
            second_card = (row, col)
            if second_card == self.first_card:
                messagebox.showerror("Недопустимый ход", "Нельзя выбрать одну и ту же карту дважды.")
                self.revealed[self.first_card[0]][self.first_card[1]] = False
                self.first_card = None
                return
            
            self.revealed[row][col] = True
            self.print_board()
            
            # Проверка совпадения
            if self.board[self.first_card[0]][self.first_card[1]] == self.board[row][col]:
                messagebox.showinfo("Совпадение", "Пара найдена!")
                if self.current_player == 1:
                    self.player1_score += 1
                else:
                    self.player2_score += 1
                if self.player1_score + self.player2_score == self.pairs:
                    self.end_game()
                self.first_card = None
            else:
                messagebox.showinfo("Нет совпадения", "Пары нет. Ход следующего игрока.")
                self.revealed[self.first_card[0]][self.first_card[1]] = False
                self.revealed[row][col] = False
                self.current_player = 2 if self.current_player == 1 else 1
                self.current_player_label.config(text=f"Player {self.current_player}'s turn")
                self.first_card = None
                self.print_board()

    def end_game(self):
        """Завершение игры и объявление победителя"""
        self.game_over = True
        self.move_button.config(state='disabled')
        if self.player1_score > self.player2_score:
            winner = "Player 1"
        elif self.player2_score > self.player1_score:
            winner = "Player 2"
        else:
            winner = "Ничья"
        messagebox.showinfo("Игра окончена", f"Игра окончена! {winner} победил с счётом {self.player1_score} против {self.player2_score}.")

    def new_game(self):
        """Запуск новой игры"""
        self.size = 4  # Размер поля 4x4
        self.pairs = self.size * self.size // 2
        self.board, self.revealed = self.create_board()
        self.player1_score = 0
        self.player2_score = 0
        self.current_player = 1
        self.first_card = None
        self.game_over = False
        self.move_button.config(state='normal')
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        self.current_player_label.config(text=f"Player {self.current_player}'s turn")
        self.print_board()

if __name__ == "__main__":
    game = MemoryGame()
    game.mainloop()
