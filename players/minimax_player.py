from models.minimax import minimax_search
from players.player import Player


# Minimax model abstraction class
class MinimaxPlayer(Player):
    def __init__(self, depth=3):
        self.depth = depth

    def get_next_move(self, board, verbose):
        move = minimax_search(self.depth, board, board.turn)
        return move

    def get_name(self):
        return "Minimax"
