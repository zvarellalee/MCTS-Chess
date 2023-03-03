from anytree import NodeMixin, RenderTree
import chess

class MCTSNode(NodeMixin):
    def __init__(self, name, state, score, action=None, parent=None, children=None):
        super(MCTSNode, self).__init__()
        self.name = name
        self.state = state
        self.score = score
        self.num_visits = 0
        if action:
            self.action = action
        self.parent = parent
        if children:
            self.children = children

    @property
    def untried_actions(self):
        board = chess.Board(self.state)
        return list(board.legal_moves)

    def q(self):
        pass



