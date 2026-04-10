from mancala_aima import MancalaAIMA
from players import Player, PLAYER_TYPES, PLAYER_TYPE_NAMES, DEPTH_PLAYERS, make_player
import argparse
import json
import os
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


class Simulator():
    def __init__(self, p1: Player, p2: Player, simulation_count: int, num_pits: int = 6, stones_per_pit: int = 4):
        self.p1 = p1
        self.p2 = p2
        self.simulation_count = simulation_count
        self.simulation_stats = {"p1_wins": 0, "p2_wins": 0, "ties": 0, "avg_turns": 0, "num_games": 0}

    def simulate(self):
        start_time = time.time()

        try:
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
        except KeyboardInterrupt:
            print("\nInterrupted!")

        elapsed = time.time() - start_time
        interrupted = self.simulation_stats["num_games"] < self.simulation_count
        if self.simulation_stats["num_games"] > 0:
            self.display_current_simulation_stats()
            print(f"Simulation completed in {elapsed:.3f}s")
            print(f"Average time per game: {elapsed / self.simulation_stats['num_games']:.3f}s")
            self.save_results(elapsed, interrupted)

    def display_current_simulation_stats(self):
        print(f"Results over {self.simulation_stats["num_games"]} games:")
        print(f"  Avg turns per game : {self.simulation_stats["avg_turns"]:.1f}")
        print(f"         Win%   Loss%   Tie%")
        print(f"  P1:   {self.simulation_stats["p1_wins"]/self.simulation_stats["num_games"]*100:5.2f}%  {self.simulation_stats["p2_wins"]/self.simulation_stats["num_games"]*100:5.2f}%  {self.simulation_stats["ties"]/self.simulation_stats["num_games"]*100:5.2f}%")
        print()


    def _player_label(self, player):
        name = PLAYER_TYPE_NAMES[type(player)]
        depth = getattr(player, "depth", None)
        return f"{name}_d{depth}" if depth is not None else name

    def save_results(self, elapsed, interrupted):
        num_games = self.simulation_stats["num_games"]
        p1_label = self._player_label(self.p1)
        p2_label = self._player_label(self.p2)
        p1_name = PLAYER_TYPE_NAMES[type(self.p1)]
        p2_name = PLAYER_TYPE_NAMES[type(self.p2)]
        filename = f"{p1_label}_vs_{p2_label}_n{num_games}.json"
        if interrupted:
            filename = f"incomplete_{filename}"

        results_dir = os.path.join(os.path.dirname(__file__), "results")
        os.makedirs(results_dir, exist_ok=True)

        data = {
            "config": {
                "num_games": num_games,
                "p1_type": p1_name,
                "p2_type": p2_name,
                "p1_depth": getattr(self.p1, "depth", None),
                "p2_depth": getattr(self.p2, "depth", None),
            },
            "results": {
                "avg_time_per_game": elapsed / num_games,
                "avg_turns_per_game": self.simulation_stats["avg_turns"],
                "p1_winrate": self.simulation_stats["p1_wins"] / num_games,
                "p1_tie_rate": self.simulation_stats["ties"] / num_games,
            },
        }

        filepath = os.path.join(results_dir, filename)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Results saved to {filepath}")

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


if __name__ == "__main__":
    main()
