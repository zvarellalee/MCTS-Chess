import chess
import chess.engine
import chess.pgn

class StockfishPlayer():
    def __init__(self, path='stockfish.exe', depth=10):
        self.stockfish = chess.engine.SimpleEngine.popen_uci('stockfish.exe')
        self.depth = depth

    def get_next_move(self, fen):
        board = chess.Board(fen)
        analysis = self.stockfish.analyse(board, chess.engine.Limit(depth=self.depth))
        return analysis['pv'][0]

def play_vs_stockfish():
    board = chess.Board()
    engine = chess.engine.SimpleEngine.popen_uci('stockfish.exe')

    #game = chess.pgn.Game()

    while((not board.is_game_over())):
        pass




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
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

    b = chess.Board()
    print(b)
    #print(b.pieces(chess.PAWN, chess.BLACK))
    #for i in b.pieces(chess.PAWN, chess.BLACK):
    #    print(i)
    for square in chess.SQUARES:
        piece = b.piece_at(square)
        if piece:
            print(square//8)
            print(piece)
            print(piece.color == chess.WHITE)
            print(piece.piece_type == chess.ROOK)
            print()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
