import json
import os
import glob
import argparse
import fnmatch
import matplotlib.pyplot as plt
from constants import DEPTH_PLAYER_NAMES

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def load_results(include_incomplete=False):
    """Load results, keeping only the highest-n run per config."""
    files = glob.glob(os.path.join(RESULTS_DIR, "*.json"))
    best = {}
    for f in files:
        if not include_incomplete and os.path.basename(f).startswith("incomplete_"):
            continue
        with open(f) as fh:
            data = json.load(fh)
        cfg = data["config"]
        key = (cfg["p1_type"], cfg["p2_type"], cfg["p1_depth"], cfg["p2_depth"])
        if key not in best or cfg["num_games"] > best[key]["config"]["num_games"]:
            best[key] = data
    return list(best.values())


def chart_winrate_vs_depth(results, show_baseline=True):
    """Line chart: P1 win rate vs depth, grouped by player type matchup."""
    series = {}
    for r in results:
        p1_type = r["config"]["p1_type"]
        p2_type = r["config"]["p2_type"]
        p1_depth = r["config"]["p1_depth"]
        if p1_depth is None:
            continue
        label = f"{p1_type} vs {p2_type}"
        if label not in series:
            series[label] = {"depths": [], "winrates": []}
        series[label]["depths"].append(p1_depth)
        series[label]["winrates"].append(r["results"]["p1_winrate"] * 100)

    # Find random vs random baseline
    random_winrate = None
    if show_baseline:
        for r in results:
            if r["config"]["p1_type"] == "random" and r["config"]["p2_type"] == "random":
                random_winrate = r["results"]["p1_winrate"] * 100

    if not series and random_winrate is None:
        print("No results to plot for win rate chart.")
        return

    fig, ax = plt.subplots()
    for label, data in series.items():
        depths, winrates = zip(*sorted(zip(data["depths"], data["winrates"])))
        ax.plot(depths, winrates, marker="o", label=label)

    if random_winrate is not None:
        ax.axhline(y=random_winrate, color="gray", linestyle="--", label=f"random vs random ({random_winrate:.1f}%)")

    ax.set_xlabel("Depth (plies)")
    ax.set_ylabel("P1 Win Rate (%)")
    ax.set_title("Win Rate vs Search Depth")
    ax.legend()
    ax.grid(True)

    filepath = os.path.join(RESULTS_DIR, "winrate_vs_depth.png")
    fig.savefig(filepath, dpi=150, bbox_inches="tight")
    print(f"Saved {filepath}")
    plt.close(fig)


def chart_timing_comparison(results, log_scale=False):
    """Line chart: avg time per game for minimax vs alphabeta at same depths."""
    series = {}
    for r in results:
        p1_type = r["config"]["p1_type"]
        p1_depth = r["config"]["p1_depth"]
        if p1_depth is None or p1_type not in DEPTH_PLAYER_NAMES:
            continue
        p2_type = r["config"]["p2_type"]
        label = f"{p1_type} vs {p2_type}"
        if label not in series:
            series[label] = {"depths": [], "times": []}
        series[label]["depths"].append(p1_depth)
        series[label]["times"].append(r["results"]["avg_time_per_game"])

    if not series:
        print("No timing results to plot.")
        return

    fig, ax = plt.subplots()
    for label, data in series.items():
        depths, times = zip(*sorted(zip(data["depths"], data["times"])))
        ax.plot(depths, times, marker="o", label=label)

    if log_scale:
        ax.set_yscale("log")

    ax.set_xlabel("Depth (plies)")
    ax.set_ylabel("Avg Time per Game (s)")
    ax.set_title("Search Algorithm Timing Comparison")
    ax.legend()
    ax.grid(True)

    filepath = os.path.join(RESULTS_DIR, "timing_comparison.png")
    fig.savefig(filepath, dpi=150, bbox_inches="tight")
    print(f"Saved {filepath}")
    plt.close(fig)


def chart_turns_vs_depth(results):
    """Line chart: avg turns per game vs depth, grouped by player type matchup."""
    series = {}
    for r in results:
        p1_type = r["config"]["p1_type"]
        p2_type = r["config"]["p2_type"]
        p1_depth = r["config"]["p1_depth"]
        if p1_depth is None:
            continue
        label = f"{p1_type} vs {p2_type}"
        if label not in series:
            series[label] = {"depths": [], "turns": []}
        series[label]["depths"].append(p1_depth)
        series[label]["turns"].append(r["results"]["avg_turns_per_game"])

    # Find random vs random baseline
    random_turns = None
    for r in results:
            if r["config"]["p1_type"] == "random" and r["config"]["p2_type"] == "random":
                random_turns = r["results"]["avg_turns_per_game"]

    if not series and random_turns is None:
        print("No results to plot for turns chart.")
        return

    fig, ax = plt.subplots()
    for label, data in series.items():
        depths, turns = zip(*sorted(zip(data["depths"], data["turns"])))
        ax.plot(depths, turns, marker="o", label=label)

    if random_turns is not None:
        ax.axhline(y=random_turns, color="gray", linestyle="--", label=f"random vs random ({random_turns:.1f})")

    ax.set_xlabel("Depth (plies)")
    ax.set_ylabel("Avg Turns per Game")
    ax.set_title("Game Length vs Search Depth")
    ax.legend()
    ax.grid(True)

    filepath = os.path.join(RESULTS_DIR, "turns_vs_depth.png")
    fig.savefig(filepath, dpi=150, bbox_inches="tight")
    print(f"Saved {filepath}")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Generate charts from simulation results")
    parser.add_argument("--no-baseline", action="store_true", help="omit the random vs random baseline from the win rate chart")
    parser.add_argument("--include-incomplete", action="store_true", help="include incomplete simulation runs")
    parser.add_argument("--log-time", action="store_true", help="use logarithmic scale for the timing chart y-axis")
    parser.add_argument("--max-depth", type=int, default=None, help="maximum depth to display in charts")
    parser.add_argument("--players", type=str, default=None, help="comma-separated list of player types to include (filters on p1_type)")
    args = parser.parse_args()

    results = load_results(include_incomplete=args.include_incomplete)
    if not results:
        print(f"No result files found in {RESULTS_DIR}")
        return
    if args.players is not None:
        patterns = [p.strip() for p in args.players.split(",")]
        results = [r for r in results if
                   any(fnmatch.fnmatch(r["config"]["p1_type"], p) or fnmatch.fnmatch(r["config"]["p2_type"], p) for p in patterns)]
    if args.max_depth is not None:
        results = [r for r in results if r["config"]["p1_depth"] is None or r["config"]["p1_depth"] <= args.max_depth]
    chart_winrate_vs_depth(results, show_baseline=not args.no_baseline)
    chart_timing_comparison(results, log_scale=args.log_time)
    chart_turns_vs_depth(results)


if __name__ == "__main__":
    main()
