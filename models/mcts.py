import math
import chess
import time
import random
import numpy as np
from node.node import MCTSNode

'''
Base MCTS Class
'''


class MCTS:
    def __init__(self, chess_board=chess.Board(), **kwargs):
        self.max_time = kwargs.get('max_time', 5)  # 1 << 25
        self.max_moves = kwargs.get('max_moves', 1000)
        self.max_sims = kwargs.get('max_sims', 10000)
        self.C = kwargs.get('C', 1)
        self.node_counter = 0
        self.stats = {'total_time': 0, 'total_simulations': 0}
        self.tree = MCTSNode(
            f'S{self.node_counter}',
            board=chess_board,
            score=0,
        )

    def get_random_move(self, curr_board):
        return random.choice([move for move in curr_board.legal_moves])

    def get_uct(self, curr_node, log):
        """
        Base UCT formula
        """
        # Q/V + C*sqrt(2*ln(num_visits parent))/num_visits)
        c = self.C
        return curr_node.score / curr_node.num_visits + c * math.sqrt(log / curr_node.num_visits)  # curr_node.mean +

    def selection(self, node):
        """
        Selection phase - choose node with the highest UCT value to expand
        """
        selected_node = node
        best_uct = -math.inf
        if not node.untried_actions and node.children:
            log = math.log(node.num_visits)
            for child_node in node.children:
                uct = self.get_uct(child_node, log)
                if uct > best_uct:
                    selected_node = child_node
                    best_uct = uct
        return selected_node

    def expansion(self, node: MCTSNode):
        """
        Expansion phase - choose a random child to add to the tree
        """
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
            return child_node
        return node

    def simulation(self, curr_node: MCTSNode):
        """
        Simulation phase - do random moves until the end of the game, and return the final outcome
        """
        # default policy: simulate the game using randomly selected moves.
        curr_board = chess.Board(curr_node.state)
        while not curr_board.is_game_over():
            random_move = random.choice([move for move in curr_board.legal_moves])
            curr_board.push(random_move)
        if curr_board.result() == '1-0':  # if white win
            if curr_node.is_white:  # self.white_player:
                return 1
            else:
                return -1
        elif curr_board.result() == '0-1':  # if white lose
            if curr_node.is_white:  # self.white_player:
                return -1
            else:
                return 1
        else:  # if tie
            return 0

    def backpropagation(self, node, result):
        """
        Backpropagation phase - backpropagate the result score and visits
        """
        # update the tree by backpropagation of results
        while node:
            node.num_visits += 1
            # node.mean += result / node.num_visits
            node.score += result
            result = -result  # reward for one side = -reward for other side
            node = node.parent

    def _set_root(self, board):
        """
        Set the root of the tree to the existing node, or create a new node if it does not exist (tree collapse)
        This allows for tree reuse.
        """
        state = board.fen()
        self.tree = next((n for n in self.tree.children if n.state == state), None)
        if self.tree is None:  # if node cannot be found for a board state, then create a new node.
            self.tree = MCTSNode(
                f'S{self.node_counter}',
                board=board,
                score=0,
            )
        self.tree.parent = None  # deallocate the rest of the tree to save memory

    def reset(self):
        board = chess.Board()
        self.node_counter = 0
        self.tree = MCTSNode(
            f'S{self.node_counter}',
            board=board,
            score=0,
        )

    def tree_policy(self):
        """
        Tree policy implementation
        """
        current_node = self.tree
        while not current_node.is_game_over:
            if current_node.untried_actions:
                return self.expansion(current_node)
            else:
                current_node = self.selection(current_node)
        return current_node

    def run(self, board, print_stats=False):
        """
        Main search function
        """
        self._set_root(board)
        start_time = time.time()
        # computational budget = max number of steps and max allowed time
        for i in range(self.max_sims):
            # 1. tree policy
            node = self.tree_policy()
            # 3. simulation
            score = -self.simulation(node)
            # 4. backpropagation
            self.backpropagation(node, score)
            # check time limit
            if self.max_time is not None and (time.time() - start_time) > self.max_time:
                break
        time_taken = time.time() - start_time
        # get the best action using the 'robust child' method
        if self.tree.is_game_over:
            return None
        best_child = np.argmax([child.num_visits for child in self.tree.children])
        best_move = self.tree.children[best_child].action

        self.stats['total_time'] += time_taken
        self.stats['total_simulations'] += i + 1
        if print_stats:  # for statistics
            print(f'Time elapsed: {time_taken}, Simulations completed: {i + 1}')
            print('Child node visits:', [child.num_visits for child in self.tree.children])
            print('Child node scores:', [child.score for child in self.tree.children])
            print(f'Best move: {best_move}, Num visits: {self.tree.children[best_child].num_visits}')
        return best_move

    def get_stats(self):
        return self.stats


# testing
if __name__ == '__main__':
    board = chess.Board()

    mcts = MCTS(board)
    move = mcts.run(board, print_stats=True)

    board.push(move)

    print(board)
