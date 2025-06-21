import tkinter as tk
from tkinter import messagebox
import random

def create_deck():
    return [(i,j) for i in range(7) for j in range(i,7)]

def draw_hands(deck,players):
    hand_size = 7 if players==2 else 5
    return [[deck.pop() for _ in range(hand_size)] for _ in range(players)]

def get_playable(hand,left,right):
    if left is None:
        return list(range(len(hand)))
    playable=[]
    for i,(a,b) in enumerate(hand):
        if a==left or b==left or a==right or b==right:
            playable.append(i)
    return playable

def play_tile(hand,layout,index,left,right):
    a,b = hand.pop(index)
    if left is None:
        layout.append((a,b))
        return a,b
    if a==left:
        layout.insert(0,(b,a))
        return b,right
    if b==left:
        layout.insert(0,(a,b))
        return a,right
    if a==right:
        layout.append((a,b))
        return left,b
    if b==right:
        layout.append((b,a))
        return left,a
    return left,right

def sum_pips(hand):
    return sum(a+b for a,b in hand)

class DominoApp:
    def __init__(self, master):
        master.title("Домино")
        self.new_button = tk.Button(master, text="Новая игра", command=self.new_game)
        self.new_button.pack(pady=5)
        self.log = tk.Text(master, height=20, state=tk.DISABLED)
        self.log.pack(pady=5)
        self.entry = tk.Entry(master)
        self.entry.pack(pady=5)
        self.entry.bind('<Return>', self.on_move)
        self.move_button = tk.Button(master, text="Сделать ход", command=self.on_move)
        self.move_button.pack(pady=5)
        self.new_game()

    def new_game(self):
        self.players = 2
        deck = create_deck()
        random.shuffle(deck)
        self.hands = draw_hands(deck, self.players)
        self.layout = []
        self.left = None
        self.right = None
        self.passes = 0
        self.turn = 0
        self.log.config(state=tk.NORMAL)
        self.log.delete('1.0', tk.END)
        self.log.insert(tk.END, "Новая игра\n")
        self.display_state()
        self.log.config(state=tk.DISABLED)
        self.entry.delete(0, tk.END)
        self.entry.focus()

    def display_state(self):
        idx = self.turn % self.players
        hand = self.hands[idx]
        self.log.insert(tk.END, f"Игрок {idx+1} рука: ")
        for i,(a,b) in enumerate(hand,1):
            self.log.insert(tk.END, f"{i}:{a}-{b} ")
        self.log.insert(tk.END, "\n")
        self.log.insert(tk.END, "Выкладка: ")
        for a,b in self.layout:
            self.log.insert(tk.END, f"{a}-{b} ")
        self.log.insert(tk.END, "\n")
        if self.left is None:
            self.log.insert(tk.END, "Можно сыграть любую фишку\n")
        else:
            self.log.insert(tk.END, f"Концы: {self.left}-{self.right}\n")
            playable = get_playable(hand, self.left, self.right)
            self.log.insert(tk.END, "Допустимые номера: ")
            for i in playable:
                self.log.insert(tk.END, f"{i+1} ")
            self.log.insert(tk.END, "\n")
        self.log.insert(tk.END, "Введите номер фишки и нажмите Enter\n")
        self.log.see(tk.END)

    def on_move(self, event=None):
        idx = self.turn % self.players
        hand = self.hands[idx]
        if self.left is None:
            playable = list(range(len(hand)))
        else:
            playable = get_playable(hand, self.left, self.right)
        move = self.entry.get().strip()
        if not move.isdigit():
            messagebox.showerror("Ошибка","Введите число")
            return
        num = int(move)-1
        if num not in playable:
            if playable:
                messagebox.showerror("Ошибка","Недопустимый ход")
                return
            else:
                self.passes +=1
                self.log.config(state=tk.NORMAL)
                self.log.insert(tk.END, f"Игрок {idx+1} пропускает ход\n")
                if self.passes >= self.players:
                    scores=[sum_pips(h) for h in self.hands]
                    winner = scores.index(min(scores))
                    self.log.insert(tk.END, "Блокировка. Победил игрок "+str(winner+1)+"\n")
                    self.entry.config(state=tk.DISABLED)
                    self.move_button.config(state=tk.DISABLED)
                    self.log.config(state=tk.DISABLED)
                    return
                self.turn+=1
                self.display_state()
                self.log.config(state=tk.DISABLED)
                self.entry.delete(0, tk.END)
                return
        tile = hand[num]
        self.left, self.right = play_tile(hand, self.layout, num, self.left, self.right)
        self.passes=0
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, f"Игрок {idx+1} сыграл {tile[0]}-{tile[1]}\n")
        if not hand:
            self.log.insert(tk.END, f"Игрок {idx+1} победил\n")
            self.entry.config(state=tk.DISABLED)
            self.move_button.config(state=tk.DISABLED)
            self.log.config(state=tk.DISABLED)
            return
        self.turn+=1
        self.display_state()
        self.log.config(state=tk.DISABLED)
        self.entry.delete(0, tk.END)
        self.entry.focus()

if __name__=='__main__':
    root = tk.Tk()
    app = DominoApp(root)
    root.mainloop()
