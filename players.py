from games import alpha_beta_cutoff_search
from constants import DEPTH_PLAYER_NAMES, utility_score_diff
import numpy as np


INF = float('inf')


class Player():
    def move(self, game, state):
        raise NotImplementedError

    @staticmethod
    def make_eval_fn(game, player, utility_fn):
        """Build an eval lambda from a utility_fn(game, board) -> score-from-P1-perspective."""
        if player == 1:
            return lambda s: utility_fn(game, s.board)
        else:
            return lambda s: -utility_fn(game, s.board)


class RandomPlayer(Player):
    def move(self, game, state):
        random_move = game.random_move(state)
        state = game.result(state, random_move)

        return state


class AlphaBetaPlayer(Player):
    def __init__(self, depth=4, utility_fn=utility_score_diff):
        self.depth = depth
        self.utility_fn = utility_fn

    def move(self, game, state):
        eval_fn = self.make_eval_fn(game, state.to_move, self.utility_fn)
        best_move = alpha_beta_cutoff_search(state, game, d=self.depth, eval_fn=eval_fn)
        return game.result(state, best_move)


class HumanPlayer(Player):
    def move(self, game, state):
        game.display(state)
        valid_moves = game.actions(state)
        print(f"Valid moves: {valid_moves}")
        while True:
            try:
                choice = int(input("Your move: "))
                if choice in valid_moves:
                    return game.result(state, choice)
                print(f"Invalid move. Choose from {valid_moves}")
            except ValueError:
                print(f"Enter a number. Choose from {valid_moves}")


class MinimaxPlayer(Player):
    def __init__(self, depth=4, utility_fn=utility_score_diff):
        self.depth = depth
        self.utility_fn = utility_fn

    def _search(self, state, game, d, eval_fn):
        cutoff_test = lambda state, depth: depth > d or game.terminal_test(state)

        def max_value(state, depth):
            if cutoff_test(state, depth):
                return eval_fn(state)
            v = -np.inf
            for a in game.actions(state):
                v = max(v, min_value(game.result(state, a), depth + 1))
            return v

        def min_value(state, depth):
            if cutoff_test(state, depth):
                return eval_fn(state)
            v = np.inf
            for a in game.actions(state):
                v = min(v, max_value(game.result(state, a), depth + 1))
            return v

        best_score = -np.inf
        best_action = None
        for a in game.actions(state):
            v = min_value(game.result(state, a), 1)
            if v > best_score:
                best_score = v
                best_action = a
        return best_action

    def move(self, game, state):
        eval_fn = self.make_eval_fn(game, state.to_move, self.utility_fn)
        best_move = self._search(state, game, d=self.depth, eval_fn=eval_fn)
        return game.result(state, best_move)


class AlphaBetaTTPlayer(Player):
    def __init__(self, depth=4, utility_fn=utility_score_diff):
        self.depth = depth
        self.tt = {}
        self.utility_fn = utility_fn

    def _search(self, state, game, d, eval_fn):
        tt = self.tt
        cutoff_test = lambda state, depth: depth > d or game.terminal_test(state)

        def max_value(state, alpha, beta, depth):
            remaining = d - depth
            key = (state.board, state.to_move)
            entry = tt.get(key)
            if entry is not None:
                tt_val, tt_depth, tt_flag = entry
                if tt_depth >= remaining:
                    if tt_flag == 'exact':
                        return tt_val
                    elif tt_flag == 'lower':
                        alpha = max(alpha, tt_val)
                    elif tt_flag == 'upper':
                        beta = min(beta, tt_val)
                    if alpha >= beta:
                        return tt_val

            if cutoff_test(state, depth):
                val = eval_fn(state)
                tt[key] = (val, remaining, 'exact')
                return val

            orig_alpha = alpha
            v = -np.inf
            for a in game.actions(state):
                v = max(v, min_value(game.result(state, a), alpha, beta, depth + 1))
                if v >= beta:
                    tt[key] = (v, remaining, 'lower')
                    return v
                alpha = max(alpha, v)

            if v > orig_alpha:
                tt[key] = (v, remaining, 'exact')
            else:
                tt[key] = (v, remaining, 'upper')
            return v

        def min_value(state, alpha, beta, depth):
            remaining = d - depth
            key = (state.board, state.to_move)
            entry = tt.get(key)
            if entry is not None:
                tt_val, tt_depth, tt_flag = entry
                if tt_depth >= remaining:
                    if tt_flag == 'exact':
                        return tt_val
                    elif tt_flag == 'lower':
                        alpha = max(alpha, tt_val)
                    elif tt_flag == 'upper':
                        beta = min(beta, tt_val)
                    if alpha >= beta:
                        return tt_val

            if cutoff_test(state, depth):
                val = eval_fn(state)
                tt[key] = (val, remaining, 'exact')
                return val

            orig_beta = beta
            v = np.inf
            for a in game.actions(state):
                v = min(v, max_value(game.result(state, a), alpha, beta, depth + 1))
                if v <= alpha:
                    tt[key] = (v, remaining, 'upper')
                    return v
                beta = min(beta, v)

            if v < orig_beta:
                tt[key] = (v, remaining, 'exact')
            else:
                tt[key] = (v, remaining, 'lower')
            return v

        best_score = -np.inf
        beta = np.inf
        best_action = None
        for a in game.actions(state):
            v = min_value(game.result(state, a), best_score, beta, 1)
            if v > best_score:
                best_score = v
                best_action = a
        return best_action

    def move(self, game, state):
        eval_fn = self.make_eval_fn(game, state.to_move, self.utility_fn)
        best_move = self._search(state, game, d=self.depth, eval_fn=eval_fn)
        return game.result(state, best_move)


