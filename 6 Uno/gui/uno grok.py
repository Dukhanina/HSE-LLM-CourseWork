import tkinter as tk
from tkinter import messagebox, simpledialog
import random
from collections import deque

class Card:
    def __init__(self, color, value):
        self.color = color
        self.value = value
    
    def __str__(self):
        return f"{self.color} {self.value}"

class UnoGame:
    def __init__(self, num_players):
        self.num_players = num_players
        self.colors = ['Red', 'Yellow', 'Green', 'Blue']
        self.values = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'Skip', 'Reverse', 'Draw Two', 'Wild', 'Wild Draw Four']
        self.deck = [Card(color, value) for color in self.colors for value in self.values if value not in ['Wild', 'Wild Draw Four']] + [Card('Wild', 'Wild') for _ in range(4)] + [Card('Wild', 'Wild Draw Four') for _ in range(4)]
        random.shuffle(self.deck)
        self.players = [[] for _ in range(num_players)]
        self.discard_pile = deque()
        self.current_player = 0
        self.direction = 1
        self.winner = None
        
        # Deal 7 cards to each player
        for _ in range(7):
            for player in self.players:
                player.append(self.deck.pop())
        self.discard_pile.append(self.deck.pop())
    
    def can_play_card(self, card):
        top_card = self.discard_pile[-1]
        return card.color == top_card.color or card.value == top_card.value or card.color == 'Wild'
    
    def play_card(self, card):
        self.discard_pile.append(card)
        self.players[self.current_player].remove(card)
        if len(self.players[self.current_player]) == 0:
            self.winner = self.current_player
        elif len(self.players[self.current_player]) == 1:
            print("UNO!")  # В GUI это отображается в логе
        if card.value == 'Reverse':
            self.direction *= -1
        elif card.value == 'Skip':
            self.advance_player()
        elif card.value == 'Draw Two':
            next_player = (self.current_player + self.direction) % self.num_players
            for _ in range(2):
                if self.deck:
                    self.players[next_player].append(self.deck.pop())
        elif card.value == 'Wild Draw Four':
            next_player = (self.current_player + self.direction) % self.num_players
            for _ in range(4):
                if self.deck:
                    self.players[next_player].append(self.deck.pop())
    
    def draw_card(self, root):
        if len(self.deck) == 0:
            self.deck = list(self.discard_pile)[:-1]
            self.discard_pile = deque([self.discard_pile[-1]])
            random.shuffle(self.deck)
        card = self.deck.pop()
        self.players[self.current_player].append(card)
        if self.can_play_card(card):
            if card.value in ('Wild', 'Wild Draw Four'):
                color = simpledialog.askstring("Выбор цвета", "Введите цвет (Red/Yellow/Green/Blue):", parent=root)
                if color and color.capitalize() in ['Red', 'Yellow', 'Green', 'Blue']:
                    card.color = color.capitalize()
                else:
                    self.players[self.current_player].remove(card)
                    self.deck.append(card)
                    return
            self.play_card(card)
    
    def take_turn(self, choice, root):
        player = self.players[self.current_player]
        if choice == 'draw':
            self.draw_card(root)
            return None
        else:
            try:
                index = int(choice)
                if index < 0 or index >= len(player):
                    return "Недопустимый индекс карты"
                card = player[index]
                if self.can_play_card(card):
                    if card.value in ('Wild', 'Wild Draw Four'):
                        color = simpledialog.askstring("Выбор цвета", "Введите цвет (Red/Yellow/Green/Blue):", parent=root)
                        if color and color.capitalize() in ['Red', 'Yellow', 'Green', 'Blue']:
                            card.color = color.capitalize()
                        else:
                            return "Недопустимый цвет"
                    self.play_card(card)
                    return None
                else:
                    return "Эту карту нельзя сыграть"
            except ValueError:
                return "Недопустимый ввод"
    
    def advance_player(self):
        self.current_player = (self.current_player + self.direction) % self.num_players

class UnoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Игра Uno")
        self.game = None
        self.setup_widgets()
        self.start_new_game()
    
    def setup_widgets(self):
        self.new_game_button = tk.Button(self.root, text="Новая игра", command=self.start_new_game)
        self.new_game_button.pack(pady=5)
        
        self.log_text = tk.Text(self.root, height=20, width=50)
        self.log_text.pack(pady=5)
        
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(pady=5)
        
        self.input_label = tk.Label(self.input_frame, text="Введите индекс карты или 'draw':")
        self.input_label.pack(side=tk.LEFT)
        
        self.input_entry = tk.Entry(self.input_frame)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        
        self.play_button = tk.Button(self.input_frame, text="Сыграть", command=self.play_move)
        self.play_button.pack(side=tk.LEFT)
    
    def start_new_game(self):
        self.game = UnoGame(2)  # 2 игрока для простоты
        self.display_turn()
    
    def display_turn(self):
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, f"Ход игрока {self.game.current_player}\n")
        self.log_text.insert(tk.END, f"Верхняя карта: {self.game.discard_pile[-1]}\n")
        self.log_text.insert(tk.END, "Ваша рука:\n")
        for i, card in enumerate(self.game.players[self.game.current_player]):
            self.log_text.insert(tk.END, f"{i}: {card}\n")
        if len(self.game.players[(self.game.current_player - self.game.direction) % self.game.num_players]) == 1:
            self.log_text.insert(tk.END, "Предыдущий игрок сказал: UNO!\n")
        self.log_text.see(tk.END)
    
    def play_move(self):
        if self.game.winner is not None:
            messagebox.showinfo("Игра окончена", f"Победил игрок {self.game.winner}!")
            return
        choice = self.input_entry.get().strip()
        self.input_entry.delete(0, tk.END)
        error = self.game.take_turn(choice, self.root)
        if error:
            messagebox.showerror("Ошибка", error)
        else:
            if self.game.winner is not None:
                messagebox.showinfo("Игра окончена", f"Победил игрок {self.game.winner}!")
            else:
                self.game.advance_player()
                self.display_turn()

if __name__ == "__main__":
    root = tk.Tk()
    app = UnoGUI(root)
    root.mainloop()
