import math
import random
import sys
from board import Board
from config import *

class Node:
    """Represents a node in the MCTS tree."""
    
    def __init__(self, board, parent=None, action=None, color=""):
        """Initialize a new MCTS node."""
        self.visits = 0  # Visit count
        self.reward = 0.0  # Win count
        self.board = board  # Board state
        self.children = []  # Child nodes
        self.parent = parent  # Parent node
        self.action = action  # Action that led to this state
        self.color = color  # Player color for this node
    
    def get_ucb(self):
        """Calculate the UCB (Upper Confidence Bound) value of this node."""
        if self.visits == 0:
            return sys.maxsize  # Unvisited nodes have max UCB
        
        # UCB formula: Q(s,a) + c * sqrt(ln(N(s)) / N(s,a))
        exploration = math.sqrt(2.0 * math.log(self.parent.visits) / float(self.visits))
        exploitation = self.reward / self.visits
        return exploitation + exploration
    
    def add_child(self, board, action, color):
        """Add a child node to this node."""
        child_node = Node(board, parent=self, action=action, color=color)
        self.children.append(child_node)
    
    def is_fully_expanded(self):
        """Check if all possible child nodes have been visited at least once."""
        if not self.children:
            return False
            
        for child in self.children:
            if child.visits == 0:
                return False
                
        return True


class MCTSAI:
    """AI player using Monte Carlo Tree Search algorithm."""
    
    def __init__(self, difficulty, player_color):
        """Initialize the AI with the specified difficulty."""
        self.difficulty = difficulty
        self.player_color = player_color
        self.ai_color = WHITE_TILE if player_color == BLACK_TILE else BLACK_TILE
        self.current_iteration = 0
    
    def get_progress(self):
        """获取当前搜索进度，返回0到1之间的值"""
        if self.difficulty == 0:
            return 1.0
        return min(1.0, self.current_iteration / self.difficulty)
    
    def get_best_move(self, board, progress_callback=None):
        """
        Get the best move according to MCTS algorithm.
        
        Args:
            board: The current board state
            progress_callback: Optional callback function to report progress
        """
        root = Node(board.get_copy(), None, None, self.player_color)
        self.current_iteration = 0
        
        # Run MCTS for the specified number of iterations
        for i in range(self.difficulty):
            self.current_iteration = i + 1
            
            # Selection phase: select a promising node
            selected_node = self._select(root)
            
            # Expansion phase: expand the selected node
            leaf_node = self._expand(selected_node)
            
            # Simulation phase: simulate a random game from the leaf node
            reward = self._simulate(leaf_node)
            
            # Backpropagation phase: update statistics in the path
            self._backpropagate(leaf_node, reward)
            
            # 报告进度
            if progress_callback and i % 10 == 0:  # 每10次迭代更新一次进度，避免过于频繁的UI更新
                progress_callback(self.get_progress())
        
        # Select the child with the highest UCB
        best_child = None
        best_ucb = float('-inf')
        
        for child in root.children:
            child_ucb = child.get_ucb()
            if best_ucb < child_ucb:
                best_ucb = child_ucb
                best_child = child
        
        # Print statistics for children
        print("validmoves\trewards\tvisits")
        for child in root.children:
            print(child.action, '\t', ':', '\t', child.reward, '\t', child.visits)
        print("--------------------------")
        
        return best_child.action if best_child else None
    
    def _select(self, node):
        """Select a node to expand based on UCB values."""
        if not node.children:  # Node needs expansion
            return node
            
        if node.is_fully_expanded():
            # Select child with highest UCB
            best_child = None
            best_ucb = float('-inf')
            
            for child in node.children:
                child_ucb = child.get_ucb()
                if best_ucb < child_ucb:
                    best_ucb = child_ucb
                    best_child = child
                    
            return self._select(best_child)
        else:
            # Select first unvisited child
            for child in node.children:
                if child.visits == 0:
                    return child
    
    def _expand(self, node):
        """Expand the selected node by adding all possible child nodes."""
        if node.visits == 0:  # Node hasn't been visited yet
            return node
            
        # Get the next player's color
        next_color = WHITE_TILE if node.color == BLACK_TILE else BLACK_TILE
        
        # Get all valid moves for the next player
        for action in node.board.get_valid_moves(next_color):
            new_board = node.board.get_copy()
            new_board.make_move(next_color, action[0], action[1])
            node.add_child(new_board, action=action, color=next_color)
        
        if not node.children:
            return node
            
        return node.children[0]  # Return first child for simulation
    
    def _simulate(self, node):
        """Simulate a random game from the current position to determine reward."""
        board = node.board.get_copy()
        color = node.color
        
        # Play random moves until game over
        while not board.is_game_over():
            # Get valid moves for current player
            valid_moves = board.get_valid_moves(color)
            
            if valid_moves:  # If player can move
                # Select a random valid move
                action = random.choice(valid_moves)
                board.make_move(color, action[0], action[1])
            
            # Switch player
            color = WHITE_TILE if color == BLACK_TILE else BLACK_TILE
            
            # If new player can't move, switch back
            new_valid_moves = board.get_valid_moves(color)
            if not new_valid_moves:
                color = WHITE_TILE if color == BLACK_TILE else BLACK_TILE
                # If original player also can't move, game is over
                if not board.get_valid_moves(color):
                    break
        
        # Determine winner
        scores = board.get_score()
        ai_score = scores[self.ai_color]
        player_score = scores[self.player_color]
        
        # Return 1 if AI wins, 0 otherwise
        return 1 if ai_score > player_score else 0
    
    def _backpropagate(self, node, reward):
        """Update statistics in all nodes along the path to the root."""
        while node:
            node.visits += 1
            
            # Update rewards based on player perspective
            if node.color == self.ai_color:
                node.reward += reward
            else:
                node.reward -= reward
                
            node = node.parent