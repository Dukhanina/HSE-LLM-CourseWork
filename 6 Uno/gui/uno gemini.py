import random
import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext

class UnoCard:
    def __init__(self, color, value):
        self.color = color
        self.value = value

    def __str__(self):
        if self.color == "Wild":
            return f"{self.value}" # Wild and Wild Draw Four
        return f"{self.color} {self.value}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, UnoCard):
            return NotImplemented
        return self.color == other.color and self.value == other.value

    def is_wild(self):
        return self.color == "Wild"

class UnoGame:
    def __init__(self, gui_app, num_players=2):
        self.gui_app = gui_app
        self.colors = ["Red", "Green", "Blue", "Yellow"]
        self.values = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "Skip", "Reverse", "Draw Two"]
        self.wild_cards = ["Wild", "Wild Draw Four"] # Renamed for clarity in card object
        self.deck = self._create_deck()
        self.players = [[] for _ in range(num_players)]
        self.discard_pile = []
        self.current_player_index = 0
        self.direction = 1 # 1 for clockwise (left), -1 for counter-clockwise (right)
        self.game_over = False
        self.current_color = None # The active color on the discard pile
        self.current_value = None # The active value on the discard pile

    def _create_deck(self):
        deck = []
        for color in self.colors:
            deck.append(UnoCard(color, "0")) # One 0 card per color
            for value in self.values[1:]: # Two of each 1-9, Skip, Reverse, Draw Two per color
                deck.append(UnoCard(color, value))
                deck.append(UnoCard(color, value))
        for _ in range(4): # Four Wild cards
            deck.append(UnoCard("Wild", "Wild"))
            deck.append(UnoCard("Wild", "Wild Draw Four")) # Four Wild Draw 4 cards
        random.shuffle(deck)
        return deck

    def _deal_cards(self):
        for i in range(len(self.players)):
            for _ in range(7): # Each player dealt seven cards
                self.players[i].append(self._draw_card())

    def _draw_card(self):
        if not self.deck:
            if len(self.discard_pile) <= 1:
                self.gui_app.log_message("No cards left to draw! Game might be stuck.")
                return None
            last_card = self.discard_pile.pop() # Keep the top card on discard
            self.deck = self.discard_pile
            random.shuffle(self.deck)
            self.discard_pile = [last_card]
            self.gui_app.log_message("Shuffling discard pile to create new deck.")
        return self.deck.pop(0)

    def _setup_discard_pile(self):
        while True:
            first_card = self._draw_card()
            if first_card is None: # Handle case where deck is somehow empty initially
                self.gui_app.log_message("Error: Deck empty during initial setup.")
                self.game_over = True
                return

            if first_card.value in ["Wild", "Wild Draw Four"]:
                self.deck.append(first_card)
                random.shuffle(self.deck)
                continue
            else:
                self.discard_pile.append(first_card)
                self.current_color = first_card.color
                self.current_value = first_card.value
                self.gui_app.log_message(f"Starting card: {first_card}")

                if first_card.value == "Draw Two":
                    self.gui_app.log_message(f"Player {self.current_player_index + 1} must draw 2 cards and forfeit turn.")
                    self.draw_cards_and_skip_turn(self.players[self.current_player_index], 2)
                    self._next_player_turn() # Skip the first player's turn
                elif first_card.value == "Reverse":
                    self.direction *= -1
                    self.gui_app.log_message(f"Play direction reversed.")
                    # If 2 players, reverse acts as a skip
                    if len(self.players) == 2:
                        self.gui_app.log_message(f"With 2 players, Reverse acts as a Skip. Player {self.current_player_index + 1} is skipped.")
                        self._next_player_turn()
                elif first_card.value == "Skip":
                    self.gui_app.log_message(f"Player {self.current_player_index + 1} is skipped.")
                    self._next_player_turn()
                break

    def start_game(self):
        self.game_over = False
        self.deck = self._create_deck()
        num_players = len(self.players)
        self.players = [[] for _ in range(num_players)] # Reset player hands
        self.discard_pile = []
        self.current_player_index = 0
        self.direction = 1
        
        self._deal_cards()
        self._setup_discard_pile()
        self.gui_app.log_message("\n--- Game Started ---")
        self.gui_app.update_game_state()

    def _next_player_turn(self):
        self.current_player_index = (self.current_player_index + self.direction) % len(self.players)
        if self.current_player_index < 0: # Handle negative index from reverse
            self.current_player_index += len(self.players)


    def is_valid_play(self, card_to_play):
        if not self.discard_pile: # Should not happen after setup, but for safety
            return False

        if card_to_play.is_wild():
            return True # Wild cards can always be played

        # Match by current color or current value
        if card_to_play.color == self.current_color or card_to_play.value == self.current_value:
            return True

        return False

    def get_playable_cards_indices(self, player_index):
        playable_indices = []
        for i, card in enumerate(self.players[player_index]):
            if self.is_valid_play(card):
                playable_indices.append(i)
        return playable_indices

    def attempt_play_card(self, player_index, card_index, chosen_color=None):
        player_hand = self.players[player_index]
        
        if not (0 <= card_index < len(player_hand)):
            self.gui_app.show_error("Invalid card index selected.")
            return False

        card_to_play = player_hand[card_index]

        if not self.is_valid_play(card_to_play):
            self.gui_app.show_error(f"Cannot play {card_to_play}. It does not match current color/value ({self.current_color} {self.current_value}).")
            return False

        # Specific rule for Wild Draw Four
        if card_to_play.value == "Wild Draw Four":
            has_matching_color = False
            for card in player_hand:
                if card.color == self.current_color and not card.is_wild():
                    has_matching_color = True
                    break
            if has_matching_color:
                self.gui_app.show_error("You have a card matching the current color. You cannot play Wild Draw Four.")
                return False # Prevent playing illegally

        # --- Card is valid, proceed with playing ---
        player_hand.pop(card_index)
        self.discard_pile.append(card_to_play)

        self.gui_app.log_message(f"Player {player_index + 1} played: {card_to_play}")

        # Update current color/value based on played card
        if card_to_play.is_wild():
            if chosen_color not in self.colors:
                self.gui_app.show_error("Wild card played, but no valid color chosen. Reverting play.")
                # This state should ideally not be reached if GUI prompts correctly.
                # For robustness, we could draw back the card, but for simplicity,
                # we'll just log and let the game continue in a potentially odd state
                # or enforce a default color.
                chosen_color = random.choice(self.colors) # Fallback to a random color
                self.gui_app.log_message(f"Defaulting wild color to {chosen_color} due to invalid choice.")

            self.current_color = chosen_color
            self.current_value = card_to_play.value # "Wild" or "Wild Draw Four"
            self.gui_app.log_message(f"Color changed to {self.current_color}.")
        else:
            self.current_color = card_to_play.color
            self.current_value = card_to_play.value

        # Apply special card effects
        if card_to_play.value == "Skip":
            self.gui_app.log_message(f"Player {self.current_player_index + 1} is skipped.")
            self._next_player_turn()
        elif card_to_play.value == "Reverse":
            self.direction *= -1
            self.gui_app.log_message(f"Play direction reversed.")
            if len(self.players) == 2: # In a 2-player game, Reverse acts as a Skip
                self.gui_app.log_message(f"With 2 players, Reverse acts as a Skip. Player {self.current_player_index + 1} is skipped.")
                self._next_player_turn()
        elif card_to_play.value == "Draw Two":
            self.gui_app.log_message(f"Next player draws 2 cards and is skipped.")
            self._next_player_turn() # Advance to the player who must draw
            self.draw_cards_and_skip_turn(self.players[self.current_player_index], 2)
            self._next_player_turn() # Skip them
        elif card_to_play.value == "Wild Draw Four":
            self.gui_app.log_message(f"Next player draws 4 cards and is skipped.")
            self._next_player_turn() # Advance to the player who must draw
            self.draw_cards_and_skip_turn(self.players[self.current_player_index], 4)
            self._next_player_turn() # Skip them

        # Check for UNO
        if len(player_hand) == 1:
            self.gui_app.log_message(f"Player {player_index + 1} has ONE card left! UNO!")
            # In a full game, there would be a penalty if they don't declare "Uno"
            # and another player catches them before the next player's turn begins.
            # This simplified version just logs it.

        return True

    def draw_cards_and_skip_turn(self, player_hand, num_cards):
        drawn_cards_str = []
        for _ in range(num_cards):
            drawn_card = self._draw_card()
            if drawn_card:
                player_hand.append(drawn_card)
                drawn_cards_str.append(str(drawn_card))
            else:
                self.gui_app.log_message("Not enough cards to draw.")
                break
        self.gui_app.log_message(f"Drew cards: {', '.join(drawn_cards_str)}")


    def check_for_winner(self):
        if not self.players[self.current_player_index]:
            self.game_over = True
            self.gui_app.log_message(f"\n--- Player {self.current_player_index + 1} wins the round! ---")
            messagebox.showinfo("Game Over", f"Player {self.current_player_index + 1} wins!")
            return True
        return False

