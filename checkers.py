import pygame
import sys
from pygame import gfxdraw
import random
import time
import threading
from copy import deepcopy

# Initialize pygame module
pygame.init()

# Game constants
WIDTH, HEIGHT = 900, 800  # Increased width to accommodate side panel
BOARD_SIZE = 700  # Actual board size
ROWS, COLS = 8, 8
SQUARE_SIZE = BOARD_SIZE // COLS
BOARD_OFFSET_X = 50  # Offset from left edge
BOARD_OFFSET_Y = 80  # Offset from top edge
SIDE_PANEL_X = BOARD_OFFSET_X + BOARD_SIZE + 20  # Start of side panel

# Colors
RED = (255, 50, 50)
WHITE = (240, 240, 240)
BLACK = (30, 30, 30)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (180, 180, 180)
BLUE = (0, 150, 255)
GREEN = (50, 255, 50)
GOLD = (255, 215, 0)
GLOW_BLUE = (0, 200, 255, 100)
PANEL_BG = (40, 40, 50)

# Fonts
FONT_LARGE = pygame.font.SysFont('Arial', 48, bold=True)
FONT_MEDIUM = pygame.font.SysFont('Arial', 32)
FONT_SMALL = pygame.font.SysFont('Arial', 22)
FONT_TINY = pygame.font.SysFont('Arial', 18)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI CHECKERS MASTER")

