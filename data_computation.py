"""CSC111 Project 2: Gomoku AI computation.

Description
===========
This module contains the AI computation logic for our Gomoku project:
- heuristic evaluation
- move ordering
- explicit game-tree expansion
- minimax search with alpha-beta pruning
- selecting the best move

The AI combines tree-based search with graph-based local board heuristics.

Copyright and Usage Information
===============================
This file was created by Kai Zang, Shiyuan Lyu, Seoyun Ju, and Emily Ye
for CSC111 at the University of Toronto St. George campus.

This file is provided solely for the personal and private use of the
instructors and TAs of CSC111 for the purpose of grading this work.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

import game_class


WIN_SCORE = 10_000_000
FOUR_SCORE = 100_000
THREE_SCORE = 5_000
TWO_SCORE = 200

OPEN_FOUR_BONUS = 40_000
OPEN_THREE_BONUS = 2_000
OPEN_TWO_BONUS = 80

CENTER_BONUS = 6
NEAR_BONUS_FRIEND = 8
NEAR_BONUS_ENEMY = 4

NEG_INF = -10**18
POS_INF = 10**18


@dataclass
class SearchContext:
    """Context data used during game-tree search.

    Instance Attributes:
        - graph: the board adjacency graph
        - ai_player: the AI player symbol
        - table: a transposition table for caching alpha-beta results
    """
    graph: game_class.BoardGraph
    ai_player: str
    table: dict[tuple[tuple[tuple[Optional[str], ...], ...], str, int, bool], int] = field(
        default_factory=dict
    )


def get_opponent(player: str) -> str:
    """Return the opponent of player.

    Preconditions:
        - player in {'X', 'O'}

    >>> get_opponent('X')
    'O'
    >>> get_opponent('O')
    'X'
    """
    return 'O' if player == 'X' else 'X'


def choose_best_move(
        state: game_class.GomokuState,
        graph: game_class.BoardGraph,
        ai_player: str,
        depth: int = 2) -> Optional[game_class.Move]:
    """Choose the best move for ai_player using explicit game-tree search.

    Return None if the state is terminal or if it is not ai_player's turn.

    Preconditions:
        - ai_player in {'X', 'O'}
        - depth >= 1
    """
    if state.is_terminal():
        return None
    if state.next_player != ai_player:
        return None

    context = SearchContext(graph, ai_player)

    winning_pos = _find_immediate_win(state, ai_player)
    if winning_pos is not None:
        return game_class.Move(winning_pos[0], winning_pos[1], ai_player)

    root = game_class.GameTree(state.copy())
    root_candidates = _root_candidate_moves(state, ai_player)
    _expand_tree_node(root, context, True, root_candidates)

    if root.subtrees == []:
        return None

    best_subtree = None
    best_score = NEG_INF
    alpha = NEG_INF
    beta = POS_INF

    for subtree in root.subtrees:
        score = alpha_beta(subtree, depth - 1, alpha, beta, False, context)
        subtree.score = score

        if score > best_score:
            best_score = score
            best_subtree = subtree

        alpha = max(alpha, best_score)

    if best_subtree is None or best_subtree.move is None:
        return None

    return best_subtree.move


def alpha_beta(
        tree: game_class.GameTree,
        depth: int,
        alpha: int,
        beta: int,
        maximizing: bool,
        context: SearchContext) -> int:
    """Return the alpha-beta score of tree.

    Preconditions:
        - depth >= 0
        - alpha <= beta
    """
    state = tree.state
    terminal = _terminal_score(state, context.ai_player, depth)
    if terminal is not None:
        tree.score = terminal
        return terminal

    if depth == 0:
        tree.score = evaluate_state(state, context.ai_player)
        return tree.score

    key = (state.to_key(), state.next_player, depth, maximizing)
    if key in context.table:
        tree.score = context.table[key]
        return tree.score

    _expand_tree_node(tree, context, maximizing)

    if tree.subtrees == []:
        tree.score = evaluate_state(state, context.ai_player)
        context.table[key] = tree.score
        return tree.score

    if maximizing:
        result = _alpha_beta_max(tree, depth, alpha, beta, context)
    else:
        result = _alpha_beta_min(tree, depth, alpha, beta, context)

    tree.score = result
    context.table[key] = result
    return result


def _alpha_beta_max(
        tree: game_class.GameTree,
        depth: int,
        alpha: int,
        beta: int,
        context: SearchContext) -> int:
    """Return the score of a maximizing tree node."""
    best = NEG_INF

    for subtree in tree.subtrees:
        score = alpha_beta(subtree, depth - 1, alpha, beta, False, context)
        subtree.score = score
        best = max(best, score)
        alpha = max(alpha, best)

        if beta <= alpha:
            break

    return best


def _alpha_beta_min(
        tree: game_class.GameTree,
        depth: int,
        alpha: int,
        beta: int,
        context: SearchContext) -> int:
    """Return the score of a minimizing tree node."""
    best = POS_INF

    for subtree in tree.subtrees:
        score = alpha_beta(subtree, depth - 1, alpha, beta, True, context)
        subtree.score = score
        best = min(best, score)
        beta = min(beta, best)

        if beta <= alpha:
            break

    return best


def _expand_tree_node(
        tree: game_class.GameTree,
        context: SearchContext,
        maximizing: bool,
        forced_candidates: Optional[list[tuple[int, int]]] = None) -> None:
    """Expand tree by one ordered layer if it is currently unexpanded."""
    if tree.subtrees != [] or tree.state.is_terminal():
        return

    state = tree.state
    if forced_candidates is None:
        candidate_moves = state.get_candidate_moves()
    else:
        candidate_moves = forced_candidates

    if candidate_moves == []:
        return

    ordered = ordered_moves(
        state, context.graph, context.ai_player, maximizing, candidate_moves
    )

    current_player = state.next_player
    for row, col in ordered:
        new_state = state.copy()
        success = new_state.make_move(row, col)
        if success:
            move = game_class.Move(row, col, current_player)
            tree.add_subtree(game_class.GameTree(new_state, move))


def _root_candidate_moves(
        state: game_class.GomokuState, ai_player: str) -> list[tuple[int, int]]:
    """Return the root candidate moves, preferring safe moves when possible."""
    safe_moves = _safe_candidate_moves(state, ai_player)
    candidate_moves = state.get_candidate_moves()

    if safe_moves != set():
        return [move for move in candidate_moves if move in safe_moves]

    return candidate_moves


def ordered_moves(
        state: game_class.GomokuState,
        graph: game_class.BoardGraph,
        ai_player: str,
        maximizing: bool,
        candidate_moves: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Return candidate moves in a useful search order.

    When maximizing is True, better moves for the AI are searched earlier.
    When maximizing is False, moves that are better for the opponent are
    searched earlier, which usually improves alpha-beta pruning.

    Preconditions:
        - all(state.is_valid_move(move[0], move[1]) for move in candidate_moves)
    """
    current_player = state.next_player
    scored = []

    for move_pos in candidate_moves:
        temp = state.copy()
        temp.make_move(move_pos[0], move_pos[1])

        tactical = _tactical_move_bonus(temp, current_player, ai_player)
        value = evaluate_state(temp, ai_player)
        value += graph_local_bonus(state, graph, move_pos, current_player)
        value += tactical
        scored.append((value, move_pos))

    if maximizing:
        scored.sort(key=lambda pair: pair[0], reverse=True)
    else:
        scored.sort(key=lambda pair: pair[0])

    return [pos for _, pos in scored]


