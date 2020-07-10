class InputOutOfRange(Exception):
    pass


class CellNotEmpty(Exception):
    pass


class TicTacToe:
    def __init__(self, board=None, player_turn=1):
        if type(board) == list:
            self.board = board
        elif type(board) == str and len(board) == 9:
            self.board = [[int(j) for j in board[i * 3:i * 3 + 3]] for i in range(3)]
        else:
            self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

        self.player_turn = player_turn if player_turn in [1, 2] else 1
        self.winner = None

    def _display_board(self):
        [print(i) for i in self.board]

    def board_as_string(self):
        return ''.join(str(i) for i in self.board[0] + self.board[1] + self.board[2])

    def _change_turn(self):
        self.player_turn = 1 if self.player_turn == 2 else 2

    def _update_winner(self):

        def check_triplet(s):
            s_set = set(s)
            if len(s_set) == 1:
                result = s_set.pop()
                if result != 0:
                    self.winner = result
                    return True

        # vertical
        for i in range(3):
            column = [row[i] for row in self.board]
            if check_triplet(column):
                return

        # horizontal
        for row in self.board:
            if check_triplet(row):
                return

        # top left to bottom right
        across = [self.board[i][i] for i in range(3)]
        if check_triplet(across):
            return

        # top right to bottom left
        across = [self.board[i][2 - i] for i in range(3)]
        if check_triplet(across):
            return

        # check if there is a 0 if not, return 0 which is a draw
        for row in self.board:
            if 0 in row:
                return

        self.winner = 0

    def move(self, x, y):
        if x not in range(0, 3) or y not in range(0, 3):
            raise InputOutOfRange
        if self.board[y][x]:
            raise CellNotEmpty
        self.board[y][x] = self.player_turn
        self._update_winner()
        if self.winner is not None:
            return self.winner
        self._change_turn()

    def restart(self):
        self.__init__(player_turn=self.winner)
