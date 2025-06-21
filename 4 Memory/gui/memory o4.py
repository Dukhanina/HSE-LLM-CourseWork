import tkinter as tk
from tkinter import messagebox
import random

ROWS=4
COLS=4
PAIRS=ROWS*COLS//2

def init_board():
    cards=[chr(ord('A')+i) for i in range(PAIRS)]*2
    random.shuffle(cards)
    return cards

def make_move(board,revealed,p1,p2,current,scores):
    if board[p1]==board[p2]:
        revealed[p1]=True
        revealed[p2]=True
        scores[current]+=1
        return True
    return False

def check_win(scores):
    return scores[1]+scores[2]==PAIRS

class MemoryApp:
    def __init__(self,master):
        master.title("Memory")
        self.new_button=tk.Button(master,text="Новая игра",command=self.new_game)
        self.new_button.pack(pady=5)
        self.log=tk.Text(master,height=20,state=tk.DISABLED)
        self.log.pack(pady=5)
        self.entry=tk.Entry(master)
        self.entry.pack(pady=5)
        self.entry.bind('<Return>',self.on_move)
        self.move_button=tk.Button(master,text="Сделать ход",command=self.on_move)
        self.move_button.pack(pady=5)
        self.new_game()

    def new_game(self):
        self.board=init_board()
        self.revealed=[False]*(ROWS*COLS)
        self.scores={1:0,2:0}
        self.current=1
        self.temp=[]
        self.log.config(state=tk.NORMAL)
        self.log.delete('1.0',tk.END)
        self.log.insert(tk.END,"Новая игра\n")
        self.print_board()
        self.log.insert(tk.END,f"Ход игрока {self.current}: введите две позиции (1-{ROWS*COLS}) через пробел\n")
        self.log.config(state=tk.DISABLED)
        self.entry.config(state=tk.NORMAL)
        self.move_button.config(state=tk.NORMAL)
        self.entry.delete(0,tk.END)
        self.entry.focus()

    def print_board(self):
        for i in range(ROWS):
            row=[]
            for j in range(COLS):
                idx=i*COLS+j
                if self.revealed[idx] or idx in self.temp:
                    row.append(self.board[idx])
                else:
                    row.append('*')
            self.log.insert(tk.END,' '.join(row)+'\n')
        self.log.insert(tk.END,'\n')

    def on_move(self,event=None):
        parts=self.entry.get().split()
        if len(parts)!=2:
            messagebox.showerror("Ошибка","Введите две позиции через пробел")
            return
        try:
            p1=int(parts[0])-1
            p2=int(parts[1])-1
        except:
            messagebox.showerror("Ошибка","Введите числовые позиции")
            return
        if not(0<=p1<ROWS*COLS) or not(0<=p2<ROWS*COLS):
            messagebox.showerror("Ошибка","Позиции вне диапазона")
            return
        if p1==p2:
            messagebox.showerror("Ошибка","Выберите разные позиции")
            return
        if self.revealed[p1] or self.revealed[p2]:
            messagebox.showerror("Ошибка","Карты уже открыты")
            return
        self.temp=[p1,p2]
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END,f"Игрок {self.current}: открыт(ы) {p1+1}, {p2+1}\n")
        self.print_board()
        match=make_move(self.board,self.revealed,p1,p2,self.current,self.scores)
        if match:
            self.log.insert(tk.END,"Совпадение!\n")
        else:
            self.log.insert(tk.END,"Нет совпадения\n")
        self.temp=[]
        self.print_board()
        if match and check_win(self.scores):
            self.log.insert(tk.END,f"Игра окончена. Счёт: {self.scores}\n")
            if self.scores[1]>self.scores[2]:
                self.log.insert(tk.END,"Игрок 1 выиграл\n")
            elif self.scores[2]>self.scores[1]:
                self.log.insert(tk.END,"Игрок 2 выиграл\n")
            else:
                self.log.insert(tk.END,"Ничья\n")
            self.entry.config(state=tk.DISABLED)
            self.move_button.config(state=tk.DISABLED)
            self.log.config(state=tk.DISABLED)
            return
        if not match:
            self.current=2 if self.current==1 else 1
        self.log.insert(tk.END,f"Следующий ход: игрок {self.current}\n")
        self.log.config(state=tk.DISABLED)
        self.entry.delete(0,tk.END)
        self.entry.focus()

if __name__=='__main__':
    root=tk.Tk()
    MemoryApp(root)
    root.mainloop()
