DEPTH_PLAYER_NAMES = {"alphabeta", "alphabeta_tt", "alphabeta_tt_mvorder", "alphabeta_tt_mvorder_inf", "alphabeta_tt_mvorder_inf_id", "minimax"}


def utility_score_diff(game, board):
    """Default: simple score difference (P1 mancala - P2 mancala)."""
    return board[game.p1_mancala_index] - board[game.p2_mancala_index]


UTILITY_FUNCTIONS = {
    "score_diff": utility_score_diff,
}
