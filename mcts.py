import math

import chess
# from node import MCTS_Node

import time
import random
import numpy as np
from functions.eval import evaluate
from anytree import RenderTree
from node import MCTSNode
from copy import deepcopy


class MCTS:
    def __init__(self, board: chess.Board, **kwargs):
        self.board = board.copy()
        self.max_time = kwargs.get('max_time', 5)
        self.max_moves = kwargs.get('max_moves', 1000)
        self.max_sims = kwargs.get('max_sims', 1000)
        self.C = kwargs.get('C', 2)
        self.node_counter = 0
        self.tree = MCTSNode(
            f'S{self.node_counter}',
            state=board.fen(),
            score=0,
        )

    def get_untried_actions(self, board):
        return list(board.legal_moves)

    def get_random_move(self, curr_board):
        return random.choice([move for move in curr_board.legal_moves])

    def uct(self, curr_node, log):
        # Q/V + C*sqrt(2*ln(num_visits parent))/num_visits)
        return curr_node.score/curr_node.num_visits + \
                                self.C * math.sqrt(log/curr_node.num_visits)

    def selection(self):
        # use UCT (UCB applied to trees) for balancing exploration and exploitation.
        #node = deepcopy(self.root)
        node = self.tree  # set current node to root
        while not node.is_leaf:  # continue until a leaf node is found (no children)
            #if node.children is None: # if node is not fully expanded
            #    return node
            #else:
            if node.is_root:
                pass
            else:
                best_uct_score = -math.inf
                log = math.log(node.num_visits)
                for child_node in node.children:
                    uct_score = self.uct(child_node, log)

                    if uct_score > best_uct_score:
                        best_uct_score = uct_score
                        node = child_node
        return node

    def expansion(self, node):
        # given a node, expand a random legal move as a child node
        # TODO: choose the child to expand with maximum priority (according to UCT formula) or random?
        board = chess.Board(node.state)
        move = self.get_random_move(board)
        new_board = board.copy()
        new_board.push(move)
        self.node_counter += 1
        child_node = MCTSNode(
            name=f'S{self.node_counter}',
            state=new_board.fen(),
            parent=node,
            action=move,
        )

    def simulation(self, curr_node):
        # simulate the game using randomly selected moves.

        curr_board = chess.Board(curr_node.state)
        for i in range(self.max_moves): # do until no more moves, or until game end?
            # first, check if the game is over
            if curr_board.is_game_over():
                if curr_board.result() == '1-0': # if win
                    return 1  # TODO: how much reward to give for win?
                elif curr_board.result() == '0-1': # if lose
                    return 0  # TODO: how much negative reward to give for lose?
                else: # if tie
                    return 0  # TODO: how much reward for draw?
            random_move = self.get_random_move(curr_board)
            curr_board.push(random_move)
        # if there is no victor after the max number of moves has been made, use evaluation function.
        score = evaluate(curr_board, True)
        if score > 150:
            return 1
        else:
            return 0

    def backpropagation(self, node, result):
        # update the tree by backpropagation of results
        while node:
            node.score += result # increment by reward
            node.num_visits += 1
            node = node.parent

    def iteration(self):
        # run through one iteration of MCTS - selection, expansion, simulation, and backpropagation.
        selected_node = self.selection()
        self.expansion(selected_node)
        result = self.simulation() # TODO: put the selected node child in here? what if terminal node?
        self.backpropagation(selected_node, result)


    def run(self):
        start_time = time.time()
        time_taken = 0
        # computational budget = max number of steps and max allowed time
        for i in range(self.max_sims):
            self.iteration()
            if self.max_time is not None and (time.time() - start_time) > self.max_time:
                time_taken = time.time() - start_time
                break

        # get the best action using the 'robust child' method
        # TODO: experiment with max child
        best_child = np.argmax([child.num_visits for child in self.tree.children])
        best_move = self.tree.children[best_child].action
        print(f'Time elapsed: {time_taken}, Steps completed: {i+1}')
        return best_move

    def get_stats(self):
        pass


