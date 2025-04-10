import pygame
import numpy as np
import random
from sys import exit

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Snakes & Ladders")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)

# Game constants
BOARD_SIZE = 10
CELL_SIZE = 60
GRID_OFFSET = 100
PLAYER_SIZE = 20

# Game state
player1_pos = 0  # Start at 0 (bottom left)
player2_pos = 0
current_player = 1  # Player 1 starts
game_over = False
winner = None

# Create snakes and ladders (random positions)
snakes = {}
ladders = {}
for _ in range(5):  # 5 snakes
    start = random.randint(1, 98)
    end = random.randint(1, start-1)
    snakes[start] = end

for _ in range(5):  # 5 ladders
    start = random.randint(1, 98)
    end = random.randint(start+1, 99)
    ladders[start] = end

# Font for text
font = pygame.font.SysFont(None, 36)

def draw_board():
    screen.fill(WHITE)
    
    # Draw grid
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            x = col * CELL_SIZE + GRID_OFFSET
            y = (BOARD_SIZE - 1 - row) * CELL_SIZE + GRID_OFFSET
            pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 1)
            
            # Draw cell number
            cell_num = row * BOARD_SIZE + col + 1
            text = font.render(str(cell_num), True, BLACK)
            text_rect = text.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2))
            screen.blit(text, text_rect)
            
            # Draw snakes and ladders
            if cell_num in snakes:
                pygame.draw.circle(screen, RED, (x + CELL_SIZE//2, y + CELL_SIZE//2), 5)
            elif cell_num in ladders:
                pygame.draw.circle(screen, GREEN, (x + CELL_SIZE//2, y + CELL_SIZE//2), 5)

def get_cell_position(pos):
    row = (pos - 1) // BOARD_SIZE
    col = (pos - 1) % BOARD_SIZE
    x = col * CELL_SIZE + GRID_OFFSET + CELL_SIZE//2
    y = (BOARD_SIZE - 1 - row) * CELL_SIZE + GRID_OFFSET + CELL_SIZE//2
    return x, y

def draw_players():
    # Draw player 1
    x1, y1 = get_cell_position(player1_pos + 1)
    pygame.draw.circle(screen, RED, (x1 - 10, y1), PLAYER_SIZE)
    
    # Draw player 2
    x2, y2 = get_cell_position(player2_pos + 1)
    pygame.draw.circle(screen, BLUE, (x2 + 10, y2), PLAYER_SIZE)

def roll_dice():
    return random.randint(1, 6)

def move_player(player_pos, steps):
    new_pos = player_pos + steps
    
    # Check if player landed on a snake
    if new_pos in snakes:
        new_pos = snakes[new_pos]
    
    # Check if player landed on a ladder
    if new_pos in ladders:
        new_pos = ladders[new_pos]
    
    # Ensure player doesn't go beyond the board
    if new_pos > 99:
        new_pos = 99
        
    return new_pos

def draw_game_info():
    # Draw current player
    player_text = font.render(f"Current Player: {current_player}", True, BLACK)
    screen.blit(player_text, (20, 20))
    
    # Draw game over message
    if game_over:
        winner_text = font.render(f"Player {winner} wins!", True, BLACK)
        screen.blit(winner_text, (20, 60))

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if event.type == pygame.KEYDOWN and not game_over:
            if event.key == pygame.K_SPACE:
                # Roll dice and move current player
                dice_roll = roll_dice()
                if current_player == 1:
                    player1_pos = move_player(player1_pos, dice_roll)
                    if player1_pos == 99:
                        game_over = True
                        winner = 1
                else:
                    player2_pos = move_player(player2_pos, dice_roll)
                    if player2_pos == 99:
                        game_over = True
                        winner = 2
                
                # Switch players
                current_player = 3 - current_player  # Toggle between 1 and 2
    
    # Draw everything
    draw_board()
    draw_players()
    draw_game_info()
    
    pygame.display.update()
    clock.tick(60)