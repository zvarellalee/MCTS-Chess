import random
import chess

from functions.eval import evaluate, tanh
from models.mcts_progressive_unpruning import MCTSProgressiveUnpruning


# MCTS with Decisive Move simulation
class MCTSDecisiveMoves(MCTSProgressiveUnpruning):
    def __init__(self, chess_board=chess.Board(), **kwargs):
        super().__init__(chess_board, **kwargs)

    def choose_move(self, curr_board):
        # Scan for any possible decisive moves (moves that will win the game).
        temp_board = curr_board.copy()
        for legal_move in curr_board.legal_moves:
            temp_board.push(legal_move)
            if temp_board.is_checkmate():
                return legal_move
            temp_board.pop()
        return self.get_random_move(curr_board)

    # modification of epsilon-greedy simulation to include decisive moves
    def simulation(self, curr_node):
        curr_board = chess.Board(curr_node.state)
        for i in range(self.max_moves):
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
            next_move = self.choose_move(curr_board)
            curr_board.push(next_move)
        # if there is no victor after the max number of moves has been made, use evaluation function.
        score = evaluate(curr_board, curr_node.is_white)
        return tanh(score)


# testing
if __name__ == '__main__':
    # test decisive move available
    # board = chess.Board('8/8/8/5n2/8/K7/2k5/4q3 b - - 3 57')

    board = chess.Board()

    mcts = MCTSDecisiveMoves(board)
    move = mcts.run(board, print_stats=True)

    board.push(move)

    print(board)
