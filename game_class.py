"""CSC111 Project 2: Gomoku core data types.

Description
===========
This module contains the core data types for our Gomoku project:
- Move: an immutable data object representing one move
- GomokuState: the board state and game logic
- GameTree: an explicit game tree used for AI search
- Vertex and BoardGraph: a graph representation of board-position adjacency

This module is responsible for representing the problem domain in a way that
supports both tree-based search and graph-based local board analysis.

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
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Move:
    """A move in Gomoku.

    Instance Attributes:
        - row: row index of the move
        - col: column index of the move
        - player: the player placing the stone

    Representation Invariants:
        - self.player in {'X', 'O'}
        - self.row >= 0
        - self.col >= 0
    """
    row: int
    col: int
    player: str


class GomokuState:
    """A Gomoku game state.

    This class stores the board, the next player to move, and the most recent
    move.

    Private Instance Attributes:
        - _board:
            A square grid whose entries are None, 'X', or 'O'
        - _next_player:
            The player whose turn is next
        - _last_move:
            The most recent move, or None if no move has been played yet

    Representation Invariants:
        - len(self._board) >= 5
        - all(len(row) == len(self._board) for row in self._board)
        - self._next_player in {'X', 'O'}
        - all(cell in {None, 'X', 'O'} for row in self._board for cell in row)
    """
    _board: list[list[Optional[str]]]
    _next_player: str
    _last_move: Optional[Move]

    def __init__(self, size: int = 10) -> None:
        """Initialize an empty Gomoku board of the given size.

        Preconditions:
            - size >= 5

        >>> s = GomokuState(10)
        >>> s.get_size()
        10
        >>> s.get_cell(0, 0) is None
        True
        >>> s.next_player
        'X'
        """
        self._board = [[None for _ in range(size)] for _ in range(size)]
        self._next_player = 'X'
        self._last_move = None

    @property
    def next_player(self) -> str:
        """Return the player whose turn is next."""
        return self._next_player

    @property
    def last_move(self) -> Optional[Move]:
        """Return the last move played, if any."""
        return self._last_move

    def get_size(self) -> int:
        """Return the side length of the board."""
        return len(self._board)

    def get_cell(self, row: int, col: int) -> Optional[str]:
        """Return the board entry at (row, col).

        Preconditions:
            - 0 <= row < self.get_size()
            - 0 <= col < self.get_size()
        """
        return self._board[row][col]

    def is_valid_move(self, row: int, col: int) -> bool:
        """Return whether placing a stone at (row, col) is valid.

        >>> s = GomokuState(5)
        >>> s.is_valid_move(2, 2)
        True
        >>> _ = s.make_move(2, 2)
        >>> s.is_valid_move(2, 2)
        False
        """
        return (
            0 <= row < self.get_size()
            and 0 <= col < self.get_size()
            and self._board[row][col] is None
        )

    def make_move(self, row: int, col: int) -> bool:
        """Place a stone for the current player at (row, col).

        Return whether the move was successfully made.

        >>> s = GomokuState(5)
        >>> s.make_move(2, 2)
        True
        >>> s.get_cell(2, 2)
        'X'
        >>> s.next_player
        'O'
        >>> s.make_move(2, 2)
        False
        """
        if not self.is_valid_move(row, col):
            return False

        player = self._next_player
        self._board[row][col] = player
        self._last_move = Move(row, col, player)
        self._next_player = 'O' if player == 'X' else 'X'
        return True

    def copy(self) -> GomokuState:
        """Return a deep copy of this state.

        >>> s1 = GomokuState(5)
        >>> _ = s1.make_move(0, 0)
        >>> s2 = s1.copy()
        >>> s2.get_cell(0, 0)
        'X'
        >>> s1 is s2
        False
        >>> s1._board is s2._board
        False
        """
        new_state = GomokuState(self.get_size())
        new_state._board = [row[:] for row in self._board]
        new_state._next_player = self._next_player
        new_state._last_move = self._last_move
        return new_state

    def get_valid_moves(self) -> list[tuple[int, int]]:
        """Return all valid moves.

        >>> s = GomokuState(5)
        >>> len(s.get_valid_moves())
        25
        >>> _ = s.make_move(0, 0)
        >>> (0, 0) in s.get_valid_moves()
        False
        """
        moves = []
        for row in range(self.get_size()):
            for col in range(self.get_size()):
                if self._board[row][col] is None:
                    moves.append((row, col))
        return moves

    def get_occupied_positions(self) -> list[tuple[int, int]]:
        """Return all occupied board positions.

        >>> s = GomokuState(5)
        >>> _ = s.make_move(0, 0)
        >>> _ = s.make_move(1, 1)
        >>> sorted(s.get_occupied_positions())
        [(0, 0), (1, 1)]
        """
        positions = []
        for row in range(self.get_size()):
            for col in range(self.get_size()):
                if self._board[row][col] is not None:
                    positions.append((row, col))
        return positions

    def get_empty_positions_near(
            self, row: int, col: int, radius: int) -> set[tuple[int, int]]:
        """Return empty positions within the given square radius of (row, col).

        Preconditions:
            - radius >= 1

        >>> s = GomokuState(5)
        >>> _ = s.make_move(2, 2)
        >>> result = s.get_empty_positions_near(2, 2, 1)
        >>> (2, 2) in result
        False
        >>> (1, 1) in result and (3, 3) in result
        True
        """
        result = set()

        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                new_row = row + dr
                new_col = col + dc
                if self.is_valid_move(new_row, new_col):
                    result.add((new_row, new_col))

        return result

    def get_candidate_moves(self, radius: int = 2) -> list[tuple[int, int]]:
        """Return a reduced set of candidate moves near existing stones.

        If the board is empty, return the center position only.

        Preconditions:
            - radius >= 1

        >>> s = GomokuState(5)
        >>> s.get_candidate_moves()
        [(2, 2)]
        >>> _ = s.make_move(2, 2)
        >>> (2, 2) in s.get_candidate_moves()
        False
        """
        occupied = self.get_occupied_positions()

        if occupied == []:
            centre = self.get_size() // 2
            return [(centre, centre)]

        candidates = set()
        for row, col in occupied:
            candidates.update(self.get_empty_positions_near(row, col, radius))

        return sorted(candidates)

    def is_full(self) -> bool:
        """Return whether the board is full.

        >>> s = GomokuState(5)
        >>> s.is_full()
        False
        """
        return all(cell is not None for row in self._board for cell in row)

    def has_five_from(
            self, start: tuple[int, int], direction: tuple[int, int],
            player: str) -> bool:
        """Return whether there are five consecutive <player> stones.

        The check starts at <start> and continues in <direction>.

        Preconditions:
            - self._board[start[0]][start[1]] == player

        >>> s = GomokuState(5)
        >>> for i in range(5):
        ...     s._board[0][i] = 'X'
        >>> s.has_five_from((0, 0), (0, 1), 'X')
        True
        """
        row, col = start
        dr, dc = direction
        size = self.get_size()

        for k in range(5):
            new_row = row + dr * k
            new_col = col + dc * k
            if not (0 <= new_row < size and 0 <= new_col < size):
                return False
            if self._board[new_row][new_col] != player:
                return False

        return True

    def get_winner_at_position(self, row: int, col: int) -> Optional[str]:
        """Return the winner starting at (row, col), if any.

        Preconditions:
            - 0 <= row < self.get_size()
            - 0 <= col < self.get_size()
        """
        player = self._board[row][col]
        if player is None:
            return None

        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for direction in directions:
            if self.has_five_from((row, col), direction, player):
                return player

        return None

    def get_winner_from_last_move(self) -> Optional[str]:
        """Return the winner by checking only around the last move.

        Return None if no winner exists or if there is no last move.
        """
        if self._last_move is None:
            return None

        start = (self._last_move.row, self._last_move.col)
        player = self._last_move.player

        for direction in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            reverse = (-direction[0], -direction[1])
            count = 1
            count += self._count_direction(start, direction, player)
            count += self._count_direction(start, reverse, player)

            if count >= 5:
                return player

        return None

    def get_winner(self) -> Optional[str]:
        """Return the winner, if one exists.

        >>> s = GomokuState(10)
        >>> for i in range(5):
        ...     s._board[0][i] = 'X'
        >>> s.get_winner()
        'X'
        """
        winner = self.get_winner_from_last_move()
        if winner is not None:
            return winner

        size = self.get_size()
        for row in range(size):
            for col in range(size):
                winner = self.get_winner_at_position(row, col)
                if winner is not None:
                    return winner

        return None

    def get_winning_positions(self) -> list[tuple[int, int]]:
        """Return one winning line of 5 positions, or [] if there is none."""
        if self._last_move is not None:
            player = self._last_move.player
            start = (self._last_move.row, self._last_move.col)

            for direction in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                line = self._winning_line_through(start, direction, player)
                if line != []:
                    return line

        return self._scan_for_win()

    def _scan_for_win(self) -> list[tuple[int, int]]:
        """Return one winning line by scanning the whole board, or [] if none."""
        for start, player in self._occupied_starts():
            for direction in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                positions = self._five_positions(start, direction, player)
                if positions != []:
                    return positions

        return []

    def _occupied_starts(self) -> list[tuple[tuple[int, int], str]]:
        """Return all occupied positions together with their player symbols."""
        starts = []
        size = self.get_size()

        for row in range(size):
            for col in range(size):
                cell = self._board[row][col]
                if cell is not None:
                    starts.append(((row, col), cell))

        return starts

    def _five_positions(
            self, start: tuple[int, int], direction: tuple[int, int],
            player: str) -> list[tuple[int, int]]:
        """Return the 5 positions from start in direction if they form a win."""
        positions = []
        row, col = start
        dr, dc = direction
        size = self.get_size()

        for k in range(5):
            new_row = row + dr * k
            new_col = col + dc * k

            if not (0 <= new_row < size and 0 <= new_col < size):
                return []

            if self._board[new_row][new_col] != player:
                return []

            positions.append((new_row, new_col))

        return positions

    def _winning_line_through(
            self, start: tuple[int, int], direction: tuple[int, int],
            player: str) -> list[tuple[int, int]]:
        """Return a winning line through start in the given direction."""
        row, col = start
        dr, dc = direction
        line = [start]

        curr_row = row - dr
        curr_col = col - dc
        while self._is_player_stone((curr_row, curr_col), player):
            line.insert(0, (curr_row, curr_col))
            curr_row -= dr
            curr_col -= dc

        curr_row = row + dr
        curr_col = col + dc
        while self._is_player_stone((curr_row, curr_col), player):
            line.append((curr_row, curr_col))
            curr_row += dr
            curr_col += dc

        if len(line) >= 5:
            return line[:5]
        return []

    def _count_direction(
            self, start: tuple[int, int], direction: tuple[int, int],
            player: str) -> int:
        """Return how many consecutive player stones appear from start."""
        count = 0
        row, col = start
        dr, dc = direction
        curr_row = row + dr
        curr_col = col + dc

        while self._is_player_stone((curr_row, curr_col), player):
            count += 1
            curr_row += dr
            curr_col += dc

        return count

    def _is_player_stone(self, pos: tuple[int, int], player: str) -> bool:
        """Return whether pos is on the board and contains player."""
        row, col = pos
        return (
            0 <= row < self.get_size()
            and 0 <= col < self.get_size()
            and self._board[row][col] == player
        )

    def is_terminal(self) -> bool:
        """Return whether this state is terminal.

        A state is terminal if some player has won or the board is full.

        >>> s = GomokuState(5)
        >>> s.is_terminal()
        False
        """
        return self.get_winner() is not None or self.is_full()

    def to_key(self) -> tuple[tuple[Optional[str], ...], ...]:
        """Return a hashable representation of the board.

        >>> s = GomokuState(5)
        >>> isinstance(s.to_key(), tuple)
        True
        """
        return tuple(tuple(row) for row in self._board)

    def __str__(self) -> str:
        """Return a simple text representation of this board."""
        symbols = {None: '.', 'X': 'X', 'O': 'O'}
        return '\n'.join(
            ' '.join(symbols[cell] for cell in row)
            for row in self._board
        )


class GameTree:
    """A game tree node for Gomoku AI search.

    Private Instance Attributes:
        - _state: the game state at this node
        - _move: the move used to arrive at this state from the parent
        - _subtrees: the child game trees
        - _score: a cached score assigned during alpha-beta search

    Representation Invariants:
        - all(subtree._move is not None for subtree in self._subtrees)
    """
    _state: GomokuState
    _move: Optional[Move]
    _subtrees: list[GameTree]
    _score: Optional[int]

    def __init__(self, state: GomokuState, move: Optional[Move] = None) -> None:
        """Initialize a new game tree node."""
        self._state = state
        self._move = move
        self._subtrees = []
        self._score = None

    @property
    def state(self) -> GomokuState:
        """Return the state stored at this node."""
        return self._state

    @property
    def move(self) -> Optional[Move]:
        """Return the move that led to this node."""
        return self._move

    @property
    def subtrees(self) -> list[GameTree]:
        """Return the child subtrees."""
        return self._subtrees

    @property
    def score(self) -> Optional[int]:
        """Return the cached score of this node, if one exists."""
        return self._score

    @score.setter
    def score(self, value: int) -> None:
        """Set the cached score of this node."""
        self._score = value

    def is_leaf(self) -> bool:
        """Return whether this node has no children.

        >>> tree = GameTree(GomokuState(5))
        >>> tree.is_leaf()
        True
        """
        return self._subtrees == []

    def add_subtree(self, subtree: GameTree) -> None:
        """Add subtree as a child of this node."""
        self._subtrees.append(subtree)

    def clear_subtrees(self) -> None:
        """Remove all child subtrees."""
        self._subtrees = []

    def get_moves_at_root(self) -> list[Move]:
        """Return the moves available from this node.

        >>> tree = GameTree(GomokuState(5))
        >>> tree.get_moves_at_root()
        []
        """
        moves = []
        for subtree in self._subtrees:
            if subtree._move is not None:
                moves.append(subtree._move)
        return moves

    def size(self) -> int:
        """Return the number of nodes in this tree.

        >>> root = GameTree(GomokuState(5))
        >>> root.size()
        1
        """
        return 1 + sum(subtree.size() for subtree in self._subtrees)


class Vertex:
    """A vertex in the board graph.

    Instance Attributes:
        - item: a board position (row, col)
        - neighbours: adjacent board-position vertices

    Representation Invariants:
        - self.item[0] >= 0
        - self.item[1] >= 0
    """
    item: tuple[int, int]
    neighbours: set[Vertex]

    def __init__(self, item: tuple[int, int]) -> None:
        """Initialize a new vertex."""
        self.item = item
        self.neighbours = set()


class BoardGraph:
    """An undirected graph representing board-position adjacency.

    Each board position is a vertex, and edges connect neighboring positions,
    including diagonal neighbors. This graph is used for local neighborhood
    analysis around moves.

    Private Instance Attributes:
        - _vertices: maps board positions to vertices
        - _size: the side length of the board

    Representation Invariants:
        - self._size >= 5
        - len(self._vertices) == self._size ** 2
    """
    _vertices: dict[tuple[int, int], Vertex]
    _size: int

    def __init__(self, size: int) -> None:
        """Initialize a board graph for a size x size board.

        Preconditions:
            - size >= 5

        >>> g = BoardGraph(5)
        >>> len(g._vertices)
        25
        """
        self._vertices = {}
        self._size = size
        self.build_grid_graph()

    def get_direction_offsets(self) -> list[tuple[int, int]]:
        """Return the 8 adjacency directions.

        >>> g = BoardGraph(5)
        >>> len(g.get_direction_offsets())
        8
        """
        return [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

    def add_edge(self, u: tuple[int, int], v: tuple[int, int]) -> None:
        """Add an undirected edge between u and v.

        Preconditions:
            - u in self._vertices
            - v in self._vertices
            - u != v
        """
        vertex_u = self._vertices[u]
        vertex_v = self._vertices[v]
        vertex_u.neighbours.add(vertex_v)
        vertex_v.neighbours.add(vertex_u)

    def connect_position_neighbours(self, row: int, col: int) -> None:
        """Connect (row, col) to all valid neighboring positions."""
        for dr, dc in self.get_direction_offsets():
            new_row = row + dr
            new_col = col + dc
            if 0 <= new_row < self._size and 0 <= new_col < self._size:
                self.add_edge((row, col), (new_row, new_col))

    def build_grid_graph(self) -> None:
        """Build the full board adjacency graph."""
        for row in range(self._size):
            for col in range(self._size):
                self._vertices[(row, col)] = Vertex((row, col))

        for row in range(self._size):
            for col in range(self._size):
                self.connect_position_neighbours(row, col)

    def get_neighbours(self, pos: tuple[int, int]) -> set[tuple[int, int]]:
        """Return the neighboring board positions of pos.

        Preconditions:
            - pos in self._vertices

        >>> g = BoardGraph(5)
        >>> sorted(g.get_neighbours((0, 0)))
        [(0, 1), (1, 0), (1, 1)]
        """
        neighbours = set()
        for vertex in self._vertices[pos].neighbours:
            neighbours.add(vertex.item)
        return neighbours

    def get_next_frontier(
            self, frontier: set[tuple[int, int]],
            visited: set[tuple[int, int]]) -> set[tuple[int, int]]:
        """Return the next BFS frontier.

        Preconditions:
            - frontier.issubset(set(self._vertices))
            - visited.issubset(set(self._vertices))
        """
        new_frontier = set()

        for pos in frontier:
            for neighbour in self.get_neighbours(pos):
                if neighbour not in visited:
                    visited.add(neighbour)
                    new_frontier.add(neighbour)

        return new_frontier

    def positions_within_distance(
            self, start: tuple[int, int], dist: int) -> set[tuple[int, int]]:
        """Return all positions within graph distance <= dist from start.

        This method uses BFS.

        Preconditions:
            - start in self._vertices
            - dist >= 0

        >>> g = BoardGraph(5)
        >>> g.positions_within_distance((2, 2), 0)
        {(2, 2)}
        >>> len(g.positions_within_distance((2, 2), 1))
        9
        """
        if dist == 0:
            return {start}

        visited = {start}
        frontier = {start}

        for _ in range(dist):
            frontier = self.get_next_frontier(frontier, visited)
            if frontier == set():
                break

        return visited


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['dataclasses', 'typing'],
        'allowed-io': [],
        'max-line-length': 100
    })


