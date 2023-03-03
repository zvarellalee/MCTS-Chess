import chess

class MCTSPlayer():
    def __init__(self, algo_model):
        self.algo_model = algo_model

    def get_next_move(self):
        algo_model.