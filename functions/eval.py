import chess

DOUBLED_PAWN_PENALTY = 10
ISOLATED_PAWN_PENALTY = 20
BACKWARDS_PAWN_PENALTY = 8
PASSED_PAWN_BONUS = 20
ROOK_SEMI_OPEN_FILE_BONUS = 10
ROOK_OPEN_FILE_BONUS = 15
ROOK_ON_SEVENTH_BONUS = 20

pawn_pcsq = [
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 15, 20, 20, 15, 10, 5,
    4, 8, 12, 16, 16, 12, 8, 4,
    3, 6, 9, 12, 12, 9, 6, 3,
    2, 4, 6, 8, 8, 6, 4, 2,
    1, 2, 3, -10, -10, 3, 2, 1,
    0, 0, 0, -40, -40, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0
]

knight_pcsq = [
    -10, -10, -10, -10, -10, -10, -10, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, -30, -10, -10, -10, -10, -30, -10
]

bishop_pcsq = [
    -10, -10, -10, -10, -10, -10, -10, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, -10, -20, -10, -10, -20, -10, -10
]

king_pcsq = [
    -40, -40, -40, -40, -40, -40, -40, -40,
    -40, -40, -40, -40, -40, -40, -40, -40,
    -40, -40, -40, -40, -40, -40, -40, -40,
    -40, -40, -40, -40, -40, -40, -40, -40,
    -40, -40, -40, -40, -40, -40, -40, -40,
    -40, -40, -40, -40, -40, -40, -40, -40,
    -20, -20, -20, -20, -20, -20, -20, -20,
    0, 20, 40, -20, 0, -20, 40, 20
]

king_endgame_pcsq = [
    0, 10, 20, 30, 30, 20, 10, 0,
    10, 20, 30, 40, 40, 30, 20, 10,
    20, 30, 40, 50, 50, 40, 30, 20,
    30, 40, 50, 60, 60, 50, 40, 30,
    30, 40, 50, 60, 60, 50, 40, 30,
    20, 30, 40, 50, 50, 40, 30, 20,
    10, 20, 30, 40, 40, 30, 20, 10,
    0, 10, 20, 30, 30, 20, 10, 0
]

# flip table is used for caluclation the piece/square values of dark pieces.
# piece/square value of light pawn = pawn_pcsq[sq]
# piece/square value of dark pawn - pawn_pcsq[flip[sq]]
# NOTE: because chess library starts from the last 0, use this to flip the index to the values used in TCSP
flip = [
    56, 57, 58, 59, 60, 61, 62, 63,
    48, 49, 50, 51, 52, 53, 54, 55,
    40, 41, 42, 43, 44, 45, 46, 47,
    32, 33, 34, 35, 36, 37, 38, 39,
    24, 25, 26, 27, 28, 29, 30, 31,
    16, 17, 18, 19, 20, 21, 22, 23,
    8, 9, 10, 11, 12, 13, 14, 15,
    0, 1, 2, 3, 4, 5, 6, 7
]

piece_values = {
    chess.PAWN: 100,
    chess.BISHOP: 300,
    chess.KNIGHT: 300,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 2000
}

LIGHT = 0
DARK = 1


