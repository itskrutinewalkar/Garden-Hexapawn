import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from itertools import count
import pygame

class HexapawnGUI:
    # [Previous initialization code remains the same until the evaluate method]
    def __init__(self):
        pygame.mixer.init()
        self.window = tk.Tk()
        self.window.title("Hexapawn")
        self.window.configure(bg="#F1F0E8")

        # Center the window on the screen
        window_width = 800  # Set desired width
        window_height = 800  # Set desired height

        # Get the screen dimensions
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        # Calculate the center position
        center_x = (screen_width // 2) - (window_width // 2)
        center_y = (screen_height // 2) - (window_height // 2)
        self.window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        self.win_sound = "win.mp3"
        self.lose_sound = "lose.mp3"
        pygame.mixer.music.load(self.win_sound)

        #Sounds while playing
        self.sounds = {
            'select': lambda: self.window.bell(),
            'move': lambda: self.window.bell(),
        }

         # Start page
        self.create_start_page()

    def create_start_page(self):
        # Clear any existing widgets
        for widget in self.window.winfo_children():
            widget.destroy()        

        # Title
        title = tk.Label(self.window, text="♟ HEXAPAWN ♟", font=('Times New Roman', 35, 'bold'), bg="#F1F0E8", fg="#493628")
        title.pack(pady=20)

        # Description
        desc = tk.Label(self.window, 
                        text="Hexapawn is a mini chess-like game played on a 3x3 board where\n\n"
                            "- Each player starts with 3 pawns on opposite ends\n"
                            "- Pawns can move forward one square if unblocked\n"
                            "- Pawns can capture diagonally forward\n"
                            "- First player to either get a pawn to the opposite end,\n capture all opponent pawns, or block all opponent moves wins", 
                        font=('Lora', 20, 'italic'), justify=tk.LEFT, bg="#F1F0E8", fg="#493628")
        desc.pack(pady=20)

        # Start button
        start_button = tk.Button(self.window, text="START GAME", 
                                command=self.start_game, 
                                font=('Times New Roman', 18), bg="#493628", fg="#493628", relief="flat",  # Removes the default border
                                      padx=20, pady=10,  # Padding inside the button
                                      bd=0)
        start_button.pack(pady=10)

        self.gif_label = tk.Label(self.window, bg="#F1F0E8")
        self.gif_label.pack(pady=20)
        self.hexapawn_gif = "hexa.gif"
        # Load and animate the GIF
        self.animate_gif(self.hexapawn_gif)

    def animate_gif(self, gif_path):
        gif = Image.open(gif_path)

        frames = []
        try:
            while True:
                frame = gif.copy()
                frame.thumbnail((320, 320))
                frames.append(ImageTk.PhotoImage(frame))
                gif.seek(len(frames))  # Go to next frame
        except EOFError:
            pass  # End of frames

        def update(ind=0):
            frame = frames[ind]
            self.gif_label.configure(image=frame)
            ind = (ind + 1) % len(frames)  # Loop through frames
            self.window.after(50, update, ind)  # Adjust timing as needed

        update()  # Start animation



    def start_game(self):
        # Clear start page
        for widget in self.window.winfo_children():
            widget.destroy()

        
        # Game state
        self.board = [
            ['B', 'B', 'B'],
            ['.', '.', '.'],
            ['W', 'W', 'W']
        ]
        self.current_player = 'W'  # W for White (human), B for Black (AI)
        self.selected_piece = None
        
        # Create buttons for the board
        self.buttons = []
        for i in range(3):
            row = []
            self.window.grid_rowconfigure(i, weight=1)
            for j in range(3):
                self.window.grid_columnconfigure(j, weight=1)
                if i == j or (i % 2 == 0 and j % 2 == 0):
                   bg_color = '#F1F0E8'
                else:
                   bg_color = '#755322'
                button = tk.Button(self.window, width=10, height=5,
                                   command=lambda r=i, c=j: self.handle_click(r, c),
                                   font=('Helvatica', 120, 'bold'), fg=bg_color)
                button.grid(row=i, column=j)
                row.append(button)
            self.buttons.append(row)
        
        self.update_display()
    
    def update_display(self):
        for i in range(3):
            for j in range(3):
                text = self.board[i][j]
                if text == 'W':
                    self.buttons[i][j].config(text='♙', fg='#6b3417', bg='#ee871a')
                elif text == 'B':
                    self.buttons[i][j].config(text='♟', fg='#6b3417', bg='#ee871a')
                else:
                    self.buttons[i][j].config(text='', bg='#F1F0E8')
    
    def handle_click(self, row, col):
        if self.current_player != 'W':  # Only allow clicks during human's turn
            return

        self.sounds['select']()  # Play selection sound

        if self.selected_piece is None:
            # Selecting a piece
            if self.board[row][col] == 'W':
                self.selected_piece = (row, col)
                button = self.buttons[row][col]
                button.config(bg='#ee871a')
                button.update()
        else:
            # Moving a piece
            start_row, start_col = self.selected_piece
            if self.is_valid_move(start_row, start_col, row, col):
                # Make the move
                self.board[row][col] = self.board[start_row][start_col]
                self.board[start_row][start_col] = '.'
                self.selected_piece = None
                self.update_display()
                
                if self.check_win('W'):
                    pygame.mixer.music.load(self.win_sound)
                    pygame.mixer.music.play()
                    self.window.after(500, lambda: self.display_message_and_exit("You win! 🎉"))
                    return
                
                # AI's turn
                self.current_player = 'B'
                self.make_ai_move()
            else:
                messagebox.showinfo("Invalid move!", "Please select the correct cell")
                self.selected_piece = None
                self.update_display()
    
    def is_valid_move(self, start_row, start_col, end_row, end_col):
        piece = self.board[start_row][start_col]
        target = self.board[end_row][end_col]
        
        if piece == 'W':
            # White moves upward
            if end_row == start_row - 1:  # Moving one step forward
                if end_col == start_col and target == '.':  # Straight move
                    return True
                if abs(end_col - start_col) == 1 and target == 'B':  # Capture
                    return True
        return False
    
    def get_possible_moves(self, player):
        moves = []
        direction = -1 if player == 'W' else 1
        
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == player:
                    # Forward move
                    new_row = i + direction
                    if 0 <= new_row < 3 and self.board[new_row][j] == '.':
                        moves.append(((i, j), (new_row, j)))
                    
                    # Diagonal captures
                    for new_col in [j-1, j+1]:
                        if 0 <= new_row < 3 and 0 <= new_col < 3:
                            if self.board[new_row][new_col] != '.' and \
                               self.board[new_row][new_col] != player:
                                moves.append(((i, j), (new_row, new_col)))
        return moves
    
    def make_move(self, start, end):
        start_row, start_col = start
        end_row, end_col = end
        self.board[end_row][end_col] = self.board[start_row][start_col]
        self.board[start_row][start_col] = '.'
    
    def undo_move(self, start, end, captured_piece):
        start_row, start_col = start
        end_row, end_col = end
        self.board[start_row][start_col] = self.board[end_row][end_col]
        self.board[end_row][end_col] = captured_piece
    
    def check_win(self, player):
        opponent = 'B' if player == 'W' else 'W'
        
        # Check if opponent has no pieces
        if not any(opponent in row for row in self.board):
            return True
            
        # Check if opponent has no valid moves
        if not self.get_possible_moves(opponent):
            return True
            
        # Check if any pawn reached the opposite end
        if player == 'W' and 'W' in self.board[0]:
            return True
        if player == 'B' and 'B' in self.board[2]:
            return True
            
        return False

    def evaluate(self):
        # First check for immediate wins
        if self.check_win('B'):
            return 1000
        if self.check_win('W'):
            return -1000
            
        # Improved heuristic evaluation
        score = 0
        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):  # Fixed: enumerate row directly
                if cell == 'B':
                    # Give more value to pawns closer to winning position
                    score += 10 + (2 - i) * 5  # More value for pawns closer to bottom
                    # Add value for having center control
                    if j == 1:
                        score += 2
                elif cell == 'W':
                    # Similar evaluation for white pieces
                    score -= 10 + i * 5  # More value for pawns closer to top
                    if j == 1:
                        score -= 2

        # Add mobility score (number of possible moves)
        b_moves = len(self.get_possible_moves('B'))
        w_moves = len(self.get_possible_moves('W'))
        score += b_moves * 3
        score -= w_moves * 3

        return score

    def get_possible_moves(self, player):
        moves = []
        direction = -1 if player == 'W' else 1
        
        # Debug print
        print(f"Getting moves for {player}")
        print("Current board state:")
        for row in self.board:
            print(row)
        
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == player:
                    # Forward move
                    new_row = i + direction
                    if 0 <= new_row < 3 and self.board[new_row][j] == '.':
                        moves.append(((i, j), (new_row, j)))
                        print(f"Found forward move from ({i},{j}) to ({new_row},{j})")
                    
                    # Diagonal captures
                    for new_col in [j-1, j+1]:
                        if 0 <= new_row < 3 and 0 <= new_col < 3:
                            target = self.board[new_row][new_col]
                            enemy = 'W' if player == 'B' else 'B'
                            if target == enemy:
                                moves.append(((i, j), (new_row, new_col)))
                                print(f"Found capture move from ({i},{j}) to ({new_row},{new_col})")
        
        print(f"Total moves found: {len(moves)}")
        return moves

    def minimax(self, depth, alpha, beta, maximizing_player):
        # Debug print
        print(f"Minimax called with depth {depth}, maximizing: {maximizing_player}")
        
        if depth == 0:
            eval_score = self.evaluate()
            print(f"Leaf node evaluation: {eval_score}")
            return eval_score, None
            
        if self.check_win('B'):
            return 1000 + depth, None
        if self.check_win('W'):
            return -1000 - depth, None
        
        player = 'B' if maximizing_player else 'W'
        possible_moves = self.get_possible_moves(player)
        
        if not possible_moves:
            eval_score = self.evaluate()
            print(f"No moves available, evaluation: {eval_score}")
            return eval_score, None
        
        best_move = possible_moves[0]  # Initialize with first move
        if maximizing_player:
            max_eval = float('-inf')
            for start, end in possible_moves:
                captured_piece = self.board[end[0]][end[1]]
                self.make_move(start, end)
                
                eval, _ = self.minimax(depth - 1, alpha, beta, False)
                self.undo_move(start, end, captured_piece)
                
                print(f"Move {start}->{end} evaluation: {eval}")
                
                if eval > max_eval:
                    max_eval = eval
                    best_move = (start, end)
                
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for start, end in possible_moves:
                captured_piece = self.board[end[0]][end[1]]
                self.make_move(start, end)
                
                eval, _ = self.minimax(depth - 1, alpha, beta, True)
                self.undo_move(start, end, captured_piece)
                
                print(f"Move {start}->{end} evaluation: {eval}")
                
                if eval < min_eval:
                    min_eval = eval
                    best_move = (start, end)
                
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def make_ai_move(self):
        print("AI is thinking...")
        # Reduce depth to 3 for faster response while debugging
        score, best_move = self.minimax(3, float('-inf'), float('inf'), True)
        print(f"Best move found: {best_move} with score {score}")
        
        if best_move:
            start, end = best_move
            print(f"Making move from {start} to {end}")
            
            # Make the move
            self.board[end[0]][end[1]] = self.board[start[0]][start[1]]
            self.board[start[0]][start[1]] = '.'
            self.update_display()
            
            # Check for win
            if self.check_win('B'):
                pygame.mixer.music.load(self.lose_sound)
                pygame.mixer.music.play()
                self.window.after(500, lambda: self.display_message_and_exit("AI wins! 😊"))
                return
            
            self.current_player = 'W'
        else:
            print("No valid moves found!")
            if self.check_win('W'):
                pygame.mixer.music.load(self.win_sound)
                pygame.mixer.music.play()
                self.window.after(500, lambda: self.display_message_and_exit("You win! 🎉"))
            else:
                pygame.mixer.music.load(self.lose_sound)
                pygame.mixer.music.play()
                self.window.after(500, lambda: self.display_message_and_exit("Stalemate! 🤝"))
        
    def display_message_and_exit(self, message):
        response = messagebox.askyesno("Game Over", f"{message}\nDo you want to continue?")
        if response:  # If the user chooses "Yes"
            self.start_new_game()
        else:  # If the user chooses "No"
            self.window.quit()

    def start_new_game(self):
        # Reset the game state and start a new game
        self.start_game()
        self.update_ui()
    
    def run(self):
        self.window.mainloop()

if __name__ == '__main__':
    game = HexapawnGUI()
    game.run()