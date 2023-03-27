from anytree import NodeMixin, RenderTree
import random

MAX_SCORE = 10000


class MCTSNode(NodeMixin):
    """
    Node class for MCTS implementations.
    """
    def __init__(self, name, board, score=0, heuristic_score=0, action=None, parent=None, children=None):
        super(MCTSNode, self).__init__()
        # ---- Base parameters ----
        self.name = name # node identifier
        self.state = board.fen() # current board state (FEN string)
        self.score = score  # the total rewards from MCTS exploration
        self.num_visits = 0  # visit count of the node
        self.is_game_over = board.is_game_over()  # terminal node identifier - precalculating this saves time
        self.is_white = board.turn  # store the turn of the node
        moves = list(board.legal_moves)
        random.shuffle(moves)
        self.untried_actions = moves  # store all the untried actions as a list
        if action:
            self.action = action  # the move performed by selecting this node from the parent
        self.parent = parent  # parent to this node
        if children:
            self.children = children  # children to this node
        # ---- Progressive bias parameters ----
        self.heuristic_score = heuristic_score  # heuristic value of node's state
        # ---- Score bounded search parameters ----
        self.pess_bound = -MAX_SCORE  # lower boundary
        self.opti_bound = heuristic_score  # upper boundary
        if self.is_game_over:
            self.outcome = board.result()  # store game result
        # ---- Progressive unpruning parameters ----
        self.sorted_children = []
        self.num_unpruned = 0

    def sort_children(self):
        """
        Sort nodes by their average score
        """
        self.sorted_children = sorted(self.children, reverse=True)

    def alpha_beta_pruning(self):
        """
        Do hard alpha beta pruning and return the sorted list of remaining children nodes
        """
        self.sort_children()
        new_child_list = []
        pruned_list = []
        for child in self.sorted_children:
            if not -child.pess_bound <= self.pess_bound or (-child.pess_bound == self.opti_bound and child.pess_bound == child.opti_bound):
                new_child_list.append(child)
            else:
                pruned_list.append(child)
        self.sorted_children = new_child_list

    def __lt__(self, other):
        return self.score / self.num_visits < other.score / other.num_visits