def evaluate(board: chess.Board, is_white: bool):
    score = [0, 0]  # total score of each side
    piece_mat = [0, 0]  # value of a side's pieces
    pawn_mat = [0, 0]  # value of a side's pawns

    pawn_rank = [[0]*10, [7]*10]

    # first pass: set up pawn_rank, piece_mat, and pawn_mat
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_value = piece_values[piece.piece_type]
            piece_color = LIGHT if piece.color == chess.WHITE else DARK
            if piece.piece_type == chess.PAWN:
                pawn_mat[piece_color] += piece_value
                location = flip[square]  # TODO: may need to remove this
                col = location % 8 + 1
                row = location // 8
                if piece_color == LIGHT:
                    if pawn_rank[LIGHT][col] < row:
                        pawn_rank[LIGHT][col] = row
                else:
                    if pawn_rank[DARK][col] > row:
                        pawn_rank[DARK][col] = row
            else:
                piece_mat[piece_color] += piece_value

    # second pass: evaluate each piece
    score[LIGHT] = piece_mat[LIGHT] + pawn_mat[LIGHT]
    score[DARK] = piece_mat[DARK] + pawn_mat[DARK]

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_type = piece.piece_type
            color = LIGHT if piece.color == chess.WHITE else DARK
            location = flip[square]  # TODO: may need to remove this
            if color == LIGHT:
                if piece_type == chess.PAWN:
                    score[LIGHT] += eval_light_pawn(location, pawn_rank)
                elif piece_type == chess.KNIGHT:
                    score[LIGHT] += knight_pcsq[location]
                elif piece_type == chess.BISHOP:
                    score[LIGHT] += bishop_pcsq[location]
                elif piece_type == chess.ROOK:
                    col = location % 8 + 1
                    row = location // 8
                    if pawn_rank[LIGHT][col] == 0:
                        if pawn_rank[DARK][col] == 7:
                            score[LIGHT] += ROOK_OPEN_FILE_BONUS
                        else:
                            score[LIGHT] += ROOK_SEMI_OPEN_FILE_BONUS
                    if row == 1:
                        score[LIGHT] += ROOK_ON_SEVENTH_BONUS
                elif piece_type == chess.KING:
                    if piece_mat[DARK] <= 1200:
                        score[LIGHT] += king_endgame_pcsq[location]
                    else:
                        score[LIGHT] += eval_light_king(location, pawn_rank, piece_mat)
            else:
                if piece_type == chess.PAWN:
                    score[DARK] += eval_dark_pawn(location, pawn_rank)
                elif piece_type == chess.KNIGHT:
                    score[DARK] += knight_pcsq[flip[location]]
                elif piece_type == chess.BISHOP:
                    score[DARK] += bishop_pcsq[flip[location]]
                elif piece_type == chess.ROOK:
                    col = location % 8 + 1
                    row = location // 8
                    # TODO: may have to flip this
                    if pawn_rank[DARK][col] == 7:
                        if pawn_rank[LIGHT][col] == 0:
                            score[DARK] += ROOK_OPEN_FILE_BONUS
                        else:
                            score[DARK] += ROOK_SEMI_OPEN_FILE_BONUS
                    if row == 6:
                        score[DARK] += ROOK_ON_SEVENTH_BONUS
                elif piece_type == chess.KING:
                    if piece_mat[LIGHT] <= 1200:
                        score[DARK] += king_endgame_pcsq[location]
                    else:
                        score[DARK] += eval_dark_king(location, pawn_rank, piece_mat)
    if is_white:
        return score[LIGHT] - score[DARK]
    return score[DARK] - score[LIGHT]


def eval_light_pawn(square: int, pawn_rank):
    score = 0
    col = square % 8 + 1
    row = square // 8

    score += pawn_pcsq[square]

    # if there is a pawn behind the one being evaluated, penalty is doubled
    if pawn_rank[LIGHT][col] > row:
        score -= DOUBLED_PAWN_PENALTY

    # if there are no friendly pawns on either side of this pawn, it is isolated
    if pawn_rank[LIGHT][col-1] == 0 and pawn_rank[LIGHT][col+1] == 0:
        score -= BACKWARDS_PAWN_PENALTY

    # if not isolated, might be backwards
    elif pawn_rank[LIGHT][col-1] < row and pawn_rank[LIGHT][col+1] < row:
        score -= BACKWARDS_PAWN_PENALTY

    # add bonus if enemy pawn is passed
    if pawn_rank[DARK][col-1] >= row and pawn_rank[DARK][col] >= row and pawn_rank[DARK][col+1] >= row:
        score += (7 - row) * PASSED_PAWN_BONUS

    return score


