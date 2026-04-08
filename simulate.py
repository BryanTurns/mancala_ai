from mancala_aima import MancalaAIMA
import argparse


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

        self.display_current_simulation_stats()

    def display_current_simulation_stats(self):
        print(f"Results over {self.simulation_stats["num_games"]} games:")
        print(f"  Avg turns per game : {self.simulation_stats["avg_turns"]:.1f}")
        print(f"         Win%   Loss%   Tie%")
        print(f"  P1:   {self.simulation_stats["p1_wins"]/self.simulation_stats["num_games"]*100:5.1f}%  {self.simulation_stats["p2_wins"]/self.simulation_stats["num_games"]*100:5.1f}%  {self.simulation_stats["ties"]/self.simulation_stats["num_games"]*100:5.1f}%")
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


PLAYER_TYPES = {
    "random": RandomPlayer,
}


def main():
    parser = argparse.ArgumentParser(description="Simulate Mancala games")
    parser.add_argument("-n", "--num-games", type=int, default=100, help="number of games to simulate (default: 100)")
    parser.add_argument("--p1", choices=PLAYER_TYPES.keys(), default="random", help="player 1 type (default: random)")
    parser.add_argument("--p2", choices=PLAYER_TYPES.keys(), default="random", help="player 2 type (default: random)")
    args = parser.parse_args()

    p1 = PLAYER_TYPES[args.p1]()
    p2 = PLAYER_TYPES[args.p2]()

    simulation = Simulator(p1, p2, args.num_games)
    simulation.simulate()



if __name__ == "__main__":
    main()