class Piece:
    PADDING = 15
    OUTLINE = 3
    GLOW_SIZE = 20
    
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()
        self.selected = False

    def calc_pos(self):
        """Calculate the piece's position on the board"""
        self.x = BOARD_OFFSET_X + SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = BOARD_OFFSET_Y + SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def make_king(self):
        """Promote the piece to a king"""
        self.king = True

    def draw(self, win):
        """Draw the piece on the board with enhanced visuals"""
        radius = SQUARE_SIZE // 2 - self.PADDING
        
        # Draw glow effect if selected
        if self.selected:
            glow_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, GLOW_BLUE, 
                             (SQUARE_SIZE//2, SQUARE_SIZE//2), 
                             radius + self.GLOW_SIZE)
            win.blit(glow_surface, (self.x - SQUARE_SIZE//2, self.y - SQUARE_SIZE//2))
        
        # Draw piece with gradient effect
        for i in range(5, 0, -1):
            shade = 20 * i
            if self.color == RED:
                draw_color = (min(255, self.color[0] + shade), 
                             max(0, self.color[1] - shade), 
                             max(0, self.color[2] - shade))
            else:
                draw_color = (min(255, self.color[0] + shade), 
                             min(255, self.color[1] + shade), 
                             min(255, self.color[2] + shade))
            
            pygame.draw.circle(win, draw_color, (self.x, self.y), radius - (5 - i))
        
        # Draw outline
        pygame.draw.circle(win, BLACK, (self.x, self.y), radius + 1, 1)
        
        # Draw king crown
        if self.king:
            crown_radius = radius // 2
            pygame.draw.circle(win, GOLD, (self.x, self.y), crown_radius)
            pygame.draw.circle(win, BLACK, (self.x, self.y), crown_radius, 1)

    def move(self, row, col):
        """Move the piece to a new position"""
        self.row = row
        self.col = col
        self.calc_pos()
        
    def __repr__(self):
        return f"Piece({self.row}, {self.col}, {self.color}, king={self.king})"
        
    def copy(self):
        """Create a deep copy of the piece"""
        copy = Piece(self.row, self.col, self.color)
        copy.king = self.king
        return copy

class Board:
    def __init__(self):
        self.board = []
        self.red_left = self.white_left = 12
        self.red_kings = self.white_kings = 0
        self.create_board()

    def draw_squares(self, win):
        """Draw the checkerboard pattern with enhanced visuals"""
        # Draw board background
        pygame.draw.rect(win, DARK_GRAY, 
                       (BOARD_OFFSET_X - 10, BOARD_OFFSET_Y - 10, 
                        BOARD_SIZE + 20, BOARD_SIZE + 20), 
                        border_radius=5)
        
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 0:
                    color = LIGHT_GRAY
                else:
                    color = BLACK
                
                # Draw square with subtle level effect
                pygame.draw.rect(win, color, 
                               (BOARD_OFFSET_X + col * SQUARE_SIZE, 
                                BOARD_OFFSET_Y + row * SQUARE_SIZE, 
                                SQUARE_SIZE, SQUARE_SIZE))
                
                # Add subtle grid lines
                if row == 0 or col == 0:
                    pygame.draw.line(win, (color[0]//2, color[1]//2, color[2]//2), 
                                     (BOARD_OFFSET_X + col * SQUARE_SIZE, BOARD_OFFSET_Y + row * SQUARE_SIZE), 
                                     (BOARD_OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE, BOARD_OFFSET_Y + row * SQUARE_SIZE), 1)
                    pygame.draw.line(win, (color[0]//2, color[1]//2, color[2]//2), 
                                     (BOARD_OFFSET_X + col * SQUARE_SIZE, BOARD_OFFSET_Y + row * SQUARE_SIZE), 
                                     (BOARD_OFFSET_X + col * SQUARE_SIZE, BOARD_OFFSET_Y + row * SQUARE_SIZE + SQUARE_SIZE), 1)

    def create_board(self):
        """Initialize the board with pieces in starting positions"""
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if (row + col) % 2 == 1:
                    if row < 3:
                        self.board[row].append(Piece(row, col, WHITE))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, RED))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw(self, win):
        """Draw the entire board"""
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def move(self, piece, row, col):
        """Move a piece and handle king promotion"""
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)
        
        # Check for king promotion
        if row == 0 and piece.color == RED:
            if not piece.king:
                piece.make_king()
                self.red_kings += 1
        elif row == ROWS - 1 and piece.color == WHITE:
            if not piece.king:
                piece.make_king()
                self.white_kings += 1

    def get_piece(self, row, col):
        """Get piece at specific position"""
        if 0 <= row < ROWS and 0 <= col < COLS:
            return self.board[row][col]
        return None

    def remove(self, pieces):
        """Remove captured pieces from the board"""
        for piece in pieces:
            if piece != 0:
                self.board[piece.row][piece.col] = 0
                if piece.color == RED:
                    self.red_left -= 1
                else:
                    self.white_left -= 1
                    
    def copy(self):
        """Create a deep copy of the board"""
        new_board = Board()
        new_board.board = []
        new_board.red_left = self.red_left
        new_board.white_left = self.white_left
        new_board.red_kings = self.red_kings
        new_board.white_kings = self.white_kings
        
        for row in range(ROWS):
            new_board.board.append([])
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    new_board.board[row].append(piece.copy())
                else:
                    new_board.board[row].append(0)
                    
        return new_board
        
    def get_all_pieces(self, color):
        """Get all pieces of a specific color"""
        pieces = []
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces
        
    def evaluate(self):
        """Evaluate the board state (positive is good for RED, negative for WHITE)"""
        return (self.red_left - self.white_left) + (self.red_kings * 0.5 - self.white_kings * 0.5)

class Game:
    def __init__(self, win):
        self.win = win
        self.board = Board()
        self.turn = RED
        self.selected = None
        self.valid_moves = {}
        self.game_over = False
        self.winner = None
        self.turn_indicator_time = 0
        self.clock = pygame.time.Clock()
        self.title_glow = 0
        self.title_glow_dir = 1
        
        # Monte Carlo simulation variables
        self.monte_carlo_running = False
        self.monte_carlo_results = {"RED": 0, "WHITE": 0, "DRAW": 0}
        self.monte_carlo_total = 0
        self.monte_carlo_thread = None
        self.auto_monte_carlo = True  # Auto-run Monte Carlo after each move
        self.simulation_speed = 500  # Number of simulations to run

    def update(self):
        """Update the game display"""
        self.clock.tick(60)
        self.draw_background()
        self.board.draw(self.win)
        self.draw_valid_moves()
        self.draw_side_panel()
        self.draw_ui()
        pygame.display.update()

    def draw_background(self):
        """Draw animated background elements"""
        # Fill background
        self.win.fill((30, 30, 40))
        
        # Animate title glow
        self.title_glow += 0.05 * self.title_glow_dir
        if self.title_glow > 1 or self.title_glow < 0:
            self.title_glow_dir *= -1
        
        # Draw glowing title
        title_text = FONT_LARGE.render("AI CHECKERS MASTER", True, 
                                     (0, 200 + int(55 * self.title_glow), 
                                     255))
        title_rect = title_text.get_rect(center=(WIDTH//2, 40))
        
        # Create glow effect
        glow_surface = pygame.Surface((title_rect.width + 40, title_rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (0, 100, 150, 30), 
                         (0, 0, title_rect.width + 40, title_rect.height + 20), 
                         border_radius=10)
        self.win.blit(glow_surface, (title_rect.x - 20, title_rect.y - 10))
        self.win.blit(title_text, title_rect)

    def draw_side_panel(self):
        """Draw side panel with Monte Carlo results"""
        # Draw panel background
        panel_rect = pygame.Rect(SIDE_PANEL_X, BOARD_OFFSET_Y, WIDTH - SIDE_PANEL_X - 20, BOARD_SIZE)
        pygame.draw.rect(self.win, PANEL_BG, panel_rect, border_radius=10)
        
        # Draw panel title
        panel_title = FONT_MEDIUM.render("Win Probability", True, WHITE)
        self.win.blit(panel_title, (SIDE_PANEL_X + 10, BOARD_OFFSET_Y + 20))
        
        # Draw separator line
        pygame.draw.line(self.win, LIGHT_GRAY, 
                       (SIDE_PANEL_X + 10, BOARD_OFFSET_Y + 60), 
                       (WIDTH - 30, BOARD_OFFSET_Y + 60), 2)
        
        # Draw Monte Carlo results
        y_offset = BOARD_OFFSET_Y + 80
        
        if self.monte_carlo_total > 0:
            # Calculate percentages
            red_pct = (self.monte_carlo_results["RED"] / self.monte_carlo_total) * 100
            white_pct = (self.monte_carlo_results["WHITE"] / self.monte_carlo_total) * 100
            draw_pct = (self.monte_carlo_results["DRAW"] / self.monte_carlo_total) * 100
            
            # Draw bars
            self.draw_probability_bar("RED", red_pct, y_offset)
            self.draw_probability_bar("WHITE", white_pct, y_offset + 80)
            self.draw_probability_bar("DRAW", draw_pct, y_offset + 160)
            
            # Show total simulations
            total_text = FONT_SMALL.render(f"Simulations: {self.monte_carlo_total}", True, LIGHT_GRAY)
            self.win.blit(total_text, (SIDE_PANEL_X + 10, y_offset + 240))
            
            # Show loading animation if simulation is running
            if self.monte_carlo_running:
                dots = "." * (int(time.time() * 2) % 4)
                running_text = FONT_SMALL.render(f"Simulating{dots}", True, GREEN)
                self.win.blit(running_text, (SIDE_PANEL_X + 10, y_offset + 270))
        else:
            # Show waiting message
            if self.monte_carlo_running:
                dots = "." * (int(time.time() * 2) % 4)
                waiting_text = FONT_MEDIUM.render(f"Calculating{dots}", True, BLUE)
                self.win.blit(waiting_text, (SIDE_PANEL_X + 20, y_offset + 100))
            else:
                waiting_text = FONT_MEDIUM.render("Waiting for move", True, LIGHT_GRAY)
                self.win.blit(waiting_text, (SIDE_PANEL_X + 10, y_offset + 100))

    def draw_probability_bar(self, player, percentage, y_position):
        """Draw a probability bar for a player"""
        # Set color based on player
        if player == "RED":
            color = RED
            text = "RED"
        elif player == "WHITE":
            color = WHITE
            text = "WHITE"
        else:
            color = LIGHT_GRAY
            text = "DRAW"
            
        # Draw label
        label = FONT_SMALL.render(text, True, color)
        self.win.blit(label, (SIDE_PANEL_X + 10, y_position))
        
        # Draw percentage
        pct_text = FONT_SMALL.render(f"{percentage:.1f}%", True, color)
        self.win.blit(pct_text, (SIDE_PANEL_X + 10, y_position + 25))
        
        # Draw bar background
        bar_width = WIDTH - SIDE_PANEL_X - 40
        pygame.draw.rect(self.win, (60, 60, 70), 
                       (SIDE_PANEL_X + 10, y_position + 50, 
                        bar_width, 20), 
                        border_radius=5)
        
        # Draw filled bar
        fill_width = int((percentage / 100) * bar_width)
        if fill_width > 0:
            pygame.draw.rect(self.win, color, 
                           (SIDE_PANEL_X + 10, y_position + 50, 
                            fill_width, 20), 
                            border_radius=5)

    def draw_ui(self):
        """Draw user interface elements"""
        # Draw turn indicator
        turn_text = "RED'S TURN" if self.turn == RED else "WHITE'S TURN"
        text_color = RED if self.turn == RED else WHITE
        text = FONT_MEDIUM.render(turn_text, True, text_color)
        text_rect = text.get_rect(center=(BOARD_OFFSET_X + BOARD_SIZE//2, HEIGHT - 40))
        
        # Draw background for turn indicator
        pygame.draw.rect(self.win, BLACK, 
                       (text_rect.x - 20, text_rect.y - 10, 
                        text_rect.width + 40, text_rect.height + 20), 
                       border_radius=10)
        self.win.blit(text, text_rect)
        
        # Draw piece counters
        red_text = FONT_SMALL.render(f"RED: {self.board.red_left}", True, RED)
        white_text = FONT_SMALL.render(f"WHITE: {self.board.white_left}", True, WHITE)
        self.win.blit(red_text, (BOARD_OFFSET_X, BOARD_OFFSET_Y - 30))
        self.win.blit(white_text, (BOARD_OFFSET_X + BOARD_SIZE - white_text.get_width(), BOARD_OFFSET_Y - 30))
        
        # Draw winner message
        if self.game_over:
            self.display_winner()

    def draw_selected(self):
        """Highlight the selected piece"""
        if self.selected:
            self.selected.selected = True

    def draw_valid_moves(self):
        """Highlight valid moves for the selected piece with animation"""
        current_time = pygame.time.get_ticks()
        pulse_size = int(5 * (0.5 + 0.5 * abs(pygame.math.Vector2(0, 1).rotate(current_time / 5).y)))
        
        for move, skipped in self.valid_moves.items():
            row, col = move
            center_x = BOARD_OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = BOARD_OFFSET_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2
            
            # Draw pulsing green circle
            pygame.draw.circle(self.win, GREEN, (center_x, center_y), 15 + pulse_size)
            pygame.draw.circle(self.win, BLACK, (center_x, center_y), 15 + pulse_size, 1)

    def get_valid_moves(self, piece):
        """Calculate all valid moves for a piece"""
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == RED or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
        
        if piece.color == WHITE or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))
        
        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break
            
            current = self.board.get_piece(r, left)
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last
                
                if last:
                    if step == -1:
                        row = max(r - 3, -1)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]
            
            left -= 1
        
        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break
            
            current = self.board.get_piece(r, right)
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last
                
                if last:
                    if step == -1:
                        row = max(r - 3, -1)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]
            
            right += 1
        
        return moves

    def get_row_col_from_mouse(self, pos):
        """Convert mouse position to board row and column"""
        x, y = pos
        
        # Check if click is within board boundaries
        if (BOARD_OFFSET_X <= x <= BOARD_OFFSET_X + BOARD_SIZE and 
            BOARD_OFFSET_Y <= y <= BOARD_OFFSET_Y + BOARD_SIZE):
            row = (y - BOARD_OFFSET_Y) // SQUARE_SIZE
            col = (x - BOARD_OFFSET_X) // SQUARE_SIZE
            if 0 <= row < ROWS and 0 <= col < COLS:
                return row, col
        
        return None

    def select(self, pos):
        """Handle piece selection and movement"""
        # Convert mouse position to board coordinates
        result = self.get_row_col_from_mouse(pos)
        if not result:  # Click was outside the board
            return False
            
        row, col = result
        
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected.selected = False
                self.selected = None
                self.valid_moves = {}
                self.select(pos)  # Try selecting a new piece
        else:
            piece = self.board.get_piece(row, col)
            if piece != 0 and piece.color == self.turn:
                self.selected = piece
                self.selected.selected = True
                self.valid_moves = self.get_valid_moves(piece)
                return True
            
        return False

    def _move(self, row, col):
        """Move the selected piece to the specified position"""
        piece = self.board.get_piece(row, col)
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            self.change_turn()
            return True
        return False

    def change_turn(self):
        """Switch to the other player's turn"""
        if self.selected:
            self.selected.selected = False
        self.valid_moves = {}
        self.selected = None
        self.turn = WHITE if self.turn == RED else RED
        self.turn_indicator_time = pygame.time.get_ticks()
        self.check_winner()
        
        # Reset Monte Carlo results when turn changes
        self.monte_carlo_results = {"RED": 0, "WHITE": 0, "DRAW": 0}
        self.monte_carlo_total = 0
        
        # Auto-run Monte Carlo simulation if enabled and game is not over
        if self.auto_monte_carlo and not self.game_over:
            self.run_monte_carlo_simulation()

    def check_winner(self):
        """Check for a winner"""
        red_has_moves = False
        white_has_moves = False
        
        # Check if players have any valid moves
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board.get_piece(row, col)
                if piece and piece.color == RED and self.get_valid_moves(piece):
                    red_has_moves = True
                elif piece and piece.color == WHITE and self.get_valid_moves(piece):
                    white_has_moves = True
        
        if not red_has_moves or self.board.red_left <= 0:
            self.game_over = True
            self.winner = "WHITE WINS!"
        elif not white_has_moves or self.board.white_left <= 0:
            self.game_over = True
            self.winner = "RED WINS!"

    def display_winner(self):
        """Display winner message with animation"""
        if self.game_over:
            # Create semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.win.blit(overlay, (0, 0))
            
            # Draw winner text with glow effect
            text = FONT_LARGE.render(self.winner, True, GOLD)
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
            
            # Create glow
            glow_size = int(10 * abs(pygame.math.Vector2(0, 1).rotate(pygame.time.get_ticks() / 3).y))
            for i in range(glow_size, 0, -2):
                glow_color = (255, 215, 0, 10 + i * 2)
                glow_text = FONT_LARGE.render(self.winner, True, glow_color)
                self.win.blit(glow_text, (text_rect.x, text_rect.y - glow_size + i))

            self.win.blit(text, text_rect)
            
            # Draw restart prompt
            restart_text = FONT_MEDIUM.render("Click to play again", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))
            self.win.blit(restart_text, restart_rect)
            
    def run_monte_carlo_simulation(self):
        """Run Monte Carlo simulation in a separate thread"""
        if self.monte_carlo_running:
            return
            
        self.monte_carlo_running = True
        self.monte_carlo_thread = threading.Thread(target=self._monte_carlo_worker)
        self.monte_carlo_thread.daemon = True
        self.monte_carlo_thread.start()
        
    def _monte_carlo_worker(self):
        """Worker function for Monte Carlo simulation"""
        try:
            # Reset results
            self.monte_carlo_results = {"RED": 0, "WHITE": 0, "DRAW": 0}
            self.monte_carlo_total = 0
            
            # Run simulations
            num_simulations = self.simulation_speed
            max_moves = 200  # Prevent infinite games
            
            for _ in range(num_simulations):
                # Create a copy of the current game state
                board_copy = self.board.copy()
                current_turn = self.turn
                move_count = 0
                
                # Play a random game until completion
                while True:
                    # Check for winner
                    red_pieces = board_copy.get_all_pieces(RED)
                    white_pieces = board_copy.get_all_pieces(WHITE)
                    
                    if not red_pieces:
                        self.monte_carlo_results["WHITE"] += 1
                        break
                    elif not white_pieces:
                        self.monte_carlo_results["RED"] += 1
                        break
                    
                    # Check for moves
                    valid_moves_exist = False
                    pieces = board_copy.get_all_pieces(current_turn)
                    random.shuffle(pieces)  # Randomize piece selection
                    
                    for piece in pieces:
                        moves = self._get_valid_moves_for_simulation(board_copy, piece)
                        if moves:
                            valid_moves_exist = True
                            # Choose a random move
                            move_pos, skipped = random.choice(list(moves.items()))
                            
                            # Execute the move
                            row, col = move_pos
                            board_copy.move(piece, row, col)
                            if skipped:
                                board_copy.remove(skipped)
                            break
                    
                    if not valid_moves_exist:
                        # Current player has no valid moves
                        if current_turn == RED:
                            self.monte_carlo_results["WHITE"] += 1
                        else:
                            self.monte_carlo_results["RED"] += 1
                        break
                    
                    # Switch turn
                    current_turn = WHITE if current_turn == RED else RED
                    move_count += 1
                    
                    # Check for draw (too many moves)
                    if move_count >= max_moves:
                        self.monte_carlo_results["DRAW"] += 1
                        break
                
                # Update total
                self.monte_carlo_total += 1
                
                # Update every 10 simulations to show progress
                if self.monte_carlo_total % 10 == 0:
                    time.sleep(0.01)  # Small delay to allow UI updates
        finally:
            self.monte_carlo_running = False
    
    def _get_valid_moves_for_simulation(self, board, piece):
        """Get valid moves for a piece in simulation (without modifying the game state)"""
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == RED or piece.king:
            moves.update(self._traverse_left_sim(board, row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right_sim(board, row - 1, max(row - 3, -1), -1, piece.color, right))
        
        if piece.color == WHITE or piece.king:
            moves.update(self._traverse_left_sim(board, row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right_sim(board, row + 1, min(row + 3, ROWS), 1, piece.color, right))
        
        return moves
        
    def _traverse_left_sim(self, board, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break
            
            current = board.get_piece(r, left)
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last
                
                if last:
                    if step == -1:
                        row = max(r - 3, -1)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left_sim(board, r + step, row, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right_sim(board, r + step, row, step, color, left + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]
            
            left -= 1
        
        return moves

    def _traverse_right_sim(self, board, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break
            
            current = board.get_piece(r, right)
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last
                
                if last:
                    if step == -1:
                        row = max(r - 3, -1)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left_sim(board, r + step, row, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right_sim(board, r + step, row, step, color, right + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]
            
            right += 1
        
        return moves

def main():
    """Main game loop"""
    game = Game(screen)
    running = True
    
    # Run initial Monte Carlo simulation
    game.run_monte_carlo_simulation()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                if not game.game_over:
                    game.select(pos)
                else:
                    # Restart game if clicked after game over
                    game = Game(screen)
                    # Run initial Monte Carlo simulation for new game
                    game.run_monte_carlo_simulation()
            
            if event.type == pygame.USEREVENT and game.game_over:
                running = False
        
        game.update()
    
    pygame.quit()
    sys.exit()

if __name__== "__main__":
    main()