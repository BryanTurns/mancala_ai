import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'aima-python'))
from games import Game, GameState


class MancalaAIMA(Game):
    def __init__(self, pits_per_player=6, stones_per_pit=4):
        self.pits_per_player = pits_per_player

        self.p1_mancala_index = pits_per_player
        self.p2_mancala_index = (pits_per_player + 1) * 2 - 1
        self.p1_pits_index = [0, pits_per_player - 1]
        self.p2_pits_index = [pits_per_player + 1, pits_per_player * 2]

        board_list = [stones_per_pit] * ((pits_per_player + 1) * 2)
        board_list[self.p1_mancala_index] = 0
        board_list[self.p2_mancala_index] = 0
        initial_board = tuple(board_list)

        self.initial = GameState(
            to_move=1,
            utility=0,
            board=initial_board,
            moves=self._compute_valid_moves(initial_board, 1)
        )

    def _compute_valid_moves(self, board, player):
        if player == 1:
            start, end = self.p1_pits_index
        else:
            start, end = self.p2_pits_index
        return [i + 1 for i, idx in enumerate(range(start, end + 1)) if board[idx] > 0]

    def _is_terminal(self, board):
        p1_empty = all(board[i] == 0 for i in range(self.p1_pits_index[0], self.p1_pits_index[1] + 1))
        p2_empty = all(board[i] == 0 for i in range(self.p2_pits_index[0], self.p2_pits_index[1] + 1))
        return p1_empty or p2_empty

    def _compute_utility(self, board):
        return board[self.p1_mancala_index] - board[self.p2_mancala_index]

    def actions(self, state):
        return state.moves
    
    def random_move(self, state):
        return state.moves[random.randint(0, len(state.moves)-1)]

    def result(self, state, move):
        board = list(state.board)
        player = state.to_move

        if player == 1:
            start_index = self.p1_pits_index[0] + move - 1
            opponent_mancala = self.p2_mancala_index
            own_pits_start, own_pits_end = self.p1_pits_index
            own_mancala = self.p1_mancala_index
        else:
            start_index = self.p2_pits_index[0] + move - 1
            opponent_mancala = self.p1_mancala_index
            own_pits_start, own_pits_end = self.p2_pits_index
            own_mancala = self.p2_mancala_index

        num_stones = board[start_index]
        stones_used = 0
        index = start_index
        board_len = len(board)

        while stones_used < num_stones:
            index += 1
            if index == opponent_mancala:
                continue
            elif index >= board_len:
                index = 0
            board[index] += 1
            stones_used += 1

        board[start_index] = 0

        if own_pits_start <= index <= own_pits_end and board[index] == 1:
            opposite = self.p1_pits_index[1] + self.p2_pits_index[0] - index
            board[own_mancala] += board[index] + board[opposite]
            board[index] = 0
            board[opposite] = 0

        next_player = 2 if player == 1 else 1
        new_board = tuple(board)

        if self._is_terminal(new_board):
            util = self._compute_utility(new_board)
            new_moves = []
        else:
            util = 0
            new_moves = self._compute_valid_moves(new_board, next_player)

        return GameState(to_move=next_player, utility=util, board=new_board, moves=new_moves)

    def terminal_test(self, state):
        return len(state.moves) == 0

    def utility(self, state, player):
        return state.utility if player == 1 else -state.utility

    def display(self, state):
        board = state.board
        p1_pits = board[self.p1_pits_index[0]: self.p1_pits_index[1] + 1]
        p1_mancala = board[self.p1_mancala_index]
        p2_pits = board[self.p2_pits_index[0]: self.p2_pits_index[1] + 1]
        p2_mancala = board[self.p2_mancala_index]

        print('P1               P2')
        print('     ____{}____     '.format(p2_mancala))
        for i in range(self.pits_per_player):
            if i == self.pits_per_player - 1:
                print('{} -> |_{}_|_{}_| <- {}'.format(
                    i + 1, p1_pits[i], p2_pits[-(i + 1)], self.pits_per_player - i))
            else:
                print('{} -> | {} | {} | <- {}'.format(
                    i + 1, p1_pits[i], p2_pits[-(i + 1)], self.pits_per_player - i))
        print('         {}         '.format(p1_mancala))
        turn = 'P1' if state.to_move == 1 else 'P2'
        print('Turn: ' + turn)