class AlphaBetaTTMvOrderPlayer(Player):
    def __init__(self, depth=4, utility_fn=utility_score_diff):
        self.depth = depth
        self.tt = {}
        self.utility_fn = utility_fn

    def _order_moves(self, actions, tt_best_move):
        if tt_best_move is not None and tt_best_move in actions:
            return [tt_best_move] + [a for a in actions if a != tt_best_move]
        return actions

    def _search(self, state, game, d, eval_fn):
        tt = self.tt
        cutoff_test = lambda state, depth: depth > d or game.terminal_test(state)

        def max_value(state, alpha, beta, depth):
            remaining = d - depth
            key = (state.board, state.to_move)
            entry = tt.get(key)
            tt_best_move = None
            if entry is not None:
                tt_val, tt_depth, tt_flag, tt_best_move = entry
                if tt_depth >= remaining:
                    if tt_flag == 'exact':
                        return tt_val
                    elif tt_flag == 'lower':
                        alpha = max(alpha, tt_val)
                    elif tt_flag == 'upper':
                        beta = min(beta, tt_val)
                    if alpha >= beta:
                        return tt_val

            if cutoff_test(state, depth):
                val = eval_fn(state)
                tt[key] = (val, remaining, 'exact', None)
                return val

            orig_alpha = alpha
            v = -np.inf
            best_a = None
            for a in self._order_moves(game.actions(state), tt_best_move):
                child_val = min_value(game.result(state, a), alpha, beta, depth + 1)
                if child_val > v:
                    v = child_val
                    best_a = a
                if v >= beta:
                    tt[key] = (v, remaining, 'lower', best_a)
                    return v
                alpha = max(alpha, v)

            if v > orig_alpha:
                tt[key] = (v, remaining, 'exact', best_a)
            else:
                tt[key] = (v, remaining, 'upper', best_a)
            return v

        def min_value(state, alpha, beta, depth):
            remaining = d - depth
            key = (state.board, state.to_move)
            entry = tt.get(key)
            tt_best_move = None
            if entry is not None:
                tt_val, tt_depth, tt_flag, tt_best_move = entry
                if tt_depth >= remaining:
                    if tt_flag == 'exact':
                        return tt_val
                    elif tt_flag == 'lower':
                        alpha = max(alpha, tt_val)
                    elif tt_flag == 'upper':
                        beta = min(beta, tt_val)
                    if alpha >= beta:
                        return tt_val

            if cutoff_test(state, depth):
                val = eval_fn(state)
                tt[key] = (val, remaining, 'exact', None)
                return val

            orig_beta = beta
            v = np.inf
            best_a = None
            for a in self._order_moves(game.actions(state), tt_best_move):
                child_val = max_value(game.result(state, a), alpha, beta, depth + 1)
                if child_val < v:
                    v = child_val
                    best_a = a
                if v <= alpha:
                    tt[key] = (v, remaining, 'upper', best_a)
                    return v
                beta = min(beta, v)

            if v < orig_beta:
                tt[key] = (v, remaining, 'exact', best_a)
            else:
                tt[key] = (v, remaining, 'lower', best_a)
            return v

        best_score = -np.inf
        beta = np.inf
        best_action = None
        for a in game.actions(state):
            v = min_value(game.result(state, a), best_score, beta, 1)
            if v > best_score:
                best_score = v
                best_action = a
        return best_action

    def move(self, game, state):
        eval_fn = self.make_eval_fn(game, state.to_move, self.utility_fn)
        best_move = self._search(state, game, d=self.depth, eval_fn=eval_fn)
        return game.result(state, best_move)