def eval_dark_pawn(square: int, pawn_rank):
    score = 0
    col = square % 8 + 1
    row = square // 8

    score += pawn_pcsq[flip[square]]

    # if there is a pawn behind the one being evaluated, penalty is doubled
    if pawn_rank[DARK][col] < row:
        score -= DOUBLED_PAWN_PENALTY

    # if there are no friendly pawns on either side of this pawn, it is isolated
    if pawn_rank[DARK][col - 1] == 7 and pawn_rank[DARK][col + 1] == 7:
        score -= BACKWARDS_PAWN_PENALTY

    # if not isolated, might be backwards
    elif pawn_rank[DARK][col - 1] > row and pawn_rank[DARK][col + 1] > row:
        score -= BACKWARDS_PAWN_PENALTY

    # add bonus if enemy pawn is passed
    if pawn_rank[LIGHT][col - 1] <= row and pawn_rank[LIGHT][col] <= row and pawn_rank[LIGHT][col + 1] <= row:
        score += row * PASSED_PAWN_BONUS

    return score


def eval_light_king(square: int, pawn_rank, piece_mat):
    r = king_pcsq[square]
    col = square % 8

    # if king is castled, use a special function to evaluate the pawns on the appropriate side
    if col < 3:
        r += eval_lkp(1, pawn_rank)
        r += eval_lkp(2, pawn_rank)
        r += eval_lkp(3, pawn_rank) / 2

    elif col > 4:
        r += eval_lkp(8, pawn_rank)
        r += eval_lkp(7, pawn_rank)
        r += eval_lkp(6, pawn_rank) / 2

    # otherwise, assess penalty if there are open files near the king
    else:
        for i in range(col, col+3):
            if pawn_rank[LIGHT][i] == 0 and pawn_rank[DARK][i] == 7:
                r -= 10

    # scale king safety value according to the opponent's material value.
    # idea - your king safety can only be bad if the opponent has enough pieces to attack you
    r *= piece_mat[DARK]
    r //= 3100

    return r


def eval_lkp(f, pawn_rank):
    r = 0

    if pawn_rank[LIGHT][f] == 6:  # pawn hasn't moved
        pass
    elif pawn_rank[LIGHT][f] == 5:  # pawn moved on square
        r -= 10
    elif pawn_rank[LIGHT][f] != 0:  # pawn moved >1 square
        r -= 20
    else:  # no pawn on this file
        r -= 25

    if pawn_rank[DARK][f] == 7:  # no enemy pawn
        r -= 15
    elif pawn_rank[DARK][f] == 5:  # enemy pawn on 3rd rank
        r -= 10
    elif pawn_rank[DARK][f] != 0:  # enemy pawn on the 4th rank
        r -= 5

    return r


def eval_dark_king(square: int, pawn_rank, piece_mat):
    r = king_pcsq[flip[square]]
    col = square % 8

    # if king is castled, use a special function to evaluate the pawns on the appropriate side
    if col < 3:
        r += eval_dkp(1, pawn_rank)
        r += eval_dkp(2, pawn_rank)
        r += eval_dkp(3, pawn_rank) / 2

    elif col > 4:
        r += eval_dkp(8, pawn_rank)
        r += eval_dkp(7, pawn_rank)
        r += eval_dkp(6, pawn_rank) / 2

    # otherwise, assess penalty if there are open files near the king
    else:
        for i in range(col, col + 3):
            if pawn_rank[LIGHT][i] == 0 and pawn_rank[DARK][i] == 7:
                r -= 10

    # scale king safety value according to the opponent's material value.
    # idea - your king safety can only be bad if the opponent has enough pieces to attack you
    r *= piece_mat[LIGHT]
    r //= 3100

    return r


def eval_dkp(f, pawn_rank):
    r = 0

    if pawn_rank[DARK][f] == 1:  # pawn hasn't moved
        pass
    elif pawn_rank[DARK][f] == 2:  # pawn moved on square
        r -= 10
    elif pawn_rank[DARK][f] != 7:  # pawn moved >1 square
        r -= 20
    else:  # no pawn on this file
        r -= 25

    if pawn_rank[LIGHT][f] == 0:  # no enemy pawn
        r -= 15
    elif pawn_rank[LIGHT][f] == 2:  # enemy pawn on 3rd rank
        r -= 10
    elif pawn_rank[LIGHT][f] != 3:  # enemy pawn on the 4th rank
        r -= 5

    return r


# TODO: testing
if __name__ == '__main__':
    board = chess.Board('r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4')
    print(board)
    print(evaluate(board, True))
    print(board.is_game_over())
