"""CSC111 Project 2: Main entry point for Gomoku AI."""
from gomoku_ui import GomokuUI


def run() -> None:
    """Run the Gomoku game."""
    ui = GomokuUI(board_size=10, cell_size=50)
    ui.run()


if __name__ == '__main__':
    run()

    # import doctest
    # doctest.testmod(verbose=True)
    #
    # import python_ta
    # import python_ta.contracts
    #
    # python_ta.contracts.DEBUG_CONTRACTS = False
    # python_ta.contracts.check_all_contracts()
    #
    # python_ta.check_all(config={
    #     'extra-imports': ['dataclasses', 'typing', 'python_ta.contracts', 'gomoku_ui'],
    #     'allowed-io': [],
    #     'max-line-length': 100,
    #     'disable': []
    # })