class UnoGUI:
    def __init__(self, master):
        self.master = master
        master.title("Uno Game")
        self.game = None
        self.num_players = 2 # Default number of players

        # --- Widgets ---
        self.log_frame = tk.LabelFrame(master, text="Game Log")
        self.log_frame.pack(padx=10, pady=5, fill="x")
        self.log_text = scrolledtext.ScrolledText(self.log_frame, state='disabled', width=80, height=10, wrap=tk.WORD)
        self.log_text.pack(padx=5, pady=5)

        self.info_frame = tk.Frame(master)
        self.info_frame.pack(pady=5)

        self.current_player_label = tk.Label(self.info_frame, text="Current Player: -")
        self.current_player_label.pack(side=tk.LEFT, padx=10)

        self.top_card_label = tk.Label(self.info_frame, text="Top Card: -")
        self.top_card_label.pack(side=tk.LEFT, padx=10)

        self.current_color_label = tk.Label(self.info_frame, text="Current Color: -")
        self.current_color_label.pack(side=tk.LEFT, padx=10)
        
        self.player_hand_frame = tk.LabelFrame(master, text="Your Hand (Player 1)") # Assuming Player 1 is controlled by GUI
        self.player_hand_frame.pack(padx=10, pady=5, fill="x")
        self.card_buttons = []

        self.action_frame = tk.Frame(master)
        self.action_frame.pack(pady=10)

        self.draw_button = tk.Button(self.action_frame, text="Draw Card", command=self.handle_draw_card)
        self.draw_button.pack(side=tk.LEFT, padx=10)

        self.play_index_label = tk.Label(self.action_frame, text="Card Index to Play:")
        self.play_index_label.pack(side=tk.LEFT, padx=5)
        self.play_index_entry = tk.Entry(self.action_frame, width=5)
        self.play_index_entry.pack(side=tk.LEFT, padx=5)

        self.play_button = tk.Button(self.action_frame, text="Play Card", command=self.handle_play_card)
        self.play_button.pack(side=tk.LEFT, padx=10)

        self.new_game_button = tk.Button(master, text="New Game", command=self.start_new_game)
        self.new_game_button.pack(pady=10)

        self.start_new_game() # Start game immediately on launch

    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def show_error(self, message):
        messagebox.showerror("Invalid Action", message)
        self.log_message(f"Error: {message}") # Log errors as well

    def update_game_state(self):
        if not self.game or self.game.game_over:
            self.current_player_label.config(text="Game Over")
            self.top_card_label.config(text="Top Card: -")
            self.current_color_label.config(text="Current Color: -")
            self.clear_hand_display()
            self.disable_actions()
            return

        self.current_player_label.config(text=f"Current Player: {self.game.current_player_index + 1}")
        top_card_display = str(self.game.discard_pile[-1]) if self.game.discard_pile else "None"
        self.top_card_label.config(text=f"Top Card: {top_card_display}")
        self.current_color_label.config(text=f"Current Color: {self.game.current_color}")

        self.update_hand_display()
        
        # Only enable actions for the current player (Player 1 in this simple setup)
        if self.game.current_player_index == 0:
            self.enable_actions()
        else:
            self.disable_actions()
            # For AI players, simulate their turn after a delay
            self.master.after(1000, self.simulate_ai_turn) # 1 second delay for AI turn

    def clear_hand_display(self):
        for button in self.card_buttons:
            button.destroy()
        self.card_buttons = []

    def update_hand_display(self):
        self.clear_hand_display()
        if self.game.players:
            player_hand = self.game.players[0] # Assuming player 1 is controlled by GUI
            playable_indices = self.game.get_playable_cards_indices(0)

            for i, card in enumerate(player_hand):
                btn = tk.Button(self.player_hand_frame, text=str(card), 
                                command=lambda idx=i: self.select_card_from_hand(idx),
                                relief=tk.RAISED, borderwidth=2)
                
                # Highlight playable cards
                if i in playable_indices:
                    btn.config(fg="blue", font=("Arial", 10, "bold")) # Make playable cards stand out
                else:
                    btn.config(fg="black") # Non-playable cards

                # Set background color based on card color
                color_map = {"Red": "red", "Green": "green", "Blue": "blue", "Yellow": "gold", "Wild": "purple"}
                btn.config(bg=color_map.get(card.color, "lightgray"))

                btn.pack(side=tk.LEFT, padx=2, pady=2)
                self.card_buttons.append(btn)

    def select_card_from_hand(self, card_index):
        # Automatically fill the entry box when a card button is clicked
        self.play_index_entry.delete(0, tk.END)
        self.play_index_entry.insert(0, str(card_index))
        self.log_message(f"Selected card at index {card_index}: {self.game.players[0][card_index]}")

    def handle_play_card(self):
        if self.game.game_over or self.game.current_player_index != 0:
            self.show_error("It's not your turn or the game is over.")
            return

        try:
            card_index = int(self.play_index_entry.get())
        except ValueError:
            self.show_error("Please enter a valid number for the card index.")
            return

        card_to_play = None
        if 0 <= card_index < len(self.game.players[0]):
            card_to_play = self.game.players[0][card_index]
        else:
            self.show_error("Invalid card index. The index is out of bounds for your hand.")
            return

        chosen_color = None
        if card_to_play.is_wild():
            chosen_color = simpledialog.askstring("Choose Color", "Enter chosen color (Red, Green, Blue, Yellow):",
                                                  parent=self.master)
            if chosen_color:
                chosen_color = chosen_color.capitalize()
                if chosen_color not in self.game.colors:
                    self.show_error("Invalid color choice. Please choose from Red, Green, Blue, Yellow.")
                    return
            else:
                self.show_error("Color must be chosen for Wild card.")
                return # User cancelled or didn't enter a color

        played = self.game.attempt_play_card(0, card_index, chosen_color)
        if played:
            if not self.game.check_for_winner():
                self.update_game_state() # Update for next player's turn
        else:
            self.update_game_state() # Re-draw hand if play was invalid

    def handle_draw_card(self):
        if self.game.game_over or self.game.current_player_index != 0:
            self.show_error("It's not your turn or the game is over.")
            return

        # Check if any cards are playable first. If so, drawing is optional.
        playable_indices = self.game.get_playable_cards_indices(0)
        if playable_indices:
            confirm_draw = messagebox.askyesno("Draw Card?", "You have playable cards. Are you sure you want to draw instead?", parent=self.master)
            if not confirm_draw:
                return # Don't draw if user changes mind

        drawn_card = self.game._draw_card()
        if drawn_card:
            self.game.players[0].append(drawn_card)
            self.log_message(f"Player 1 drew: {drawn_card}")
            self.update_hand_display() # Update hand immediately after drawing

            # After drawing, player can play the drawn card if valid
            if self.game.is_valid_play(drawn_card):
                play_drawn = messagebox.askyesno("Play Drawn Card?", f"You drew {drawn_card}. Do you want to play it?", parent=self.master)
                if play_drawn:
                    # Find the index of the newly drawn card (always last)
                    new_card_index = len(self.game.players[0]) - 1
                    chosen_color = None
                    if drawn_card.is_wild():
                        chosen_color = simpledialog.askstring("Choose Color", "Enter chosen color (Red, Green, Blue, Yellow):",
                                                              parent=self.master)
                        if chosen_color:
                            chosen_color = chosen_color.capitalize()
                            if chosen_color not in self.game.colors:
                                self.show_error("Invalid color choice. Turn passes.")
                                self.game._next_player_turn()
                                self.update_game_state()
                                return
                        else:
                            self.show_error("Color must be chosen for Wild card. Turn passes.")
                            self.game._next_player_turn()
                            self.update_game_state()
                            return
                    
                    played = self.game.attempt_play_card(0, new_card_index, chosen_color)
                    if played:
                        if not self.game.check_for_winner():
                            self.update_game_state()
                    else:
                        self.update_game_state() # Update hand display if play failed
                else:
                    self.game._next_player_turn() # Turn passes if drawn card not played
                    self.update_game_state()
            else:
                self.game._next_player_turn() # Turn passes if drawn card not playable
                self.update_game_state()
        else:
            self.log_message("No cards left in deck to draw.")
            self.game._next_player_turn() # Turn passes if no cards to draw
            self.update_game_state()

    def simulate_ai_turn(self):
        if self.game.game_over or self.game.current_player_index == 0:
            return # Only simulate for AI players

        player_index = self.game.current_player_index
        ai_hand = self.game.players[player_index]
        playable_indices = self.game.get_playable_cards_indices(player_index)

        if playable_indices:
            # Simple AI: Play the first playable card
            card_index_to_play = playable_indices[0]
            card_to_play = ai_hand[card_index_to_play]
            
            chosen_color = None
            if card_to_play.is_wild():
                chosen_color = random.choice(self.game.colors) # AI picks random color
                self.log_message(f"AI Player {player_index + 1} chose color: {chosen_color}")

            played = self.game.attempt_play_card(player_index, card_index_to_play, chosen_color)
            if not played: # Should not happen with current logic if card is in playable_indices
                self.log_message(f"AI Player {player_index + 1} failed to play, drawing instead.")
                self._ai_draw_turn(player_index)
        else:
            self.log_message(f"AI Player {player_index + 1} has no playable cards. Drawing a card.")
            self._ai_draw_turn(player_index)

        if not self.game.game_over:
            self.update_game_state() # Update for next turn

    def _ai_draw_turn(self, player_index):
        drawn_card = self.game._draw_card()
        if drawn_card:
            self.game.players[player_index].append(drawn_card)
            self.log_message(f"AI Player {player_index + 1} drew: {drawn_card}")
            if self.game.is_valid_play(drawn_card):
                self.log_message(f"AI Player {player_index + 1} plays drawn card.")
                # Play the drawn card (it's the last one in hand)
                card_index_to_play = len(self.game.players[player_index]) - 1
                card_to_play = self.game.players[player_index][card_index_to_play]
                chosen_color = None
                if card_to_play.is_wild():
                    chosen_color = random.choice(self.game.colors)
                self.game.attempt_play_card(player_index, card_index_to_play, chosen_color)
            else:
                self.log_message(f"AI Player {player_index + 1} cannot play drawn card. Turn passes.")
                self.game._next_player_turn()
        else:
            self.log_message(f"AI Player {player_index + 1} attempted to draw but deck is empty. Turn passes.")
            self.game._next_player_turn()


    def disable_actions(self):
        self.draw_button.config(state=tk.DISABLED)
        self.play_button.config(state=tk.DISABLED)
        self.play_index_entry.config(state=tk.DISABLED)
        for btn in self.card_buttons:
            btn.config(state=tk.DISABLED)

    def enable_actions(self):
        self.draw_button.config(state=tk.NORMAL)
        self.play_button.config(state=tk.NORMAL)
        self.play_index_entry.config(state=tk.NORMAL)
        for btn in self.card_buttons:
            btn.config(state=tk.NORMAL)

    def start_new_game(self):
        num_players_str = simpledialog.askstring("New Game", "Enter number of players (2-10):", initialvalue="2", parent=self.master)
        if num_players_str:
            try:
                num_players = int(num_players_str)
                if 2 <= num_players <= 10:
                    self.num_players = num_players
                    self.log_text.config(state='normal')
                    self.log_text.delete(1.0, tk.END)
                    self.log_text.config(state='disabled')
                    self.log_message("Starting a new game...")
                    self.game = UnoGame(self, self.num_players)
                    self.game.start_game()
                else:
                    messagebox.showerror("Invalid Input", "Number of players must be between 2 and 10.")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number for players.")
        else:
            self.log_message("New game cancelled.")


def main():
    root = tk.Tk()
    app = UnoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
