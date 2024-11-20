import tkinter as tk
from tkinter import messagebox, simpledialog
import random

class HexapawnGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Hexapawn")
        
        # Set the window to 600x600 and center it on the screen
        window_width = 600
        window_height = 600
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        center_x = (screen_width // 2) - (window_width // 2)
        center_y = (screen_height // 2) - (window_height // 2)
        self.window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        # Sound simulation with simple beep
        self.sounds = {
            'select': lambda: self.window.bell(),
            'move': lambda: self.window.bell(),
            'win': lambda: [self.window.bell() for _ in range(3)],  # Human win sound (3 beeps)
            'lose': lambda: [self.window.bell() for _ in range(5)]   # AI win sound (5 beeps)
        }
        
        # Start page
        self.create_start_page()
    
    def create_start_page(self):
        # Clear any existing widgets
        for widget in self.window.winfo_children():
            widget.destroy()
        
        # Title
        title = tk.Label(self.window, text="HEXAPAWN", font=('Arial', 24, 'bold'))
        title.pack(pady=20)
        
        # Description
        desc = tk.Label(self.window, 
                        text="A strategic mini chess variant\n\n"
                             "Rules:\n"
                             "- Move pawns forward or diagonally to capture\n"
                             "- Win by reaching opposite end or capturing all opponent's pawns", 
                        font=('Arial', 12), justify=tk.CENTER)
        desc.pack(pady=20)
        
        # Start button
        start_button = tk.Button(self.window, text="Start Game", 
                                 command=self.start_game, 
                                 font=('Arial', 14))
        start_button.pack(pady=20)
    
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
            self.window.grid_rowconfigure(i, weight=1)
            row = []
            for j in range(3):
                self.window.grid_columnconfigure(j, weight=1)
                button = tk.Button(self.window, width=10, height=5,
                                 command=lambda r=i, c=j: self.handle_click(r, c),
                                 font=('Arial', 80, 'bold'))
                button.grid(row=i, column=j)
                row.append(button)
            self.buttons.append(row)
        
        self.update_display()
    
    def update_display(self):
        for i in range(3):
            for j in range(3):
                text = self.board[i][j]
                if text == 'W':
                    color = 'light gray' if (i, j) != self.selected_piece else 'pale goldenrod'
                    self.buttons[i][j].config(text='♙', fg='white', bg=color)
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
                self.update_display()  # Highlight selected piece
        else:
            # Moving a piece
            start_row, start_col = self.selected_piece
            if self.is_valid_move(start_row, start_col, row, col):
                self.sounds['move']()  # Play move sound
                # Make the move
                self.board[row][col] = self.board[start_row][start_col]
                self.board[start_row][start_col] = '.'
                self.selected_piece = None
                self.update_display()
                
                if self.check_win('W'):
                    self.sounds['win']()  # Play human win sound
                    messagebox.showinfo("Game Over", "You win! 🎉")
                    self.create_start_page()
                    return
                
                # AI's turn
                self.current_player = 'B'
                self.make_ai_move()
            else:
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
        _, best_move = self.minimax(depth=3, alpha=float('-inf'), beta=float('inf'), maximizing_player=True)
        if best_move:
            start, end = best_move
            self.make_move(start, end)
            self.update_display()
            
            if self.check_win('B'):
                self.sounds['lose']()  # Play AI win sound
                messagebox.showinfo("Game Over", "AI wins! 💻")
                self.create_start_page()
                return
        
        self.current_player = 'W'  # Switch back to human
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    gui = HexapawnGUI()
    gui.run()

