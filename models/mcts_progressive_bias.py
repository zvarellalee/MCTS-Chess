import math

import anytree
import chess
from anytree import RenderTree

from functions.eval import evaluate, tanh
from models.mcts_ept import MCTSEarlyPlayoutTermination
from node.node import MCTSNode


# MCTS with Progressive Bias
class MCTSProgressiveBias(MCTSEarlyPlayoutTermination):
    def __init__(self, chess_board=chess.Board(), **kwargs):
        super().__init__(chess_board, **kwargs)
        self.bias_weight = kwargs.get('bias_weight', 0.01)

    def get_uct(self, curr_node, log):
        """
        The UCT formula is modified to include progressive bias.
        The weight of the bias term decreases as the number of visits to the node increases.
        """
        # Q/V + C*sqrt(2*ln(num_visits parent))/num_visits)
        c = self.C
        bias = (self.bias_weight * tanh(curr_node.heuristic_score)) / (
                    curr_node.num_visits + 1)
        return curr_node.score / curr_node.num_visits + c * math.sqrt(log / curr_node.num_visits) + bias

    def expansion(self, node: MCTSNode):
        """
        When a node is expanded, evaluate the heuristic score of its board state.
        """
        if node.untried_actions:
            untried_move = node.untried_actions.pop()
            new_board = chess.Board(node.state)
            new_board.push(untried_move)

            self.node_counter += 1
            child_node = MCTSNode(
                name=f'S{self.node_counter}',
                board=new_board,
                parent=node,
                action=untried_move,
                heuristic_score=evaluate(new_board, node.is_white)
            )
            return child_node
        return node

    def _set_root(self, next_board):
        state = next_board.fen()
        self.tree = next((n for n in self.tree.children if n.state == state), None)
        if self.tree is None:
            self.tree = MCTSNode(
                f'S{self.node_counter}',
                board=next_board,
                score=0,
                heuristic_score=evaluate(next_board, not next_board.turn)
            )
        self.tree.parent = None  # deallocate the rest of the tree to save memory

    def reset(self):
        new_board = chess.Board()
        self.node_counter = 0
        self.tree = MCTSNode(
            f'S{self.node_counter}',
            board=new_board,
            score=0,
            heuristic_score=0
        )


# testing
if __name__ == '__main__':
    board = chess.Board()
    mcts = MCTSProgressiveBias(board)
    move = mcts.run(board, print_stats=True)

    board.push(move)

    for child_node in mcts.tree.children:
        print(child_node.heuristic_score)

    print(board)