def evaluate_state(state: game_class.GomokuState, ai_player: str) -> int:
    """Return a heuristic evaluation of state from ai_player's perspective.

    Positive scores favor ai_player, and negative scores favor the opponent.

    >>> s = game_class.GomokuState(5)
    >>> evaluate_state(s, 'X')
    0
    >>> s._board[2][2] = 'X'
    >>> evaluate_state(s, 'X') > 0
    True
    """
    terminal = _terminal_score(state, ai_player, 0)
    if terminal is not None:
        return terminal

    score = 0

    for line in _all_lines(state):
        score += _score_line_windows(line, ai_player)
        score += _score_line_with_open_ends(line, ai_player)

    score += _center_control_bonus(state, ai_player)
    return score


def graph_local_bonus(
        state: game_class.GomokuState,
        graph: game_class.BoardGraph,
        move_pos: tuple[int, int],
        player: str) -> int:
    """Return a small local bonus for move_pos using the board graph.

    Moves near friendly stones are rewarded slightly more than moves near enemy
    stones.

    Preconditions:
        - state.is_valid_move(move_pos[0], move_pos[1])
        - player in {'X', 'O'}

    >>> s = game_class.GomokuState(5)
    >>> g = game_class.BoardGraph(5)
    >>> s._board[2][2] = 'X'
    >>> graph_local_bonus(s, g, (2, 3), 'X') > 0
    True
    """
    bonus = 0

    for pos in graph.positions_within_distance(move_pos, 1):
        if pos == move_pos:
            continue

        cell = state.get_cell(pos[0], pos[1])
        if cell == player:
            bonus += NEAR_BONUS_FRIEND
        elif cell is not None:
            bonus += NEAR_BONUS_ENEMY

    return bonus


