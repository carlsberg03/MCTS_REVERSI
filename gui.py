import pygame
from config import *
class GameGUI:
    """Handles the graphical user interface for the Reversi game."""
    
    def __init__(self):
        """Initialize the GUI."""
        pygame.init()
        
        # Setup display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('MCTS Reversi')
        
        # Load assets
        self.background = pygame.image.load(BACKGROUND_PATH)
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # Setup clock
        self.clock = pygame.time.Clock()
        
        # AI thinking progress
        self.ai_progress = 0.0
        self.ai_thinking = False
    
    def draw_board(self, board, player_tile, valid_moves=None):
        """Draw the game board with pieces and valid moves."""
        # Draw board background
        self.screen.fill(GRAY)
        self.screen.blit(self.background, (0, 0))
        
        # Draw pieces
        for x in range(len(board.grid)):
            for y in range(len(board.grid[x])):
                # Draw black pieces
                if board.grid[x][y] == BLACK_TILE:
                    pygame.draw.circle(
                        self.screen, 
                        BLACK, 
                        [CELL_SIZE // 2 + CELL_SIZE * x, CELL_SIZE // 2 + CELL_SIZE * y], 
                        PIECE_RADIUS, 
                        PIECE_RADIUS
                    )
                # Draw white pieces
                elif board.grid[x][y] == WHITE_TILE:
                    pygame.draw.circle(
                        self.screen, 
                        WHITE, 
                        [CELL_SIZE // 2 + CELL_SIZE * x, CELL_SIZE // 2 + CELL_SIZE * y], 
                        PIECE_RADIUS, 
                        PIECE_RADIUS
                    )
                # Draw valid move hints
                elif valid_moves and (x, y) in valid_moves:
                    pygame.draw.circle(
                        self.screen, 
                        GREEN, 
                        [CELL_SIZE // 2 + CELL_SIZE * x, CELL_SIZE // 2 + CELL_SIZE * y], 
                        HINT_RADIUS, 
                        HINT_RADIUS
                    )
    
    def draw_player_indicators(self, player_tile, computer_tile):
        """Draw indicators showing which color belongs to which player."""
        # Draw player label
        player_text = self.font.render("you", True, YELLOW)
        self.screen.blit(player_text, (870, 730))
        
        # Draw AI label
        ai_text = self.font.render("AI", True, YELLOW)
        self.screen.blit(ai_text, (880, 130))
        
        # Draw player color indicator
        player_color = BLACK if player_tile == BLACK_TILE else WHITE
        pygame.draw.circle(self.screen, player_color, [900, 700], HINT_RADIUS, HINT_RADIUS)
        
        # Draw AI color indicator
        ai_color = BLACK if computer_tile == BLACK_TILE else WHITE
        pygame.draw.circle(self.screen, ai_color, [900, 100], HINT_RADIUS, HINT_RADIUS)
    
    
    
    def draw_progress_bar(self):
        """Draw the AI thinking progress bar."""
        if self.ai_thinking:
            # Draw progress bar background
            pygame.draw.rect(
                self.screen, 
                LIGHT_BLUE, 
                [PROGRESS_BAR_X, PROGRESS_BAR_Y, PROGRESS_BAR_WIDTH, PROGRESS_BAR_HEIGHT], 
                border_radius=5
            )
            
            # Draw progress bar fill
            fill_width = int(PROGRESS_BAR_WIDTH * self.ai_progress)
            if fill_width > 0:
                pygame.draw.rect(
                    self.screen, 
                    BLUE, 
                    [PROGRESS_BAR_X, PROGRESS_BAR_Y, fill_width, PROGRESS_BAR_HEIGHT], 
                    border_radius=5
                )
            
            # Draw "AI Thinking" text
            thinking_text = self.small_font.render("AI Thinking...", True, BLACK)
            self.screen.blit(thinking_text, (PROGRESS_BAR_X + 60, PROGRESS_BAR_Y - 25))
    
    def update_ai_progress(self, progress):
        """Update the AI thinking progress."""
        self.ai_progress = progress
    
    def set_ai_thinking(self, is_thinking):
        """Set whether AI is currently thinking."""
        self.ai_thinking = is_thinking
        if not is_thinking:
            self.ai_progress = 0.0
    
    def draw_game_over(self, player_score, computer_score):
        """Draw the game over message with final score."""
        if player_score > computer_score:
            result = "Win"
        elif player_score == computer_score:
            result = "Draw"
        else:
            result = "Lose"
            
        output_text = f"{result}. {player_score}:{computer_score}"
        text_surface = self.font.render(output_text, True, BLACK, YELLOW)
        text_rect = text_surface.get_rect()
        text_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.screen.blit(text_surface, text_rect)
    
    def update_display(self):
        """Update the display."""
        pygame.display.update()
        self.clock.tick(TICK_RATE)
    
    def get_clicked_cell(self):
        """Get the board cell coordinates from a mouse click."""
        x, y = pygame.mouse.get_pos()
        col = x // CELL_SIZE
        row = y // CELL_SIZE
        return col, row
    
    def quit(self):
        """Clean up and quit pygame."""
        pygame.quit()