import math
import random

import anytree
import chess

from functions.compare_models import max_depth
from functions.eval import MAX_SCORE, tanh, evaluate
from models.mcts_progressive_unpruning import MCTSProgressiveUnpruning
from node.node import MCTSNode


# MCTS with Score Bounded Search
class MCTSScoreBounded(MCTSProgressiveUnpruning):
    def __init__(self, chess_board=chess.Board(), **kwargs):
        super().__init__(chess_board, **kwargs)
        self.pess_bias = kwargs.get('pess_bias', 20)
        self.opti_bias = kwargs.get('opti_bas', 20)

    def selection(self, node):
        """
        Selection function is modified to include alpha beta pruning based on score bounds.
        """
        selected_node = node
        best_uct = -math.inf
        if not node.untried_actions and node.children:
            node.alpha_beta_pruning()

            threshold = self.PW_A * self.PW_B ** (node.num_unpruned + 1 - self.n_unpruned)
            if node.num_visits > threshold:
                node.num_unpruned += 1
            log = math.log(node.num_visits)
            j = min(node.num_unpruned, len(node.children))
            for child_node in node.sorted_children[:j]:
                uct = self.get_uct(child_node, log)
                if uct > best_uct:
                    selected_node = child_node
                    best_uct = uct
        return selected_node

    def expansion(self, node: MCTSNode):
        # given a node, expand a random legal move as a child node
        if node.untried_actions:
            move = node.untried_actions.pop()
            # make the move
            new_board = chess.Board(node.state)
            new_board.push(move)

            self.node_counter += 1
            child_node = MCTSNode(
                name=f'S{self.node_counter}',
                board=new_board,
                parent=node,
                action=move,
                heuristic_score=evaluate(new_board, new_board.turn)  # heuristic score is used to set the bounds
            )
            child_node.num_unpruned = self.n_unpruned  # initialize the current amount of unpruned nodes for each node
            return child_node
        return node

    def _set_root(self, board):
        state = board.fen()
        self.tree = next((n for n in self.tree.children if n.state == state), None)
        if self.tree is None:
            self.tree = MCTSNode(
                f'S{self.node_counter}',
                board=board,
                score=0,
                heuristic_score=evaluate(board, board.turn)
            )
            self.tree.num_unpruned = self.n_unpruned
        self.tree.parent = None  # deallocate the rest of the tree to save memory

    def reset(self):
        board = chess.Board()
        self.node_counter = 0
        self.tree = MCTSNode(
            f'S{self.node_counter}',
            board=board,
            score=0,
            heuristic_score=0
        )
        self.tree.num_unpruned = self.n_unpruned

    def backpropagation(self, node, result):
        """
        In score bounded search, we also backpropagate the optimistic and pessimistic bound values of the node.
        """
        while node:
            node.num_visits += 1
            node.score += result
            result = -result

            # update the bounds if this is a terminal node
            if node.is_game_over:
                if node.outcome == '1-0':  # if white win
                    if node.is_white:
                        node.pess_bound = MAX_SCORE
                        node.opti_bound = MAX_SCORE
                    else:
                        node.pess_bound = -MAX_SCORE
                        node.opti_bound = -MAX_SCORE
                elif node.outcome == '0-1':  # if white lose
                    if node.is_white:
                        node.opti_bound = -MAX_SCORE
                        node.pess_bound = -MAX_SCORE
                    else:
                        node.pess_bound = MAX_SCORE
                        node.opti_bound = MAX_SCORE
                else:  # if tie
                    node.pess_bound = 0
                    node.opti_bound = 0

            node = node.parent

            # propagate the pessimistic and optimistic bounds
            if node and node.children:
                pess_bound, opti_bound = self.get_bounds(node)
                node.pess_bound = pess_bound
                node.opti_bound = opti_bound

            # since we use negated rewards, both bounds should try to minimize.

    def get_bounds(self, node):
        """
        Get the minimum pessimistic and optimistic bounds amongst a node's children for backpropagation
        """
        min_child_pess = math.inf
        min_child_opti = math.inf
        for child_node in node.children:
            if child_node.pess_bound < min_child_pess:
                min_child_pess = child_node.pess_bound
            if child_node.opti_bound < min_child_opti:
                min_child_opti = child_node.opti_bound
        # these are the new pessimistic and optimistic bounds, respectively
        return -min_child_opti, -min_child_pess


# testing
if __name__ == '__main__':
    # test if bounded search prunes correctly
    board = chess.Board('rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1')
    # board = chess.Board('8/8/8/5n2/8/K7/2k5/4q3 b - - 3 57')
    mcts = MCTSScoreBounded(board, C=0.8, n_unpruned=5, max_time=5, max_sims=100000)
    move = mcts.run(board, print_stats=True)
    print(board)
    board.push(move)

    print(max_depth(mcts.tree))
    print(board)
    print(mcts.tree.sorted_children)
    print(mcts.tree.sorted_children[0].pess_bound)
    print(mcts.tree.sorted_children[0].opti_bound)
