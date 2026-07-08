# CSC111 Project: Gomoku Game

This is a Gomoku game project developed for CSC111. The program allows a human player to play Gomoku against a computer opponent through a simple graphical interface.

The project focuses on implementing the rules of Gomoku, managing the game board, detecting winning conditions, and designing a basic computer player that can choose moves based on the current board state.

## Project Overview

Gomoku is a two-player board game where players take turns placing pieces on a grid. The goal is to place five pieces in a row horizontally, vertically, or diagonally.

In this project, the user plays against the computer. The program keeps track of the board, checks whether either player has won, and updates the interface after each move.

## Features

- Graphical Gomoku board
- Human vs computer gameplay
- Turn-based game logic
- Win-condition detection
- Basic computer move selection
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

Contains the main game logic, including board representation, move handling, and win-condition checking.

### gomoku_ui.py

Contains the user interface code for displaying the Gomoku board and handling player interaction.

### data_computation.py

Contains helper functions used for move evaluation and game-related computation.

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

This project was completed as part of CSC111. The main goal was to practice Python programming, object-oriented design, algorithmic thinking, and building a complete interactive program.

## Author

Kai Zang