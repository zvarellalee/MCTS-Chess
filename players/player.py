# Player interface class
class Player:
    def get_next_move(self, board, verbose):
        """get the next move from the supplied engine"""
        pass

    def reset(self):
        """reset the search tree"""
        pass

    def close(self):
        """close uci cmd"""
        pass

    def get_name(self):
        """returns the name of the Player"""
        pass