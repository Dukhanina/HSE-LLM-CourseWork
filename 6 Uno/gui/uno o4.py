import tkinter as tk
from tkinter import messagebox, simpledialog
import random

COLORS=['R','G','B','Y']
VALUES=[str(i) for i in range(1,10)]+['+2','Skip','Reverse']

def create_deck():
    deck=[]
    for c in COLORS:
        deck.append(c+'0')
        for v in VALUES:
            deck.append(c+v)
            deck.append(c+v)
    for _ in range(4):
        deck.append('W')
        deck.append('W4')
    return deck

def draw_card(deck,discard):
    if not deck:
        deck.extend(discard[:-1])
        random.shuffle(deck)
        discard[:] = [discard[-1]]
    return deck.pop()

def can_play(card,top_color,top_value,hand):
    if card in ('W','W4'):
        if card=='W4':
            return all(c[0]!=top_color for c in hand if c not in ('W','W4'))
        return True
    if card[0]==top_color or card[1:]==top_value:
        return True
    return False

def apply_card(card,idx,players,hands,deck,discard,top_color,top_value,skip):
    discard.append(card)
    draw=0
    if card in ('W','W4'):
        while True:
            clr=simpledialog.askstring("Choose color","Choose color (R/G/B/Y):")
            if clr is None:
                messagebox.showerror("Error","Color is required")
                continue
            clr=clr.strip().upper()
            if clr in COLORS:
                top_color=clr
                break
            messagebox.showerror("Error","Invalid color")
        top_value=card
    else:
        top_color=card[0]
        top_value=card[1:]
        if top_value in ('Skip','Reverse'):
            skip=True
        if top_value=='+2':
            draw=2
    if card=='W4':
        draw=4
    if draw>0:
        for _ in range(draw):
            hands[(idx+1)%players].append(draw_card(deck,discard))
        skip=True
    return top_color,top_value,skip

def check_win(hands):
    for i,h in enumerate(hands):
        if not h:
            return i
    return None

class UnoApp:
    def __init__(self, master):
        self.master=master
        master.title("Uno")
        self.new_button=tk.Button(master, text="Новая игра", command=self.new_game)
        self.new_button.pack(pady=5)
        self.log=tk.Text(master, height=20, state=tk.DISABLED)
        self.log.pack(pady=5)
        self.entry=tk.Entry(master)
        self.entry.pack(pady=5)
        self.entry.bind('<Return>', self.on_play)
        self.play_button=tk.Button(master, text="Играть/Добрать", command=self.on_play)
        self.play_button.pack(pady=5)
        self.new_game()

    def new_game(self):
        self.players=2
        self.deck=create_deck()
        random.shuffle(self.deck)
        self.hands=[ [self.deck.pop() for _ in range(7)] for _ in range(self.players) ]
        self.discard=[self.deck.pop()]
        while self.discard[-1] in ('W','W4'):
            self.deck.insert(0,self.discard.pop())
            self.discard.append(self.deck.pop())
        self.top_color=self.discard[-1][0]
        self.top_value=self.discard[-1][1:]
        self.turn=0
        self.skip=False
        self.log.config(state=tk.NORMAL)
        self.log.delete('1.0', tk.END)
        self.log.insert(tk.END, f"Новая игра\n")
        self.update_display()
        self.log.config(state=tk.DISABLED)
        self.entry.delete(0, tk.END)
        self.entry.focus()

    def update_display(self):
        idx=self.turn%self.players
        hand=self.hands[idx]
        self.log.insert(tk.END, f"Текущая карта: {self.discard[-1]}\n")
        self.log.insert(tk.END, f"Ход игрока {idx+1}\n")
        for i,card in enumerate(hand,1):
            self.log.insert(tk.END, f"{i}: {card}  ")
        self.log.insert(tk.END, "\n")
        if self.skip:
            self.log.insert(tk.END, "Ход пропущен\n")
            self.skip=False

    def on_play(self, event=None):
        idx=self.turn%self.players
        hand=self.hands[idx]
        move=self.entry.get().strip()
        if not move:
            messagebox.showerror("Ошибка","Введите номер карты или d для добора")
            return
        if move.lower()=='d':
            card=draw_card(self.deck,self.discard)
            hand.append(card)
            action=f"Игрок {idx+1} добрал {card}\n"
        else:
            if not move.isdigit():
                messagebox.showerror("Ошибка","Неверный ввод")
                return
            num=int(move)
            if num<1 or num>len(hand):
                messagebox.showerror("Ошибка","Номер вне диапазона")
                return
            card=hand[num-1]
            if not can_play(card,self.top_color,self.top_value,hand):
                messagebox.showerror("Ошибка","Недопустимый ход")
                return
            hand.pop(num-1)
            self.top_color,self.top_value,self.skip=apply_card(card,idx,self.players,self.hands,self.deck,self.discard,self.top_color,self.top_value,self.skip)
            action=f"Игрок {idx+1} сыграл {card}\n"
        winner=check_win(self.hands)
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, action)
        if winner is not None:
            self.log.insert(tk.END, f"Игрок {winner+1} выиграл\n")
            self.entry.config(state=tk.DISABLED)
            self.play_button.config(state=tk.DISABLED)
        else:
            self.turn+=1
            self.update_display()
        self.log.config(state=tk.DISABLED)
        self.entry.delete(0, tk.END)
        self.entry.focus()

if __name__=='__main__':
    root=tk.Tk()
    app=UnoApp(root)
    root.mainloop()
