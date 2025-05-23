import pygame
import numpy as np
import random
from sys import exit

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Snakes & Ladders")
clock = pygame.time.Clock()

# Graphics Assets
sky_background = pygame.image.load('graphics/blue-sky.png')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
LIGHT_YELLOW = (255, 255, 200)
ORANGE = (255, 200, 0)

# Game constants
BOARD_SIZE = 10
CELL_SIZE = 60
GRID_OFFSET = 100
PLAYER_SIZE = 15
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50

# Game state
player1_pos = 0  # Start at 0 (bottom left)
player2_pos = 0
current_player = 1  # Player 1 starts
game_over = False
winner = None
message = "Player 1's turn. Press the button to roll!"
message_timer = 0
message_duration = 120  # frames (2 seconds at 60 FPS)

# Create snakes and ladders (random positions)
snakes = {}
ladders = {}
for _ in range(5):  # 5 snakes
    start = random.randint(1, 98)
    end = random.randint(1, start-1)
    snakes[end] = start  # Note: reversed to match your requirement

for _ in range(5):  # 5 ladders
    start = random.randint(1, 98)
    end = random.randint(start+1, 99)
    ladders[start] = end

# Font for text
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

def draw_board():
    screen.fill(WHITE)
    screen.blit(sky_background, (0,0))
    
    # Draw grid
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            x = col * CELL_SIZE + GRID_OFFSET
            y = (BOARD_SIZE - 1 - row) * CELL_SIZE + GRID_OFFSET
            
            # Alternate colors like a chess board
            if (row + col) % 2 == 0:
                color = LIGHT_YELLOW
            else:
                color = ORANGE
            
            # Draw filled square
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))
            # Draw square border
            pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 1)
            
            # Draw cell number
            cell_num = row * BOARD_SIZE + col + 1
            text = font.render(str(cell_num), True, BLACK)
            text_rect = text.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2))
            screen.blit(text, text_rect)
            
            # Draw snakes and ladders
            if cell_num in snakes:
                pygame.draw.circle(screen, RED, (x + CELL_SIZE//2, y + CELL_SIZE//2), 5)
                # Draw "S" for snake
                s_text = small_font.render("S", True, RED)
                s_rect = s_text.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2 + 15))
                screen.blit(s_text, s_rect)
            elif cell_num in ladders:
                pygame.draw.circle(screen, GREEN, (x + CELL_SIZE//2, y + CELL_SIZE//2), 5)
                # Draw "L" for ladder
                l_text = small_font.render("L", True, GREEN)
                l_rect = l_text.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2 + 15))
                screen.blit(l_text, l_rect)

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
    
    # Check if player landed on a ladder
    if new_pos in ladders:
        old_pos = new_pos
        new_pos = ladders[new_pos]
        return new_pos, f"Player {current_player} climbed a ladder from {old_pos+1} to {new_pos+1}!"
    
    # Check if player landed on a snake
    if new_pos in snakes:
        old_pos = new_pos
        new_pos = snakes[new_pos]
        return new_pos, f"Player {current_player} was bitten by a snake and moved from {old_pos+1} to {new_pos+1}!"
    
    # Ensure player doesn't go beyond the board
    if new_pos > 99:
        new_pos = 99
        
    return new_pos, f"Player {current_player} moved {steps} steps to position {new_pos+1}"

def draw_button():
    button_rect = pygame.Rect(330, 720, BUTTON_WIDTH, BUTTON_HEIGHT)
    pygame.draw.rect(screen, YELLOW, button_rect)
    pygame.draw.rect(screen, BLACK, button_rect, 2)
    
    button_text = font.render("Roll Dice", True, BLACK)
    text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, text_rect)
    
    return button_rect

def draw_game_info():
    # Draw current player
    player_text = font.render(f"Current Player: {current_player}", True, BLACK)
    screen.blit(player_text, (20, 20))
    
    # Draw game over message
    if game_over:
        winner_text = font.render(f"Player {winner} wins!", True, BLACK)
        screen.blit(winner_text, (20, 50))
    
    # Draw message if active
    if message_timer > 0:
        message_text = font.render(message, True, BLACK)
        screen.blit(message_text, (20, 70))

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mouse_pos = pygame.mouse.get_pos()
            button_rect = draw_button()
            
            if button_rect.collidepoint(mouse_pos):
                # Roll dice and move current player
                dice_roll = roll_dice()
                if current_player == 1:
                    player1_pos, move_message = move_player(player1_pos, dice_roll)
                    if player1_pos == 99:
                        game_over = True
                        winner = 1
                        message = f"Player 1 wins the game!"
                else:
                    player2_pos, move_message = move_player(player2_pos, dice_roll)
                    if player2_pos == 99:
                        game_over = True
                        winner = 2
                        message = f"Player 2 wins the game!"
                
                # Update message and timer
                message = move_message
                message_timer = message_duration
                
                # Switch players
                current_player = 3 - current_player  # Toggle between 1 and 2
    
    # Update message timer
    if message_timer > 0:
        message_timer -= 1
    
    # Draw everything
    draw_board()
    draw_players()
    draw_game_info()
    button_rect = draw_button()
    
    pygame.display.update()
    clock.tick(60)

