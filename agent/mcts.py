import chess
import chess.pgn
import chess.engineimport random
import time

# class representing one node in the MCTS tree.
# uses the UCT algorithm for balancing exploration and exploitation of nodes during search.\
class MCTNode():
    # TODO: possible improvement - use a different UCT formula (currently using base)
    def __init__(self, board, parent=None):
        self.parent = parent        # parent of current node
        self.children = {}          # child node(s) of current node
        self.num_visits = 0         # number of visits to the node
        self.checkmates = 0         # number of checkmates achieved when visiting this node
        self.C = 1                  # C constant of MCT algorithm.
        # Higher C = favour exploration, lower C = favour exploitation
        self.white = True          # if True, this is a white move node. Else, black.
        self.chess_board = board
        self.valid_moves = []




