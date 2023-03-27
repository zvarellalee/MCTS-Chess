from players.player import Player


# MCTS player abstraction class
class MCTSPlayer(Player):
    def __init__(self, algo_model):
        self.algo_model = algo_model

    def get_next_move(self, board, verbose):
        move = self.algo_model.run(board, print_stats=verbose)
        return move

    def get_stats(self):
        return self.algo_model.get_stats()

    def get_name(self):
        return self.algo_model.__class__.__name__

    def reset(self):
        self.algo_model.reset()
