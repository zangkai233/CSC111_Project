"""CSC111 Project 2: Gomoku user interface.

Description
===========
This module contains a simple Pygame user interface for our Gomoku project.
It supports a human player competing against the AI on a graphical board.

The UI is responsible only for:
- drawing the board and stones
- handling mouse and keyboard input
- coordinating turns between the human and the AI

All game logic and AI computation are handled in other modules.

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

import pygame

from game_class import GomokuState, BoardGraph
from data_computation import choose_best_move


BOARD_COLOR = (235, 190, 120)
GRID_COLOR = (40, 40, 40)
TEXT_COLOR = (20, 20, 20)
PANEL_COLOR = (230, 230, 230)
BLACK_STONE = (20, 20, 20)
WHITE_STONE = (245, 245, 245)
LAST_MOVE_COLOR = (210, 40, 40)
WIN_LINE_COLOR = (220, 30, 30)

STATUS_PANEL_HEIGHT = 60
FRAME_RATE = 30


@dataclass
class UISettings:
    """Visual settings for the Gomoku UI.

    Instance Attributes:
        - board_size: the side length of the board
        - cell_size: pixel distance between neighboring grid intersections
        - margin: pixel margin around the board

    Representation Invariants:
        - self.board_size >= 5
        - self.cell_size >= 20
        - self.margin >= 0
    """
    board_size: int = 10
    cell_size: int = 50
    margin: int = 40

    def board_pixel_size(self) -> int:
        """Return the width/height in pixels of the board area."""
        return self.margin * 2 + self.cell_size * (self.board_size - 1)

    def window_size(self) -> tuple[int, int]:
        """Return the full window size."""
        width = self.board_pixel_size()
        height = self.board_pixel_size() + STATUS_PANEL_HEIGHT
        return width, height


class GomokuUI:
    """A simple Pygame UI for human-vs-AI Gomoku.

    Private Instance Attributes:
        - _settings: visual layout settings
        - _state: the current game state
        - _graph: the board graph
        - _screen: the Pygame display surface
        - _font: font used for status text
        - _big_font: larger font used for game-over text
        - _clock: frame-rate controller

    Representation Invariants:
        - self._state.get_size() == self._settings.board_size
    """
    _settings: UISettings
    _state: GomokuState
    _graph: BoardGraph
    _screen: pygame.Surface
    _font: pygame.font.Font
    _big_font: pygame.font.Font
    _clock: pygame.time.Clock

    def __init__(self, board_size: int = 10, cell_size: int = 50) -> None:
        """Initialize the UI and game state.

        Preconditions:
            - board_size >= 5
            - cell_size >= 20
        """
        self._settings = UISettings(board_size, cell_size, 40)
        self._state = GomokuState(board_size)
        self._graph = BoardGraph(board_size)

        pygame.init()
        self._screen = pygame.display.set_mode(self._settings.window_size())
        pygame.display.set_caption('Gomoku AI (CSC111 Project 2)')
        self._font = pygame.font.SysFont(None, 28)
        self._big_font = pygame.font.SysFont(None, 34)
        self._clock = pygame.time.Clock()

    def run(self) -> None:
        """Run the main UI loop."""
        running = True

        while running:
            running = self._handle_events()

            if not self._is_game_over() and self._state.next_player == 'O':
                self._handle_ai_turn()

            self._draw_frame()
            pygame.display.flip()
            self._clock.tick(FRAME_RATE)

        pygame.quit()

    def _handle_events(self) -> bool:
        """Process one frame of events.

        Return whether the UI should keep running.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if not self._handle_keydown(event.key):
                    return False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_human_click(event.pos)

        return True

    def _handle_keydown(self, key: int) -> bool:
        """Handle keyboard input.

        Press Q to quit and R to restart.

        Return whether the UI should keep running.
        """
        if key == pygame.K_q:
            return False
        if key == pygame.K_r:
            self._restart()
        return True

    def _handle_human_click(self, pixel_pos: tuple[int, int]) -> None:
        """Handle a human move from a mouse click."""
        if self._is_game_over():
            return
        if self._state.next_player != 'X':
            return

        board_pos = self._pixel_to_board(pixel_pos[0], pixel_pos[1])
        if board_pos is None:
            return

        row, col = board_pos
        self._state.make_move(row, col)

    def _handle_ai_turn(self) -> None:
        """Handle the AI turn."""
        ai_move = choose_best_move(self._state, self._graph, 'O', depth=2)
        if ai_move is not None:
            self._state.make_move(ai_move.row, ai_move.col)

    def _restart(self) -> None:
        """Restart the game with a fresh board."""
        self._state = GomokuState(self._settings.board_size)
        self._graph = BoardGraph(self._settings.board_size)

    def _is_game_over(self) -> bool:
        """Return whether the current game has ended."""
        return self._state.is_terminal()

    def _winner_text(self) -> str:
        """Return the status text shown when the game is over."""
        winner = self._state.get_winner()
        if winner is not None:
            return f'{winner} wins! (R: Restart, Q: Quit)'
        return 'Draw! (R: Restart, Q: Quit)'

    def _status_text(self) -> str:
        """Return the current status text."""
        if self._is_game_over():
            return self._winner_text()

        if self._state.next_player == 'X':
            return 'Your turn (X)    (R: Restart, Q: Quit)'
        return 'AI turn (O)    (R: Restart, Q: Quit)'

    def _draw_frame(self) -> None:
        """Draw one full frame."""
        self._draw_board()
        self._draw_stones()
        self._draw_last_move_highlight()
        self._draw_winning_line()
        self._draw_status_panel()

    def _draw_board(self) -> None:
        """Draw the board background and grid."""
        self._screen.fill(BOARD_COLOR)

        for i in range(self._settings.board_size):
            start_h = self._board_to_pixel(i, 0)
            end_h = self._board_to_pixel(i, self._settings.board_size - 1)
            pygame.draw.line(self._screen, GRID_COLOR, start_h, end_h, 2)

            start_v = self._board_to_pixel(0, i)
            end_v = self._board_to_pixel(self._settings.board_size - 1, i)
            pygame.draw.line(self._screen, GRID_COLOR, start_v, end_v, 2)

    def _draw_stones(self) -> None:
        """Draw all stones currently on the board."""
        radius = self._settings.cell_size // 3

        for row in range(self._settings.board_size):
            for col in range(self._settings.board_size):
                cell = self._state.get_cell(row, col)
                if cell is None:
                    continue

                x, y = self._board_to_pixel(row, col)
                if cell == 'X':
                    pygame.draw.circle(self._screen, BLACK_STONE, (x, y), radius)
                else:
                    pygame.draw.circle(self._screen, WHITE_STONE, (x, y), radius)
                    pygame.draw.circle(self._screen, BLACK_STONE, (x, y), radius, 2)

    def _draw_last_move_highlight(self) -> None:
        """Draw a small red marker on the most recent move."""
        if self._state.last_move is None:
            return

        x, y = self._board_to_pixel(
            self._state.last_move.row, self._state.last_move.col
        )
        pygame.draw.circle(self._screen, LAST_MOVE_COLOR, (x, y), 6)

    def _draw_winning_line(self) -> None:
        """Draw a red line through a winning sequence, if one exists."""
        positions = self._state.get_winning_positions()
        if positions == []:
            return

        start = self._board_to_pixel(positions[0][0], positions[0][1])
        end = self._board_to_pixel(positions[-1][0], positions[-1][1])
        pygame.draw.line(self._screen, WIN_LINE_COLOR, start, end, 5)

    def _draw_status_panel(self) -> None:
        """Draw the status panel at the bottom."""
        panel_y = self._settings.board_pixel_size()
        panel_width, _ = self._settings.window_size()

        pygame.draw.rect(
            self._screen,
            PANEL_COLOR,
            (0, panel_y, panel_width, STATUS_PANEL_HEIGHT)
        )

        message = self._status_text()
        if self._is_game_over():
            text = self._big_font.render(message, True, TEXT_COLOR)
        else:
            text = self._font.render(message, True, TEXT_COLOR)

        self._screen.blit(text, (15, panel_y + 18))

    def _board_to_pixel(self, row: int, col: int) -> tuple[int, int]:
        """Convert board coordinates to pixel coordinates."""
        x = self._settings.margin + col * self._settings.cell_size
        y = self._settings.margin + row * self._settings.cell_size
        return x, y

    def _pixel_to_board(self, x: int, y: int) -> Optional[tuple[int, int]]:
        """Convert pixel coordinates to the nearest board position, if close enough.

        Return None if the click is outside the playable board area.
        """
        if y > self._settings.board_pixel_size():
            return None

        best_pos = None
        best_dist_sq = 10**18

        for row in range(self._settings.board_size):
            for col in range(self._settings.board_size):
                px, py = self._board_to_pixel(row, col)
                dx = x - px
                dy = y - py
                dist_sq = dx * dx + dy * dy

                if dist_sq < best_dist_sq:
                    best_dist_sq = dist_sq
                    best_pos = (row, col)

        if best_pos is not None and best_dist_sq <= (self._settings.cell_size // 2) ** 2:
            return best_pos
        return None


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'extra-imports': [
            'dataclasses', 'typing', 'pygame', 'game_class', 'data_computation'
        ],
        'allowed-io': [],
        'max-line-length': 100,
        'disable': ['E1101']
    })
