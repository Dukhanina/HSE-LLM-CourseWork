import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext

class TicTacToeGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Крестики-нолики с задачами")
        self.master.geometry("400x550")
        self.master.resizable(False, False)

        self.board_data = []
        self.game_over = True
        self.current_player = "X"
        
        self._create_widgets()
        self.new_game()

    def _create_widgets(self):
        # Top Frame for controls
        control_frame = tk.Frame(self.master, pady=10)
        control_frame.pack(fill=tk.X)

        self.new_game_button = tk.Button(control_frame, text="Новая игра", command=self.new_game)
        self.new_game_button.pack()

        # Board Frame
        board_frame = tk.Frame(self.master, padx=10, pady=10)
        board_frame.pack()

        self.square_buttons = []
        for i in range(9):
            button = tk.Button(board_frame, text="", width=8, height=4, font=('Helvetica', 16, 'bold'),
                               command=lambda i=i: self.on_square_click(i))
            button.grid(row=i//3, column=i%3, padx=2, pady=2)
            self.square_buttons.append(button)

        # Log Frame
        log_frame = tk.Frame(self.master, padx=10, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_widget = scrolledtext.ScrolledText(log_frame, state='disabled', height=8, wrap=tk.WORD, font=('Arial', 10))
        self.log_widget.pack(fill=tk.BOTH, expand=True)

    def _initialize_board_data(self):
        return [
            {"problem": "38 - 26", "answer": 12, "mark": " "},
            {"problem": "76 - 58", "answer": 18, "mark": " "},
            {"problem": "35 - 16", "answer": 19, "mark": " "},
            {"problem": "67 - 31", "answer": 36, "mark": " "},
            {"problem": "50 - 42", "answer": 8, "mark": " "},
            {"problem": "28 - 15", "answer": 13, "mark": " "},
            {"problem": "86 - 26", "answer": 60, "mark": " "},
            {"problem": "44 - 15", "answer": 29, "mark": " "},
            {"problem": "92 - 46", "answer": 46, "mark": " "},
        ]

    def _update_board_display(self):
        for i, cell in enumerate(self.board_data):
            mark = cell["mark"]
            self.square_buttons[i].config(text=mark, state=tk.NORMAL if mark == " " and not self.game_over else tk.DISABLED)
            if mark == "X":
                self.square_buttons[i].config(disabledforeground="blue")
            elif mark == "O":
                self.square_buttons[i].config(disabledforeground="red")

    def _log(self, message):
        self.log_widget.config(state='normal')
        self.log_widget.insert(tk.END, message + "\n")
        self.log_widget.see(tk.END)
        self.log_widget.config(state='disabled')

    def new_game(self):
        self.board_data = self._initialize_board_data()
        self.current_player = "X"
        self.game_over = False
        self.log_widget.config(state='normal')
        self.log_widget.delete('1.0', tk.END)
        self.log_widget.config(state='disabled')
        self._log("Началась новая игра!")
        self._log(f"Ход игрока {self.current_player}.")
        self._update_board_display()

    def on_square_click(self, index):
        if self.game_over:
            messagebox.showwarning("Игра окончена", "Игра уже завершена. Начните новую игру.")
            return

        if self.board_data[index]["mark"] != " ":
            messagebox.showerror("Недопустимый ход", "Эта клетка уже занята. Выберите другую.")
            return

        problem_data = self.board_data[index]
        user_answer = simpledialog.askinteger("Решите задачу", f"Вопрос: {problem_data['problem']} = ?", parent=self.master)

        if user_answer is None:
            self._log("Ход отменён игроком.")
            return

        mark_to_place = ""
        opponent = "O" if self.current_player == "X" else "X"

        if user_answer == problem_data["answer"]:
            mark_to_place = self.current_player
            self._log(f"Верно! Игрок {self.current_player} ставит '{mark_to_place}'.")
        else:
            mark_to_place = opponent
            self._log(f"Ошибка. Ответ: {problem_data['answer']}. Игрок {opponent} ставит '{mark_to_place}'.")
        
        self.board_data[index]["mark"] = mark_to_place
        self._update_board_display()

        if self._check_win(mark_to_place):
            self.game_over = True
            self._update_board_display()
            messagebox.showinfo("Победа!", f"Игрок {mark_to_place} выиграл!")
            self._log(f"Игра окончена. Победитель: {mark_to_place}")
            return

        if self._check_draw():
            self.game_over = True
            self._update_board_display()
            messagebox.showinfo("Ничья!", "Все клетки заполнены. Ничья!")
            self._log("Игра окончена. Ничья!")
            return

        self.current_player = opponent
        self._log(f"Ход игрока {self.current_player}.")

    def _check_win(self, player):
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], # Горизонтали
            [0, 3, 6], [1, 4, 7], [2, 5, 8], # Вертикали
            [0, 4, 8], [2, 4, 6]             # Диагонали
        ]
        for condition in win_conditions:
            if all(self.board_data[i]["mark"] == player for i in condition):
                return True
        return False

    def _check_draw(self):
        return all(cell["mark"] != " " for cell in self.board_data)

if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeGUI(root)
    root.mainloop()
