import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from itertools import count
import pygame

class HexapawnGUI:
    def __init__(self):
        pygame.mixer.init()
        self.window = tk.Tk()
        self.window.title("Hexapawn")

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
        title = tk.Label(self.window, text="HEXAPAWN", font=('Arial', 30, 'bold'))
        title.pack(pady=20)

        # Description
        desc = tk.Label(self.window, 
                        text="Hexapawn is a mini chess-like game played on a 3x3 board where\n\n"
                            "- Each player starts with 3 pawns on opposite ends\n"
                            "- Pawns can move forward one square if unblocked\n"
                            "- Pawns can capture diagonally forward\n"
                            "- First player to either get a pawn to the opposite end, capture all opponent pawns, or block all opponent moves wins", 
                        font=('Times New Roman', 18), justify=tk.CENTER)
        desc.pack(pady=20)

        # Start button
        start_button = tk.Button(self.window, text="Start Game", 
                                command=self.start_game, 
                                font=('Arial', 14))
        start_button.pack(pady=20)

        self.gif_label = tk.Label(self.window)
        self.gif_label.pack(pady=20)
        self.hexapawn_gif = "hexapawn.gif"
        # Load and animate the GIF
        self.animate_gif(self.hexapawn_gif)

    def animate_gif(self, gif_path):
        gif = Image.open(gif_path)

        frames = []
        try:
            while True:
                frames.append(ImageTk.PhotoImage(gif.copy()))
                gif.seek(len(frames))  # Go to next frame
        except EOFError:
            pass  # End of frames

        def update(ind=0):
            frame = frames[ind]
            self.gif_label.configure(image=frame)
            ind = (ind + 1) % len(frames)  # Loop through frames
            self.window.after(100, update, ind)  # Adjust timing as needed

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
                button = tk.Button(self.window, width=10, height=5,
                                 command=lambda r=i, c=j: self.handle_click(r, c),
                                 font=('Helvatica', 80, 'bold'))
                button.grid(row=i, column=j)
                row.append(button)
            self.buttons.append(row)
        
        self.update_display()
    
    def update_display(self):
        for i in range(3):
            for j in range(3):
                text = self.board[i][j]
                if text == 'W':
                    self.buttons[i][j].config(text='♙', fg='#93908f', bg='gray')
                elif text == 'B':
                    self.buttons[i][j].config(text='♟', fg='black', bg='gray')
                else:
                    self.buttons[i][j].config(text='', bg='light gray')
    
    def handle_click(self, row, col):
        if self.current_player != 'W':  # Only allow clicks during human's turn
            return

        self.sounds['select']()  # Play selection sound

        if self.selected_piece is None:
            # Selecting a piece
            if self.board[row][col] == 'W':
                self.selected_piece = (row, col)
                self.buttons[row][col].config(bg='yellow')  # Highlight selected piece
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
        if self.check_win('B'):
            return 1000
        if self.check_win('W'):
            return -1000
            
        # Simple piece counting heuristic
        score = 0
        for row in self.board:
            for cell in row:
                if cell == 'B':
                    score += 1
                elif cell == 'W':
                    score -= 1
        return score
    
    def minimax(self, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.check_win('B') or self.check_win('W'):
            return self.evaluate(), None
        
        player = 'B' if maximizing_player else 'W'
        possible_moves = self.get_possible_moves(player)
        
        if not possible_moves:
            return self.evaluate(), None
        
        best_move = None
        if maximizing_player:
            max_eval = float('-inf')
            for start, end in possible_moves:
                captured_piece = self.board[end[0]][end[1]]
                self.make_move(start, end)
                
                eval, _ = self.minimax(depth - 1, alpha, beta, False)
                self.undo_move(start, end, captured_piece)
                
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
                
                if eval < min_eval:
                    min_eval = eval
                    best_move = (start, end)
                
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move
    
    def make_ai_move(self):
        _, best_move = self.minimax(4, float('-inf'), float('inf'), True)
        
        if best_move:
            start, end = best_move
            self.board[end[0]][end[1]] = self.board[start[0]][start[1]]
            self.board[start[0]][start[1]] = '.'
            self.update_display()
            
            if self.check_win('B'):
                self.window.after(500, lambda: self.display_message_and_exit("AI wins! 😊"))
                return
            
            self.current_player = 'W'
        else:
            pygame.mixer.music.load(self.lose_sound)
            pygame.mixer.music.play()
            self.window.after(500, lambda: self.display_message_and_exit("Stalemate! 🤝"))
            return
    
    def display_message_and_exit(self, message):
        messagebox.showinfo("Game Over", message)
        self.window.quit()
    
    def run(self):
        self.window.mainloop()

# Start the game
if __name__ == "__main__":
    game = HexapawnGUI()
    game.run()
