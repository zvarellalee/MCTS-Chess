import chess
import math

from functions.eval import evaluate


def minimax_search(depth, curr_board, is_max_node):
    """
    Perform minimax search with alpha beta pruning
    """
    best_score = -9999 if is_max_node else 9999
    best_move = None
    for legal_move in curr_board.legal_moves:
        curr_board.push(legal_move)
        if is_max_node:
            value = max(best_score, _minimax(depth - 1, curr_board, -10000, 10000, not is_max_node))
        else:
            value = min(best_score, _minimax(depth - 1, curr_board, -10000, 10000, not is_max_node))
        curr_board.pop()
        if is_max_node:
            if value > best_score:
                best_score = value
                best_move = legal_move
        else:
            if value < best_score:
                best_score = value
                best_move = legal_move
    return best_move


def _minimax(depth, curr_board, alpha, beta, is_max_node):
    if depth == 0 or curr_board.is_game_over():
        return evaluate(curr_board, True)
    if is_max_node:
        best_score = -math.inf
        for legal_move in curr_board.legal_moves:
            curr_board.push(legal_move)
            best_score = max(best_score, _minimax(depth - 1, curr_board, alpha, beta, not is_max_node))
            curr_board.pop()
            alpha = max(alpha, best_score)
            if beta <= alpha:
                return best_score
        return best_score
    else:
        best_score = math.inf
        for legal_move in curr_board.legal_moves:
            curr_board.push(legal_move)
            best_score = min(best_score, _minimax(depth - 1, curr_board, alpha, beta, not is_max_node))
            curr_board.pop()
            beta = min(beta, best_score)
            if beta <= alpha:
                return best_score
        return best_score


if __name__ == "__main__":
    board = chess.Board()
    move = minimax_search(3, board, board.turn)
    board.push(move)
