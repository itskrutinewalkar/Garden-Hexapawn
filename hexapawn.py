import tkinter as tk
from tkinter import messagebox

class HexapawnGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Hexapawn")
        
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
            for j in range(3):
                button = tk.Button(self.window, width=10, height=5,
                                 command=lambda r=i, c=j: self.handle_click(r, c),
                                 font=('Arial', 14, 'bold'))
                button.grid(row=i, column=j)
                row.append(button)
            self.buttons.append(row)
        
        self.update_display()
    
    def update_display(self):
        for i in range(3):
            for j in range(3):
                text = self.board[i][j]
                if text == 'W':
                    self.buttons[i][j].config(text='♙', fg='white', bg='gray')
                elif text == 'B':
                    self.buttons[i][j].config(text='♟', fg='black', bg='gray')
                else:
                    self.buttons[i][j].config(text='', bg='light gray')
    
    def handle_click(self, row, col):
        if self.current_player != 'W':  # Only allow clicks during human's turn
            return
            
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
                    messagebox.showinfo("Game Over", "You win! 🎉")
                    self.window.quit()
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
        _, best_move = self.minimax(4, float('-inf'), float('inf'), True)
        
        if best_move:
            start, end = best_move
            self.board[end[0]][end[1]] = self.board[start[0]][start[1]]
            self.board[start[0]][start[1]] = '.'
            self.update_display()
            
            if self.check_win('B'):
                messagebox.showinfo("Game Over", "AI wins! 😊")
                self.window.quit()
                return
            
            self.current_player = 'W'
        else:
            messagebox.showinfo("Game Over", "Stalemate! 🤝")
            self.window.quit()
    
    def run(self):
        self.window.mainloop()

# Start the game
if __name__ == "__main__":
    game = HexapawnGUI()
    game.run()
