import tkinter as tk
from tkinter import messagebox
import random

TRACK_LEN=52
HOME_LAPS=1
START_INDICES=[0,13]

def roll_dice():
    return random.randint(1,6)

def init_pawns():
    pos=[[START_INDICES[i]]*4 for i in range(2)]
    laps=[[0]*4 for _ in range(2)]
    return pos,laps

def get_block_positions(pos,laps,player):
    counts={}
    for p,l in zip(pos[player],laps[player]):
        if l==0:
            counts[p]=counts.get(p,0)+1
    return {p for p,c in counts.items() if c>=2}

def get_playable_moves(player,roll,pos,laps):
    start=START_INDICES[player]
    opp=1-player
    block_opp=get_block_positions(pos,laps,opp)
    valid=[]
    for i in range(4):
        cur=pos[player][i]
        lp=laps[player][i]
        new=cur+roll
        nl=lp
        if new>=TRACK_LEN:
            nl+=1
            new-=TRACK_LEN
        if nl>=HOME_LAPS and new==start:
            valid.append(i)
            continue
        if nl==0 and new in block_opp:
            continue
        valid.append(i)
    return valid

def move_pawn(player,i,roll,pos,laps):
    start=START_INDICES[player]
    opp=1-player
    cur=pos[player][i]
    lp=laps[player][i]
    new=cur+roll
    nl=lp
    if new>=TRACK_LEN:
        nl+=1
        new-=TRACK_LEN
    finished=False
    if nl>=HOME_LAPS and new==start:
        finished=True
    pos[player][i]=new
    laps[player][i]=nl
    extra=False
    if not finished and nl==0:
        opp_idxs=[j for j,(p,l) in enumerate(zip(pos[opp],laps[opp])) if p==new and l==0]
        if len(opp_idxs)==1:
            j=opp_idxs[0]
            pos[opp][j]=START_INDICES[opp]
            laps[opp][j]=0
            extra=True
    return extra

def check_win(player,pos,laps):
    start=START_INDICES[player]
    return all(laps[player][i]>=HOME_LAPS and pos[player][i]==start for i in range(4))

class LudoApp:
    def __init__(self,master):
        self.master=master
        master.title("Ludo")
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
        self.pos,self.laps=init_pawns()
        self.turn=0
        self.state='roll'
        self.last_roll=0
        self.playable=[]
        self.log.config(state=tk.NORMAL)
        self.log.delete('1.0',tk.END)
        self.log.insert(tk.END,"Новая игра\n")
        self.display_state()
        self.log.config(state=tk.DISABLED)
        self.entry.delete(0,tk.END)
        self.entry.focus()

    def display_state(self):
        player=self.turn%2
        if self.state=='roll':
            self.log.insert(tk.END,f"Ход игрока {player+1}. Нажмите 'Сделать ход'\n")
        else:
            self.log.insert(tk.END,f"Бросок: {self.last_roll}. Выберите пешку {', '.join(str(i+1) for i in self.playable)}\n")

    def on_move(self,event=None):
        player=self.turn%2
        if self.state=='roll':
            roll=roll_dice()
            self.last_roll=roll
            self.playable=get_playable_moves(player,roll,self.pos,self.laps)
            self.log.config(state=tk.NORMAL)
            self.log.insert(tk.END,f"Игрок {player+1} бросил {roll}\n")
            if not self.playable:
                messagebox.showinfo("Нет ходов",f"У игрока {player+1} нет ходов")
                self.turn+=1
                self.display_state()
                self.log.config(state=tk.DISABLED)
            else:
                self.state='select'
                self.log.insert(tk.END,"Допустимые пешки: "+", ".join(str(i+1) for i in self.playable)+"\n")
                self.log.insert(tk.END,"Введите номер пешки и нажмите Enter\n")
                self.log.config(state=tk.DISABLED)
            self.entry.delete(0,tk.END)
        else:
            move=self.entry.get().strip()
            if not move.isdigit():
                messagebox.showerror("Ошибка","Введите номер пешки")
                return
            idx=int(move)-1
            if idx not in self.playable:
                messagebox.showerror("Ошибка","Недопустимый ход")
                return
            extra=move_pawn(player,idx,self.last_roll,self.pos,self.laps)
            self.log.config(state=tk.NORMAL)
            self.log.insert(tk.END,f"Игрок {player+1} переместил пешку {idx+1}\n")
            if check_win(player,self.pos,self.laps):
                self.log.insert(tk.END,f"Игрок {player+1} выиграл\n")
                self.entry.config(state=tk.DISABLED)
                self.move_button.config(state=tk.DISABLED)
                self.log.config(state=tk.DISABLED)
                return
            if self.last_roll==6 or extra:
                self.state='roll'
                self.log.insert(tk.END,"Дополнительный ход\n")
            else:
                self.turn+=1
                self.state='roll'
            self.display_state()
            self.log.config(state=tk.DISABLED)
            self.entry.delete(0,tk.END)
            self.entry.focus()

if __name__=='__main__':
    root=tk.Tk()
    app=LudoApp(root)
    root.mainloop()
