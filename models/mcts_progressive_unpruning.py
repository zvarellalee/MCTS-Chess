import math
import chess

from functions.eval import evaluate
from models.mcts_ept import MCTSEarlyPlayoutTermination
from models.mcts_progressive_bias import MCTSProgressiveBias
from node.node import MCTSNode


# MCTS with Progressive Unpruning
class MCTSProgressiveUnpruning(MCTSEarlyPlayoutTermination):
    def __init__(self, chess_board=chess.Board(), **kwargs):
        super().__init__(chess_board, **kwargs)
        self.n_unpruned = kwargs.get('n_unpruned', 5)
        self.PW_A = kwargs.get('PW_B', 50)
        self.PW_B = kwargs.get('PW_B', 1.3)

    def selection(self, node):
        """
        Once all children nodes have been expanded, prune the nodes leaving only <n_unpruned> remaining.
        When a node receives more visits than the threshold value, begin unpruning nodes.
        """
        selected_node = node
        best_uct = -math.inf
        if not node.untried_actions and node.children:
            log = math.log(node.num_visits)
            if node.num_visits >= self.PW_A:
                node.sort_children()
                threshold = self.PW_A * self.PW_B ** (node.num_unpruned + 1 - self.n_unpruned)
                if node.num_visits > threshold:
                    node.num_unpruned += 1
                j = min(node.num_unpruned, len(node.children))
                for child_node in node.sorted_children[:j]:
                    uct = self.get_uct(child_node, log)
                    if uct > best_uct:
                        selected_node = child_node
                        best_uct = uct
            else:
                for child_node in node.children:
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
        )
        self.tree.num_unpruned = self.n_unpruned


# testing
if __name__ == '__main__':
    board = chess.Board()

    mcts = MCTSProgressiveUnpruning(board, max_time=5, max_sims=100000)
    move = mcts.run(board, print_stats=True)

    board.push(move)

    print(board)
