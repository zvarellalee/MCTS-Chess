import math
import random

import chess

from functions.eval import evaluate, MAX_SCORE, tanh
from models.mcts_progressive_unpruning import MCTSProgressiveUnpruning


# MCTS with Epsilon Greedy Search
class MCTSEpsilonGreedy(MCTSProgressiveUnpruning):
    def __init__(self, chess_board=chess.Board(), **kwargs):
        super().__init__(chess_board, **kwargs)
        self.epsilon = kwargs.get('epsilon', 0.4)

    def simulation(self, curr_node):
        """
        Modified simulation policy to randomly decide between a greedy simulation and random simulation
        with probability e.
        """
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
            e = random.random()  # epsilon
            if e < self.epsilon:
                random_move = self.get_random_move(curr_board)
                curr_board.push(random_move)
            else:
                best_move = self.get_best_move(curr_board)
                curr_board.push(best_move)
        # if there is no victor after the max number of moves has been made, use evaluation function.
        score = evaluate(curr_board, curr_node.is_white)
        return tanh(score)

    def get_best_move(self, curr_board):
        """
        Get the best move out of all legal moves according to the heuristic function
        """
        best_move = None
        best_score = -math.inf
        for legal_move in curr_board.legal_moves:
            curr_board.push(legal_move)
            score = evaluate(curr_board, not curr_board.turn)
            if score > best_score:
                best_score = score
                best_move = legal_move
                if score == MAX_SCORE:
                    curr_board.pop()
                    return best_move
            curr_board.pop()
        return best_move


# testing
if __name__ == '__main__':
    board = chess.Board('rnbqkbnr/pppppppp/8/8/8/2P5/PP1PPPPP/RNBQKBNR b KQkq - 0 1')

    mcts = MCTSEpsilonGreedy(board)
    move = mcts.run(board, print_stats=True)

    board.push(move)

    print(board)
