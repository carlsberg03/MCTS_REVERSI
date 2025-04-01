import pygame
import sys
import random
import threading
from pygame.locals import *

from config import BLACK_TILE, WHITE_TILE, DIFFICULTY
from board import Board
from ai import MCTSAI
from gui import GameGUI

def who_goes_first():
    """Randomly determine who goes first."""
    if random.randint(0, 1) == 0:
        print("AI goes first")
        return 1
    else:
        print("Player goes first")
        return 0

def ai_move_thread(ai, board, computer_tile, gui, result_queue):
    """在单独的线程中运行AI思考过程"""
    move = ai.get_best_move(board, lambda progress: gui.update_ai_progress(progress))
    result_queue.append(move)

def main():
    """Main game function."""
    # Initialize game components
    board = Board()
    gui = GameGUI()
    
    # Determine who goes first
    turn = who_goes_first()
    
    # Assign colors
    if turn == 0:  # Player goes first
        player_tile = BLACK_TILE
        computer_tile = WHITE_TILE
    else:  # AI goes first
        player_tile = WHITE_TILE
        computer_tile = BLACK_TILE
    
    # Initialize AI
    ai = MCTSAI(difficulty=DIFFICULTY, player_color=player_tile)
    
    # Game state variables
    game_over = False
    
    # AI thinking thread variables
    ai_thinking = False
    ai_move_result = []
    ai_thread = None
    
    # Game loop
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                if ai_thread and ai_thread.is_alive():
                    # 等待AI线程完成，避免退出时的异常
                    ai_thread.join(timeout=0.5)
                gui.quit()
                sys.exit()
                
            # Handle player move
            if (not game_over and 
                turn == 0 and 
                event.type == MOUSEBUTTONDOWN and 
                event.button == 1):
                
                # Get clicked cell
                col, row = gui.get_clicked_cell()
                
                # Make move if valid
                if board.make_move(player_tile, col, row):
                    # Check if AI can move next
                    if board.get_valid_moves(computer_tile):
                        turn = 1  # AI's turn
                    elif not board.get_valid_moves(player_tile):
                        game_over = True  # No moves available for either player
            
            # Debug key to force AI move
            if event.type == KEYUP and event.key == K_q:
                turn = 1
        
        # Handle AI move
        if not game_over and turn == 1:
            if not ai_thinking:
                # Start AI thinking in a separate thread
                ai_thinking = True
                gui.set_ai_thinking(True)
                ai_move_result.clear()
                ai_thread = threading.Thread(
                    target=ai_move_thread,
                    args=(ai, board, computer_tile, gui, ai_move_result)
                )
                ai_thread.daemon = True  # 设置为守护线程，这样当主程序退出时，线程也会退出
                ai_thread.start()
            
            elif ai_move_result:  # AI has finished thinking
                move = ai_move_result[0]
                ai_thinking = False
                gui.set_ai_thinking(False)
                
                if move:
                    x, y = move
                    board.make_move(computer_tile, x, y)
                
                # Check if player can move next
                if board.get_valid_moves(player_tile):
                    turn = 0  # Player's turn
                elif not board.get_valid_moves(computer_tile):
                    game_over = True  # No moves available for either player
        
        # Get current valid moves for the player
        valid_moves = board.get_valid_moves(player_tile) if turn == 0 else []
        
        # Draw game state
        gui.draw_board(board, player_tile, valid_moves)
        gui.draw_player_indicators(player_tile, computer_tile)
        gui.draw_progress_bar()
        gui.draw_progress_bar()  # 绘制AI思考进度条
        
        # Handle game over state
        if game_over:
            scores = board.get_score()
            player_score = scores[player_tile]
            computer_score = scores[computer_tile]
            gui.draw_game_over(player_score, computer_score)
        
        # Update display
        gui.update_display()

if __name__ == '__main__':
    main()