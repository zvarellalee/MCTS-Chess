from functions.scores import *
import chess

def evaluate_board(color_board, piece_board):
    score_white = 0
    score_black = 0
    file = 0

    pawn_rank_white = [0] * 10
    pawn_rank_black = [7] * 10

    # value of pieces
    piece_mat_white = 0
    piece_mat_black = 0

    # value of pawns
    pawn_mat_white = 0
    pawn_mat_black = 0

    # set up piece_mat and pawn_mat
    for i in range(64):
        # TODO: board representation should change the board array.
        # TODO: seperate arrays for color and piece, or combine together?

        # E = Empty, B = Black, W = White
        if color_board[i] == b'E':
            continue

        # TODO: use some enum/variable settings to store values for pieces?
        if piece_board[i] == Pieces.PAWN:
            if color_board[i] == b'W':
                pawn_mat_white += Pieces.PAWN.value
                file = # TODO: what is file for?
                # TODO: fill out
            else:
                # TODO: fill out
                continue
        else:
            # TODO: can change this logic by moving check for color outside.
            # TODO: should make this check a bit cleaner.
            if color_board[i] == b'W':
                piece_mat_white += piece_board[i].value
            else:
                piece_mat_black += piece_board[i].value

    # evaluate each piece
    score_white = piece_mat_white + pawn_mat_white
    score_black = piece_mat_black + pawn_mat_black
    for i in range(64):
        if color_board[i] == b'E':
            continue
        if color_board[i] == b'W':
            if piece_board[i] == Pieces.PAWN:
                score_white += eval_light_pawn(i)
            elif piece_board[i] == Pieces.KNIGHT:
                score_white += knight_pcsq[i]
            elif piece_board[i] == Pieces.BISHOP:
                score_white += bishop_pcsq[i]
            elif piece_board[i] == Pieces.ROOK:
                if pawn_rank_white[...] == 0: # TODO: fill in ...
                    if pawn_rank_black[...] == 7:
                        score_white += 
            elif piece_board[i] == Pieces.KING:


def eval_light_pawn(pos):
    pass