class AlphaBetaTTMvOrderInfPlayer(Player):
    def __init__(self, depth=4, utility_fn=utility_score_diff):
        self.depth = depth
        self.tt = {}
        self.utility_fn = utility_fn

    def _order_moves(self, actions, tt_best_move):
        if tt_best_move is not None and tt_best_move in actions:
            return [tt_best_move] + [a for a in actions if a != tt_best_move]
        return actions

    def _search(self, state, game, d, eval_fn):
        tt = self.tt
        cutoff_test = lambda state, depth: depth > d or game.terminal_test(state)

        def max_value(state, alpha, beta, depth):
            remaining = d - depth
            key = (state.board, state.to_move)
            entry = tt.get(key)
            tt_best_move = None
            if entry is not None:
                tt_val, tt_depth, tt_flag, tt_best_move = entry
                if tt_depth >= remaining:
                    if tt_flag == 'exact':
                        return tt_val
                    elif tt_flag == 'lower':
                        alpha = max(alpha, tt_val)
                    elif tt_flag == 'upper':
                        beta = min(beta, tt_val)
                    if alpha >= beta:
                        return tt_val

            if cutoff_test(state, depth):
                val = eval_fn(state)
                tt[key] = (val, remaining, 'exact', None)
                return val

            orig_alpha = alpha
            v = -INF
            best_a = None
            for a in self._order_moves(game.actions(state), tt_best_move):
                child_val = min_value(game.result(state, a), alpha, beta, depth + 1)
                if child_val > v:
                    v = child_val
                    best_a = a
                if v >= beta:
                    tt[key] = (v, remaining, 'lower', best_a)
                    return v
                alpha = max(alpha, v)

            if v > orig_alpha:
                tt[key] = (v, remaining, 'exact', best_a)
            else:
                tt[key] = (v, remaining, 'upper', best_a)
            return v

        def min_value(state, alpha, beta, depth):
            remaining = d - depth
            key = (state.board, state.to_move)
            entry = tt.get(key)
            tt_best_move = None
            if entry is not None:
                tt_val, tt_depth, tt_flag, tt_best_move = entry
                if tt_depth >= remaining:
                    if tt_flag == 'exact':
                        return tt_val
                    elif tt_flag == 'lower':
                        alpha = max(alpha, tt_val)
                    elif tt_flag == 'upper':
                        beta = min(beta, tt_val)
                    if alpha >= beta:
                        return tt_val

            if cutoff_test(state, depth):
                val = eval_fn(state)
                tt[key] = (val, remaining, 'exact', None)
                return val

            orig_beta = beta
            v = INF
            best_a = None
            for a in self._order_moves(game.actions(state), tt_best_move):
                child_val = max_value(game.result(state, a), alpha, beta, depth + 1)
                if child_val < v:
                    v = child_val
                    best_a = a
                if v <= alpha:
                    tt[key] = (v, remaining, 'upper', best_a)
                    return v
                beta = min(beta, v)

            if v < orig_beta:
                tt[key] = (v, remaining, 'exact', best_a)
            else:
                tt[key] = (v, remaining, 'lower', best_a)
            return v

        best_score = -INF
        beta = INF
        best_action = None
        for a in game.actions(state):
            v = min_value(game.result(state, a), best_score, beta, 1)
            if v > best_score:
                best_score = v
                best_action = a
        return best_action

    def move(self, game, state):
        eval_fn = self.make_eval_fn(game, state.to_move, self.utility_fn)
        best_move = self._search(state, game, d=self.depth, eval_fn=eval_fn)
        return game.result(state, best_move)


class AlphaBetaTTMvOrderInfIDPlayer(AlphaBetaTTMvOrderInfPlayer):
    def move(self, game, state):
        eval_fn = self.make_eval_fn(game, state.to_move, self.utility_fn)
        best_move = None
        for d in range(1, self.depth + 1):
            best_move = self._search(state, game, d=d, eval_fn=eval_fn)
        return game.result(state, best_move)


PLAYER_TYPES = {
    "random": RandomPlayer,
    "alphabeta": AlphaBetaPlayer,
    "alphabeta_tt": AlphaBetaTTPlayer,
    "alphabeta_tt_mvorder": AlphaBetaTTMvOrderPlayer,
    "alphabeta_tt_mvorder_inf": AlphaBetaTTMvOrderInfPlayer,
    "alphabeta_tt_mvorder_inf_id": AlphaBetaTTMvOrderInfIDPlayer,
    "minimax": MinimaxPlayer,
    "human": HumanPlayer,
}


PLAYER_TYPE_NAMES = {v: k for k, v in PLAYER_TYPES.items()}

DEPTH_PLAYERS = DEPTH_PLAYER_NAMES


def make_player(player_type, depth, utility_fn=None):
    if player_type in DEPTH_PLAYERS:
        return PLAYER_TYPES[player_type](depth=depth, utility_fn=utility_fn)
    return PLAYER_TYPES[player_type]()
