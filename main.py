from functions.compare_models import compare_models
from models.mcts_root_parallelization import MCTSRootParallelization
from players.mcts_player import MCTSPlayer
from players.engine_player import EnginePlayer

if __name__ == '__main__':
    compare_models(MCTSPlayer(MCTSRootParallelization(C=0.25, max_moves=1, bias_weight=0.05, PW_A=60, PW_B=1.35, n_unpruned=4, max_sims=100000)),
                   EnginePlayer(),
                   verbose=True)