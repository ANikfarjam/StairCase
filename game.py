import pygame
import numpy as np
import random
# Define color dictionary
color_dic = {
    1: 'red', #wordle challenge
    2: 'blue', # trivia challenge
    3: 'green', # gain coins
    4: 'yellow', # wheel of fortune
    0: 'gray' # neutral
}

# Define RGB values for Pygame
color_rgb = {
    'red': (255, 0, 0),
    'blue': (0, 0, 255),
    'green': (0, 255, 0),
    'yellow': (255, 255, 0),
    'gray': (200, 200, 200)
}

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
cell_size = 60  # Size of each cell in the grid

# Create the board with the required distribution
def generate_board(board):
    total_cells = 100
    green_count = 40
    other_count = total_cells - green_count
    other_colors = [1, 2, 4, 0]  # Excluding green (3)

    # Distribute other colors evenly
    num_per_other = other_count // len(other_colors)
    color_list = [3] * green_count  # Green assigned first
    for color in other_colors:
        color_list.extend([color] * num_per_other)

    random.shuffle(color_list)  # Shuffle the board

    return np.array(color_list).reshape(10, 10)
def initialize(board, player1, player2, dice, challenges):
    pygame.draw.rect()
board = generate_board()
running = True
while running:
    #create board
    pass