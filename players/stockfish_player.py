import chess
import chess.engine


class StockfishPlayer():
    def __init__(self, path='stockfish.exe', depth=10):
        self.stockfish = chess.engine.SimpleEngine.popen_uci('stockfish.exe')
        self.depth = depth

    def get_next_move(self, fen):
        board = chess.Board(fen)
        analysis = self.stockfish.analyse(board, chess.engine.Limit(depth=self.depth))
        return analysis['pv'][0]