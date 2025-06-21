import tkinter as tk
from tkinter import messagebox
import random

LADDERS={1:38,4:14,9:31,21:42,28:84,36:44,51:67,71:91,80:100}
SNAKES={16:6,47:26,49:11,56:53,62:19,64:60,87:24,93:73,95:75,98:78}

def roll_dice():
    return random.randint(1,6)

def move(position,roll):
    pos=position+roll
    if pos>100:
        pos=100-(pos-100)
    if pos in LADDERS:
        pos=LADDERS[pos]
    elif pos in SNAKES:
        pos=SNAKES[pos]
    return pos

def check_win(position):
    return position==100

class SnakesLaddersApp:
    def __init__(self, master):
        self.master=master
        master.title("Змеи и Лестницы")
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
        self.positions=[0,0]
        self.current=0
        self.log.config(state=tk.NORMAL)
        self.log.delete('1.0',tk.END)
        self.log.insert(tk.END,"Новая игра\n")
        self.log.insert(tk.END,"Игрок 1 на клетке 0, Игрок 2 на клетке 0\n")
        self.log.insert(tk.END,"Игрок 1, введите 'r' и нажмите Enter для броска кубика\n")
        self.log.config(state=tk.DISABLED)
        self.entry.config(state=tk.NORMAL)
        self.move_button.config(state=tk.NORMAL)
        self.entry.delete(0,tk.END)
        self.entry.focus()

    def on_move(self,event=None):
        cmd=self.entry.get().strip().lower()
        if cmd!='r':
            messagebox.showerror("Ошибка","Введите 'r' для броска кубика")
            return
        roll=roll_dice()
        player=self.current
        pos=self.positions[player]
        new_pos=move(pos,roll)
        self.positions[player]=new_pos
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END,f"Игрок {player+1} бросил {roll}\n")
        self.log.insert(tk.END,f"Игрок {player+1} теперь на клетке {new_pos}\n")
        if check_win(new_pos):
            self.log.insert(tk.END,f"Игрок {player+1} выиграл!\n")
            self.entry.config(state=tk.DISABLED)
            self.move_button.config(state=tk.DISABLED)
        else:
            if roll!=6:
                self.current=1-self.current
            self.log.insert(tk.END,f"Игрок {self.current+1}, введите 'r' для броска кубика\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)
        self.entry.delete(0,tk.END)
        self.entry.focus()

if __name__=='__main__':
    root=tk.Tk()
    app=SnakesLaddersApp(root)
    root.mainloop()
