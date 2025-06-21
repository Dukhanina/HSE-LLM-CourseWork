import tkinter as tk
from tkinter import messagebox
import random

VALUES='23456789TJQKA'
SUITS='SHDC'

def create_deck():
    return [v+s for v in VALUES for s in SUITS]

def deal(deck,n=5):
    return [deck.pop() for _ in range(n)]

def hand_rank(hand):
    counts={}
    vals=[]
    for c in hand:
        v=VALUES.index(c[0])+2
        counts[v]=counts.get(v,0)+1
        vals.append(v)
    flush=len({c[1] for c in hand})==1
    unique=sorted(set(vals))
    straight=False
    if len(unique)==5:
        if unique[-1]-unique[0]==4:
            straight=True
            high=unique[-1]
        elif set(unique)=={2,3,4,5,14}:
            straight=True
            high=5
    items=sorted(counts.items(),key=lambda x:(-x[1],-x[0]))
    if straight and flush: return (9,[high])
    if items[0][1]==4: return (8,[items[0][0]]+sorted([v for v in vals if v!=items[0][0]],reverse=True))
    if items[0][1]==3 and items[1][1]==2: return (7,[items[0][0],items[1][0]])
    if flush: return (6,sorted(vals,reverse=True))
    if straight: return (5,[high])
    if items[0][1]==3: return (4,[items[0][0]]+sorted([v for v in vals if v!=items[0][0]],reverse=True))
    if items[0][1]==2 and items[1][1]==2:
        p1,p2=items[0][0],items[1][0]
        kicker=[v for v in vals if v not in (p1,p2)][0]
        return (3,sorted([p1,p2],reverse=True)+[kicker])
    if items[0][1]==2: return (2,[items[0][0]]+sorted([v for v in vals if v!=items[0][0]],reverse=True))
    return (1,sorted(vals,reverse=True))

class PokerApp:
    def __init__(self,master):
        self.master=master
        master.title("Poker")
        self.new_button=tk.Button(master,text="Новая игра",command=self.new_game)
        self.new_button.pack(pady=5)
        self.log=tk.Text(master,height=15,state=tk.DISABLED)
        self.log.pack(pady=5)
        self.entry=tk.Entry(master)
        self.entry.pack(pady=5)
        self.entry.bind('<Return>',self.on_move)
        self.move_button=tk.Button(master,text="Сделать ход",command=self.on_move)
        self.move_button.pack(pady=5)
        self.new_game()

    def new_game(self):
        self.deck=create_deck()
        random.shuffle(self.deck)
        self.hands=[deal(self.deck),deal(self.deck)]
        self.current=0
        self.log.config(state=tk.NORMAL)
        self.log.delete('1.0',tk.END)
        self.log.insert(tk.END,"Новая игра\n")
        for i,hand in enumerate(self.hands):
            self.log.insert(tk.END,f"Игрок {i+1} раздает: {' '.join(hand)}\n")
        self.log.insert(tk.END,f"Игрок {self.current+1}, введите позиции для сброса (1-5 через пробел):\n")
        self.log.config(state=tk.DISABLED)
        self.entry.delete(0,tk.END)
        self.entry.focus()

    def on_move(self,event=None):
        s=self.entry.get().split()
        try:
            idxs=sorted({int(x)-1 for x in s},reverse=True)
            for i in idxs:
                if i<0 or i>4: raise ValueError
        except:
            messagebox.showerror("Ошибка","Введите корректные позиции 1-5 через пробел")
            return
        hand=self.hands[self.current]
        for i in idxs:
            hand.pop(i)
        while len(hand)<5:
            hand.append(self.deck.pop())
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END,f"Игрок {self.current+1} новая рука: {' '.join(hand)}\n")
        if self.current==0:
            self.current=1
            self.log.insert(tk.END,f"Игрок 2, введите позиции для сброса (1-5 через пробел):\n")
            self.log.config(state=tk.DISABLED)
            self.entry.delete(0,tk.END)
            self.entry.focus()
        else:
            r0=hand_rank(self.hands[0])
            r1=hand_rank(self.hands[1])
            self.log.insert(tk.END,f"Игрок 1 рука: {' '.join(self.hands[0])} Ранг: {r0}\n")
            self.log.insert(tk.END,f"Игрок 2 рука: {' '.join(self.hands[1])} Ранг: {r1}\n")
            if r0>r1: res="Игрок 1 выиграл"
            elif r1>r0: res="Игрок 2 выиграл"
            else: res="Ничья"
            self.log.insert(tk.END,res+"\n")
            self.log.config(state=tk.DISABLED)
        self.entry.delete(0,tk.END)

if __name__=='__main__':
    root=tk.Tk()
    PokerApp(root)
    root.mainloop()