def score_window(window: list[Optional[str]], player: str) -> int:
    """Return a heuristic score for one length-5 window.

    Preconditions:
        - len(window) == 5
        - player in {'X', 'O'}

    >>> score_window(['X', 'X', 'X', 'X', 'X'], 'X') == WIN_SCORE
    True
    >>> score_window(['X', 'X', 'X', 'X', None], 'X') == FOUR_SCORE
    True
    >>> score_window(['O', 'O', 'O', 'O', None], 'X') < 0
    True
    >>> score_window(['X', 'X', None, 'O', None], 'X')
    0
    """
    opponent = get_opponent(player)

    player_count = window.count(player)
    opponent_count = window.count(opponent)
    empty_count = window.count(None)

    if player_count > 0 and opponent_count > 0:
        return 0

    if player_count == 5:
        return WIN_SCORE
    if player_count == 4 and empty_count == 1:
        return FOUR_SCORE
    if player_count == 3 and empty_count == 2:
        return THREE_SCORE
    if player_count == 2 and empty_count == 3:
        return TWO_SCORE

    if opponent_count == 5:
        return -WIN_SCORE
    if opponent_count == 4 and empty_count == 1:
        return -(FOUR_SCORE + 20_000)
    if opponent_count == 3 and empty_count == 2:
        return -(THREE_SCORE + 1_000)
    if opponent_count == 2 and empty_count == 3:
        return -TWO_SCORE

    return 0


def _terminal_score(
        state: game_class.GomokuState, ai_player: str,
        depth: int) -> Optional[int]:
    """Return the terminal score of state, if state is terminal.

    Faster wins are slightly better, and slower losses are slightly better.
    """
    winner = state.get_winner()
    if winner == ai_player:
        return WIN_SCORE - depth
    if winner == get_opponent(ai_player):
        return -WIN_SCORE + depth
    if state.is_full():
        return 0
    return None


def _safe_candidate_moves(
        state: game_class.GomokuState,
        ai_player: str) -> set[tuple[int, int]]:
    """Return candidate moves that avoid an immediate opponent win next turn.

    If every move still allows an immediate opponent win, this may return an
    empty set.
    """
    opponent = get_opponent(ai_player)
    safe_moves = set()

    for move_pos in state.get_candidate_moves():
        temp = state.copy()
        success = temp.make_move(move_pos[0], move_pos[1])
        if not success:
            continue

        if _find_immediate_win(temp, opponent) is None:
            safe_moves.add(move_pos)

    return safe_moves


def _find_immediate_win(
        state: game_class.GomokuState,
        player: str) -> Optional[tuple[int, int]]:
    """Return one immediate winning move for player, if one exists.

    Preconditions:
        - state.next_player == player
    """
    for move_pos in state.get_candidate_moves():
        if _is_immediate_winning_move(state, move_pos, player):
            return move_pos
    return None


def _is_immediate_winning_move(
        state: game_class.GomokuState,
        move_pos: tuple[int, int],
        player: str) -> bool:
    """Return whether move_pos is an immediate winning move for player.

    Preconditions:
        - state.next_player == player
    """
    temp = state.copy()
    success = temp.make_move(move_pos[0], move_pos[1])
    return success and temp.get_winner() == player


