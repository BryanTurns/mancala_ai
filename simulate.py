from mancala_aima import MancalaAIMA
from games import alpha_beta_cutoff_search
import numpy as np
import argparse
import time


def main():
    parser = argparse.ArgumentParser(description="Simulate Mancala games")
    parser.add_argument("-n", "--num-games", type=int, default=100, help="number of games to simulate (default: 100)")
    parser.add_argument("--p1", choices=PLAYER_TYPES.keys(), default="random", help="player 1 type (default: random)")
    parser.add_argument("--p2", choices=PLAYER_TYPES.keys(), default="random", help="player 2 type (default: random)")
    parser.add_argument("--p1-depth", type=int, default=4, help="search depth for player 1 (default: 4)")
    parser.add_argument("--p2-depth", type=int, default=4, help="search depth for player 2 (default: 4)")
    args = parser.parse_args()

    if args.p1 not in DEPTH_PLAYERS and args.p1_depth != 4:
        parser.error(f"--p1-depth is not applicable for player type '{args.p1}'")
    if args.p2 not in DEPTH_PLAYERS and args.p2_depth != 4:
        parser.error(f"--p2-depth is not applicable for player type '{args.p2}'")

    p1 = make_player(args.p1, args.p1_depth)
    p2 = make_player(args.p2, args.p2_depth)

    simulation = Simulator(p1, p2, args.num_games)
    simulation.simulate()


class Player():
    def move(self, game, state):
        raise NotImplementedError


class Simulator():
    def __init__(self, p1: Player, p2: Player, simulation_count: int, num_pits: int = 6, stones_per_pit: int =4):
        self.p1 = p1
        self.p2 = p2
        self.simulation_count = simulation_count
        self.simulation_stats = {"p1_wins": 0, "p2_wins": 0, "ties": 0, "avg_turns": 0, "num_games": 0}

    def simulate(self):
        start_time = time.time()

        for i in range(self.simulation_count):
            if i % 50 == 0 and i != 0:
                self.display_current_simulation_stats()

            game = MancalaAIMA()
            winner, turn_count = self.play_game(game)

            self.simulation_stats["avg_turns"] = (self.simulation_stats["num_games"] * self.simulation_stats["avg_turns"] + turn_count) / (self.simulation_stats["num_games"] + 1)
            if winner == 0:
                self.simulation_stats["ties"] += 1
            elif winner == 1:
                self.simulation_stats["p1_wins"] += 1
            elif winner == 2:
                self.simulation_stats["p2_wins"] += 1
            else:
                raise ValueError(f"play_game returned invalid winner value {winner}")

            self.simulation_stats["num_games"] += 1

        elapsed = time.time() - start_time
        self.display_current_simulation_stats()
        print(f"Simulation completed in {elapsed:.3f}s")

    def display_current_simulation_stats(self):
        print(f"Results over {self.simulation_stats["num_games"]} games:")
        print(f"  Avg turns per game : {self.simulation_stats["avg_turns"]:.1f}")
        print(f"         Win%   Loss%   Tie%")
        print(f"  P1:   {self.simulation_stats["p1_wins"]/self.simulation_stats["num_games"]*100:5.2f}%  {self.simulation_stats["p2_wins"]/self.simulation_stats["num_games"]*100:5.2f}%  {self.simulation_stats["ties"]/self.simulation_stats["num_games"]*100:5.2f}%")
        print()


    # Take a game object and play it out with the players the simulation was defined by
    # Return 1 if player 1 wins, 2 if player 2 wins, and 0 for a tie
    def play_game(self, game: MancalaAIMA):
        state = game.initial
        turn_count = 0
        while not game.terminal_test(state):
            turn_count += 1
            if state.to_move == 1:
                state = self.p1.move(game, state)
            else:
                state = self.p2.move(game, state)

        p1_stones = state.board[game.p1_mancala_index]
        p2_stones = state.board[game.p2_mancala_index]

        if p1_stones > p2_stones:
            return (1, turn_count)
        elif p2_stones > p1_stones:
            return (2, turn_count)
        else:
            return (0, turn_count) 


class RandomPlayer(Player):
    def move(self, game, state):
        random_move = game.random_move(state)
        state = game.result(state, random_move)

        return state


class AlphaBetaPlayer(Player):
    def __init__(self, depth=4):
        self.depth = depth

    def move(self, game, state):
        player = state.to_move
        eval_fn = lambda s: game._compute_utility(s.board) if player == 1 else -game._compute_utility(s.board)
        best_move = alpha_beta_cutoff_search(state, game, d=self.depth, eval_fn=eval_fn)
        return game.result(state, best_move)


def minmax_cutoff_search(state, game, d=4, cutoff_test=None, eval_fn=None):
    player = game.to_move(state)
    cutoff_test = cutoff_test or (lambda state, depth: depth > d or game.terminal_test(state))
    eval_fn = eval_fn or (lambda state: game.utility(state, player))

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
    def __init__(self, depth=4):
        self.depth = depth

    def move(self, game, state):
        player = state.to_move
        eval_fn = lambda s: game._compute_utility(s.board) if player == 1 else -game._compute_utility(s.board)
        best_move = minmax_cutoff_search(state, game, d=self.depth, eval_fn=eval_fn)
        return game.result(state, best_move)


PLAYER_TYPES = {
    "random": RandomPlayer,
    "alphabeta": AlphaBetaPlayer,
    "minimax": MinimaxPlayer,
    "human": HumanPlayer,
}


DEPTH_PLAYERS = {"alphabeta", "minimax"}


def make_player(player_type, depth):
    if player_type in DEPTH_PLAYERS:
        return PLAYER_TYPES[player_type](depth=depth)
    return PLAYER_TYPES[player_type]()


if __name__ == "__main__":
    main()
