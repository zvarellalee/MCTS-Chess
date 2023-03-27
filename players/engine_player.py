import chess
import chess.engine

from players.player import Player


# Stockfish model abstraction class
class EnginePlayer(Player):
    def __init__(self, skill_level=0, path='stockfish.exe', time=1):
        self.path = path
        self.engine = chess.engine.SimpleEngine.popen_uci(path)
        self.engine.configure({"Skill Level": skill_level})
        self.time = time

    def get_next_move(self, board, verbose):
        result = self.engine.play(board, chess.engine.Limit(time=self.time))
        return result.move

    def close(self):
        self.engine.close()

    def get_name(self):
        return self.path[:-4]
