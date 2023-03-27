import chess

from functions.compare_models import max_depth
from functions.eval import evaluate, tanh
from models.mcts import MCTS


# MCTS with Early Playout Termination
class MCTSEarlyPlayoutTermination(MCTS):
    def __init__(self, chess_board=chess.Board(), **kwargs):
        super().__init__(chess_board, **kwargs)
        self.max_moves = kwargs.get('max_moves', 3)

    def simulation(self, curr_node):
        """
        Terminate the simulation after <max_moves> plys
        """
        # default policy: simulate the game using randomly selected moves.
        curr_board = chess.Board(curr_node.state)
        for i in range(self.max_moves):  # do until no more moves, or until game end?
            # first, check if the game is over
            if curr_board.is_game_over():
                if curr_board.result() == '1-0':  # if white win
                    if curr_node.is_white:
                        return 1
                    else:
                        return -1
                elif curr_board.result() == '0-1':  # if white lose
                    if curr_node.is_white:
                        return -1
                    else:
                        return 1
                else:  # if tie
                    return 0
            random_move = self.get_random_move(curr_board)
            curr_board.push(random_move)
        # if there is no victor after the max number of moves has been made, use evaluation function.
        score = evaluate(curr_board, curr_node.is_white)
        return tanh(score)


# testing
if __name__ == '__main__':
    board = chess.Board()

    mcts = MCTSEarlyPlayoutTermination(board, max_time=10, max_sims=100000)
    move = mcts.run(board, print_stats=True)

    board.push(move)

    print(board)
    print(max_depth(mcts.tree))
