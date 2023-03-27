import math
import os
import time
import chess
import numpy as np
import random

from models.mcts_score_bounded import MCTSScoreBounded
from multiprocessing import Pool


# MCTS with Root Parallelization
class MCTSRootParallelization(MCTSScoreBounded):
    def __init__(self, chess_board=chess.Board(), **kwargs):
        super().__init__(chess_board, **kwargs)
        self.num_processes = kwargs.get('num_processes', round(os.cpu_count() * .75))  # int(os.cpu_count()/1.5))
        self.num_trees = kwargs.get('num_trees', self.num_processes)

    def parallel_search(self):
        """
        Parallelized search with a random seed for each process
        """
        random.seed((os.getpid() * int(time.time())) % 123456789)  # set a random seed so that we get different results
        start_time = time.time()
        i = 0
        for i in range(self.max_sims):
            node = self.tree_policy()
            score = -self.simulation(node)
            self.backpropagation(node, score)
            # check time limit
            if self.max_time is not None and (time.time() - start_time) > self.max_time:
                break
        best_child = np.argmax([child.num_visits for child in self.tree.children])
        best_move = self.tree.children[best_child].action
        num_visits = self.tree.children[best_child].num_visits
        # return move, total visits, total simulations performed, node stats
        return best_move, num_visits, i + 1, [(n.score, n.num_visits, n.action) for n in self.tree.children]

    def run(self, board, print_stats=False):
        """
        Modify main run function to handle parallel execution and multiple tree aggregation
        """
        if self.tree.is_game_over:
            return None

        self._set_root(board)

        start_time = time.time()

        with Pool(self.num_processes) as p:
            ensemble_rewards = p.starmap(self.parallel_search, [() for _ in range(self.num_trees)])

        time_taken = time.time() - start_time
        total_sims = 0
        move_dict = {}
        vote_dict = {}

        # first, tally the votes and visits
        for best_move, num_visits, sim_count, tree_reward_list in ensemble_rewards:
            move_name = best_move.uci()
            if move_name not in vote_dict:
                vote_dict[move_name] = [1, num_visits, best_move]
            else:
                vote_dict[move_name][0] += 1
                vote_dict[move_name][1] += num_visits
            total_sims += sim_count
            for node_reward in tree_reward_list:
                mean, visits, move = node_reward
                move_name = move.uci()
                if move_name not in move_dict:
                    # [[mean, total visits], count, move object]
                    move_dict[move_name] = [np.array([0.0, 0.0]), 0, move]
                move_dict[move_name][0][0] += mean
                move_dict[move_name][0][1] += visits
                move_dict[move_name][1] += 1

        # ----- majority voting -----
        # we combine using the majority voting method.
        # 1. each tree will vote on the best moves discovered independently.
        # 2. the number of votes are tallied, and the move with the most votes wins.
        # 3. if two (or more) moves have the same number of votes, then the move with the most visits wins.
        best = [0, 0, None]
        for move_stats in vote_dict.values():
            if move_stats[0] > best[0]:  # for majority voting
                best = move_stats
            elif move_stats[0] == best[0]:  # if there is a tie, prefer the move with the most visits
               if move_stats[1] > best[1]:
                   best = move_stats
        best_move = best[2]
        total_visits = best[1]

        self.stats['total_time'] += time_taken
        self.stats['total_simulations'] += total_sims
        if print_stats:  # for statistics
            child_node_visits, child_node_scores = [], []  # for displaying stats
            for key in move_dict.keys():
                child_node_scores.append(move_dict[key][0][0])
                child_node_visits.append(move_dict[key][0][1])
            print(f'Time elapsed: {time_taken}, Simulations completed: {total_sims}')
            print('Child node visits:', child_node_visits)
            print('Child node scores:', child_node_scores)
            print(f'Best move: {best_move}, Num visits: {total_visits}')
        return best_move


# testing
if __name__ == '__main__':
    board = chess.Board()

    mcts = MCTSRootParallelization(board)
    move = mcts.run(board, print_stats=True)

    board.push(move)

    print(board)
    print(board.fen)
