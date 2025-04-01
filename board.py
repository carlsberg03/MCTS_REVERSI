from config import BOARD_SIZE, BLACK_TILE, WHITE_TILE, EMPTY_TILE

class Board:
    """Represents the Reversi game board and its logic."""
    
    def __init__(self):
        """Initialize a new board."""
        self.reset()
    
    def reset(self):
        """Reset the board to the starting position."""
        self.grid = [[EMPTY_TILE for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        # Starting pieces
        center = BOARD_SIZE // 2
        self.grid[center-1][center-1] = BLACK_TILE
        self.grid[center-1][center] = WHITE_TILE
        self.grid[center][center-1] = WHITE_TILE
        self.grid[center][center] = BLACK_TILE
    
    def get_copy(self):
        """Return a deep copy of the current board."""
        new_board = Board()
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                new_board.grid[x][y] = self.grid[x][y]
        return new_board
    
    def is_on_board(self, x, y):
        """Check if the coordinates are within the board boundaries."""
        return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE
    
    def is_corner(self, x, y):
        """Check if the coordinates represent a corner position."""
        corners = [(0, 0), (0, BOARD_SIZE-1), (BOARD_SIZE-1, 0), (BOARD_SIZE-1, BOARD_SIZE-1)]
        return (x, y) in corners
    
    def get_valid_moves(self, color):
        """Get all valid moves for the given color."""
        valid_moves = []
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                if self.is_valid_move(color, x, y):
                    valid_moves.append((x, y))
        return valid_moves
    
    def is_valid_move(self, color, x, y):
        """Check if placing a piece at (x, y) is a valid move for the given color."""
        if not self.is_on_board(x, y) or self.grid[x][y] != EMPTY_TILE:
            return False
            
        # Temporarily place the piece
        self.grid[x][y] = color
        
        # Determine opponent's color
        opponent = WHITE_TILE if color == BLACK_TILE else BLACK_TILE
        
        # Check in all 8 directions
        flippable_pieces = []
        for dx, dy in [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]:
            temp_flips = []
            curr_x, curr_y = x + dx, y + dy
            
            # Continue in this direction as long as we find opponent's pieces
            while (self.is_on_board(curr_x, curr_y) and 
                   self.grid[curr_x][curr_y] == opponent):
                temp_flips.append((curr_x, curr_y))
                curr_x += dx
                curr_y += dy
            
            # If we found our own piece at the end, these pieces can be flipped
            if (self.is_on_board(curr_x, curr_y) and 
                self.grid[curr_x][curr_y] == color):
                flippable_pieces.extend(temp_flips)
        
        # Restore the empty space
        self.grid[x][y] = EMPTY_TILE
        
        # Valid move if any pieces would be flipped
        return flippable_pieces if flippable_pieces else False
    
    def make_move(self, color, x, y):
        """Make a move at the given position if valid."""
        flippable_pieces = self.is_valid_move(color, x, y)
        
        if not flippable_pieces:
            return False
            
        # Place the piece and flip opponent's pieces
        self.grid[x][y] = color
        for flip_x, flip_y in flippable_pieces:
            self.grid[flip_x][flip_y] = color
            
        return True
    
    def get_score(self):
        """Get the current score (count of pieces for each player)."""
        black_count = 0
        white_count = 0
        
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                if self.grid[x][y] == BLACK_TILE:
                    black_count += 1
                elif self.grid[x][y] == WHITE_TILE:
                    white_count += 1
                    
        return {BLACK_TILE: black_count, WHITE_TILE: white_count}
    
    def is_game_over(self):
        """Check if the game is over."""
        # Game ends if board is full
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                if self.grid[x][y] == EMPTY_TILE:
                    # Still have empty cells, check if any player can move
                    if (self.get_valid_moves(BLACK_TILE) or 
                        self.get_valid_moves(WHITE_TILE)):
                        return False
                    else:
                        return True  # No valid moves for either player
        
        # Board is full
        return True