def _tactical_move_bonus(
        temp_state: game_class.GomokuState,
        mover: str,
        ai_player: str) -> int:
    """Return a tactical move bonus for a just-played move."""
    if temp_state.get_winner() == mover:
        if mover == ai_player:
            return WIN_SCORE // 2
        return -(WIN_SCORE // 2)
    return 0


def _all_lines(
        state: game_class.GomokuState) -> list[list[Optional[str]]]:
    """Return all rows, columns, and diagonals of length at least 5."""
    return (
        _row_lines(state)
        + _column_lines(state)
        + _diag_down_right_lines(state)
        + _diag_down_left_lines(state)
    )


def _row_lines(
        state: game_class.GomokuState) -> list[list[Optional[str]]]:
    """Return all row lines."""
    lines = []
    size = state.get_size()

    for row in range(size):
        lines.append([state.get_cell(row, col) for col in range(size)])

    return lines


def _column_lines(
        state: game_class.GomokuState) -> list[list[Optional[str]]]:
    """Return all column lines."""
    lines = []
    size = state.get_size()

    for col in range(size):
        lines.append([state.get_cell(row, col) for row in range(size)])

    return lines


def _diag_down_right_lines(
        state: game_class.GomokuState) -> list[list[Optional[str]]]:
    """Return diagonals in the down-right direction with length >= 5."""
    size = state.get_size()
    lines = []

    for start_col in range(size):
        line = []
        row = 0
        col = start_col
        while row < size and col < size:
            line.append(state.get_cell(row, col))
            row += 1
            col += 1

        if len(line) >= 5:
            lines.append(line)

    for start_row in range(1, size):
        line = []
        row = start_row
        col = 0
        while row < size and col < size:
            line.append(state.get_cell(row, col))
            row += 1
            col += 1

        if len(line) >= 5:
            lines.append(line)

    return lines


def _diag_down_left_lines(
        state: game_class.GomokuState) -> list[list[Optional[str]]]:
    """Return diagonals in the down-left direction with length >= 5."""
    size = state.get_size()
    lines = []

    for start_col in range(size):
        line = []
        row = 0
        col = start_col
        while row < size and col >= 0:
            line.append(state.get_cell(row, col))
            row += 1
            col -= 1

        if len(line) >= 5:
            lines.append(line)

    for start_row in range(1, size):
        line = []
        row = start_row
        col = size - 1
        while row < size and col >= 0:
            line.append(state.get_cell(row, col))
            row += 1
            col -= 1

        if len(line) >= 5:
            lines.append(line)

    return lines


def _score_line_windows(line: list[Optional[str]], player: str) -> int:
    """Return the total window-based score for one line.

    >>> _score_line_windows(['X', 'X', 'X', 'X', None], 'X') == FOUR_SCORE
    True
    """
    total = 0

    for i in range(len(line) - 4):
        window = line[i:i + 5]
        total += score_window(window, player)

    return total


def _score_line_with_open_ends(line: list[Optional[str]], player: str) -> int:
    """Return the open-ended run score for one line.

    >>> _score_line_with_open_ends([None, 'X', 'X', 'X', None], 'X') > THREE_SCORE
    True
    """
    opponent = get_opponent(player)
    score = 0
    i = 0

    while i < len(line):
        cell = line[i]
        if cell is None:
            i += 1
            continue

        j = _find_run_end(line, i)
        run_len = j - i

        left_open = i - 1 >= 0 and line[i - 1] is None
        right_open = j < len(line) and line[j] is None
        open_ends = (1 if left_open else 0) + (1 if right_open else 0)

        score += _signed_run_score(cell, player, opponent, run_len, open_ends)
        i = j

    return score


def _find_run_end(line: list[Optional[str]], start: int) -> int:
    """Return the first index after the run starting at start.

    Preconditions:
        - 0 <= start < len(line)
        - line[start] is not None

    >>> _find_run_end(['X', 'X', None], 0)
    2
    >>> _find_run_end(['O', None, None], 0)
    1
    """
    end = start
    while end < len(line) and line[end] == line[start]:
        end += 1
    return end


def _signed_run_score(
        cell: Optional[str], player: str, opponent: str,
        run_len: int, open_ends: int) -> int:
    """Return the signed score contributed by one run."""
    if cell is None or run_len < 2:
        return 0

    base = _run_base_score(run_len, open_ends)
    if cell == player:
        return base
    if cell == opponent:
        return -base
    return 0


def _run_base_score(run_len: int, open_ends: int) -> int:
    """Return the base score for a run length and number of open ends.

    >>> _run_base_score(4, 2) > FOUR_SCORE
    True
    >>> _run_base_score(3, 2) > THREE_SCORE
    True
    """
    if run_len >= 5:
        return WIN_SCORE

    if run_len == 4:
        score = FOUR_SCORE
        if open_ends == 2:
            score += OPEN_FOUR_BONUS
        return score

    if run_len == 3:
        score = THREE_SCORE
        if open_ends == 2:
            score += OPEN_THREE_BONUS
        return score

    if run_len == 2:
        score = TWO_SCORE
        if open_ends == 2:
            score += OPEN_TWO_BONUS
        return score

    return 0


def _center_control_bonus(
        state: game_class.GomokuState, ai_player: str) -> int:
    """Return a small center-control bonus.

    >>> s = game_class.GomokuState(5)
    >>> s._board[2][2] = 'X'
    >>> _center_control_bonus(s, 'X') > 0
    True
    """
    size = state.get_size()
    centre = size // 2
    score = 0

    for row in range(size):
        for col in range(size):
            cell = state.get_cell(row, col)
            if cell is None:
                continue

            distance = abs(row - centre) + abs(col - centre)
            bonus = max(0, CENTER_BONUS - distance)

            if cell == ai_player:
                score += bonus
            else:
                score -= bonus

    return score


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['dataclasses', 'typing', 'game_class'],
        'allowed-io': [],
        'max-line-length': 100
    })
