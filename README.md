# CSC111 Project: Gomoku Game

This is a Gomoku game project developed for CSC111 at the University of Toronto. The program allows a human player to play Gomoku against a computer opponent through a graphical interface.

The project focuses on implementing the rules of Gomoku, managing the game board, detecting winning conditions, and designing a computer player that can make decisions based on the current board state.

## Project Overview

Gomoku is a two-player board game where players take turns placing pieces on a grid. The goal is to place five pieces in a row horizontally, vertically, or diagonally.

In this project, the user plays against a computer opponent. The program keeps track of the board, checks valid moves, detects wins, and updates the interface after each turn.

## Main Algorithm

The computer player uses a search-based decision-making algorithm combined with heuristic board evaluation.

The main AI logic includes:

- explicit game-tree expansion
- minimax search
- alpha-beta pruning
- heuristic evaluation of board positions
- move ordering to improve search efficiency
- immediate win detection
- safe move filtering
- graph-based local board bonuses

At each turn, the AI first checks whether it has an immediate winning move. If such a move exists, it plays that move directly.

If there is no immediate win, the AI generates candidate moves and builds a game tree from the current board state. It then applies minimax search with alpha-beta pruning to evaluate possible future positions. Alpha-beta pruning helps reduce the number of branches that need to be searched, making the decision process more efficient.

The evaluation function scores a board state from the AI player's perspective. Positive scores favor the AI, while negative scores favor the opponent. The scoring system considers patterns such as:

- five in a row
- four in a row
- three in a row
- two in a row
- open-ended sequences
- opponent threats
- center control
- nearby friendly and enemy stones

The AI also uses move ordering. Before searching deeper, candidate moves are scored using the heuristic function and local board information. Stronger moves are searched earlier, which improves the effectiveness of alpha-beta pruning.

A board graph is used to evaluate local relationships between positions. Moves near friendly stones receive a small bonus, while moves near enemy stones are also considered because they may be useful for blocking or creating pressure.

Overall, the AI combines tree-based search with local board heuristics to choose competitive moves.

## Features

- Graphical Gomoku board
- Human vs computer gameplay
- Turn-based game logic
- Valid move checking
- Win-condition detection
- AI move selection using minimax search
- Alpha-beta pruning for more efficient search
- Heuristic board evaluation
- Move ordering and local graph-based scoring
- Organized Python code split across multiple files
- Project report included

## File Structure

main.py
game_class.py
gomoku_ui.py
data_computation.py
project_report.pdf
project_report.tex
requirements.txt
README.md

## File Descriptions

### main.py

The main entry point of the program. Run this file to start the game.

### game_class.py

Contains the main game structures and logic, including the Gomoku game state, board representation, moves, board graph, and game tree.

### gomoku_ui.py

Contains the user interface code for displaying the Gomoku board and handling player interaction.

### data_computation.py

Contains the AI computation logic, including heuristic evaluation, move ordering, game-tree expansion, minimax search, alpha-beta pruning, and best-move selection.

### project_report.pdf

The final project report for the CSC111 project.

### project_report.tex

The LaTeX source file for the project report.

### requirements.txt

Lists the Python packages needed to run the project.

## How to Run

First, clone the repository:

git clone https://github.com/zangkai233/CSC111_Project.git

Then enter the project folder:

cd CSC111_Project

Install the required packages:

pip install -r requirements.txt

Run the game:

python main.py

Depending on your Python setup, you may need to use:

python3 main.py

## Requirements

This project is written in Python. Make sure Python is installed before running the program.

The required packages are listed in requirements.txt.

## Notes

This project was completed as part of CSC111. The main goal was to practice Python programming, object-oriented design, graph-based modeling, recursive search, heuristic evaluation, and building a complete interactive program.

## Authors (Uoft CS students)
Kai Zang  
Shiyuan Lyu  
Seoyun Ju  
Emily Ye