import pygame
import requests
from sys import exit
import time
import math

# Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (155, 229, 255)
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

# Constants
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

#SERVER_URL = "http://127.0.0.1:5000"
SERVER_URL="http://10.0.0.120:5001"
player_id = None

# Animation constants
ANIMATION_SPEED = 0.1  # Speed of animation (0.1 = 10% of the way each frame)
ANIMATION_PHASE_DURATION = 1  # Duration of each animation phase in seconds
BACKGROUND_SCROLL_SPEED = 1  # Pixels per frame to move the background

# Animation state
animating = False
current_anim_pos = [0, 0]
target_anim_pos = [0, 0]
current_player_animating = None
snake_ladder_animation = False
snake_ladder_end_pos = None
animation_phase = 1  # 1 for first phase, 2 for second phase

# Background state
background_x = 0
sky_background = pygame.image.load('graphics/blue-sky.png')

# Add these variables near the top with other game state variables
user_answer = ""
active_modal = None  # 'trivia', 'hangman', or None

screen = pygame.display.set_mode((800, 800))

def join_game():
    global player_id
    try:
        res = requests.post(f"{SERVER_URL}/join")
        print("Response status:", res.status_code)
        print("Response body:", res.text)
        res.raise_for_status()
        player_id = res.json()["player_id"]
        print("Joined as:", player_id)
    except Exception as e:
        print("join_game failed:", e)
        exit(1)

def roll_dice():
    global animating, current_anim_pos, target_anim_pos, current_player_animating, snake_ladder_animation, snake_ladder_end_pos
    
    res = requests.post(f"{SERVER_URL}/roll", json={"player_id": player_id})
    result = res.json()
    
    # Start animation
    animating = True
    current_player_animating = player_id
    animation_phase = 1
    
    # Get current and target positions
    current_pos = result.get("before_roll", 0)
    target_pos = result.get("new_position", 0)
    
    # Check if we landed on a snake or ladder
    snake_ladder_animation = result.get("snake_ladder", False)
    if snake_ladder_animation:
        snake_ladder_end_pos = result.get("snake_ladder_end", 0)
        # First phase: move to snake/ladder position
        current_anim_pos = list(get_cell_coords(current_pos))
        target_anim_pos = list(get_cell_coords(result.get("snake_ladder_start", 0)))
    else:
        # Normal movement
        current_anim_pos = list(get_cell_coords(current_pos + 1))
        target_anim_pos = list(get_cell_coords(target_pos + 1))
    
    return result

def get_state():
    return requests.get(f"{SERVER_URL}/state").json()

def get_cell_coords(pos):
    # Ensure pos is an integer
    pos = int(pos)
    row = 9 - (pos // 10)
    col = pos % 10 if (9 - row) % 2 == 0 else 9 - (pos % 10)
    return col * CELL_SIZE + GRID_OFFSET, row * CELL_SIZE + GRID_OFFSET

def draw_board(screen, state):
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

def draw_snakes_ladders(screen, state):
    for start, end in state["snakes"].items():
        start_x, start_y = get_cell_coords(start)
        end_x, end_y = get_cell_coords(end)
        pygame.draw.line(screen, RED, (start_x + CELL_SIZE//2, start_y + CELL_SIZE//2), 
                        (end_x + CELL_SIZE//2, end_y + CELL_SIZE//2), 3)
        pygame.draw.circle(screen, RED, (start_x + CELL_SIZE//2, start_y + CELL_SIZE//2), 5)
        pygame.draw.circle(screen, RED, (end_x + CELL_SIZE//2, end_y + CELL_SIZE//2), 5)
        
    for start, end in state["ladders"].items():
        start_x, start_y = get_cell_coords(start)
        end_x, end_y = get_cell_coords(end)
        pygame.draw.line(screen, GREEN, (start_x + CELL_SIZE//2, start_y + CELL_SIZE//2), 
                        (end_x + CELL_SIZE//2, end_y + CELL_SIZE//2), 3)
        pygame.draw.circle(screen, GREEN, (start_x + CELL_SIZE//2, start_y + CELL_SIZE//2), 5)
        pygame.draw.circle(screen, GREEN, (end_x + CELL_SIZE//2, end_y + CELL_SIZE//2), 5)

def draw_dice_button(screen):
    button_rect = pygame.Rect(330, 720, BUTTON_WIDTH, BUTTON_HEIGHT)
    pygame.draw.rect(screen, YELLOW, button_rect)
    pygame.draw.rect(screen, BLACK, button_rect, 2)
    
    button_text = font.render("Roll Dice", True, BLACK)
    text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, text_rect)
    
    return button_rect

def draw_game_info(screen, state):
    # Draw current player
    player_text = font.render(f"Current Player: {state['current_player']}", True, BLACK)
    screen.blit(player_text, (20, 20))
    
    # Draw game over message
    if state['game_over']:
        winner_text = font.render(f"Player {state['winner']} wins!", True, BLACK)
        screen.blit(winner_text, (20, 50))
    
    # Draw message
    message_text = font.render(state['message'], True, BLACK)
    screen.blit(message_text, (20, 70))

def draw_player_identification(screen):
    # Get player number from local player_id
    player_num = int(player_id.split('_')[1])
    # Set color based on player number
    color = RED if player_num == 1 else BLUE
    # Create message
    message = f"You are Player {player_num}"
    # Render text
    text = small_font.render(message, True, color)
    # Position at bottom left with some padding
    screen.blit(text, (20, 780 - text.get_height()))

def update_animation():
    global animating, current_anim_pos, animation_phase, snake_ladder_animation, snake_ladder_end_pos, target_anim_pos
    
    if not animating:
        return
    
    # Update position using linear interpolation
    current_anim_pos[0] += (target_anim_pos[0] - current_anim_pos[0]) * ANIMATION_SPEED
    current_anim_pos[1] += (target_anim_pos[1] - current_anim_pos[1]) * ANIMATION_SPEED
    
    # Check if animation is complete (close enough to target)
    if (abs(current_anim_pos[0] - target_anim_pos[0]) < 1 and 
        abs(current_anim_pos[1] - target_anim_pos[1]) < 1):
        if animation_phase == 1 and snake_ladder_animation:
            # Start second phase of snake/ladder animation
            animation_phase = 2
            current_anim_pos = target_anim_pos.copy()
            target_anim_pos = list(get_cell_coords(snake_ladder_end_pos))  # Remove the +1
        else:
            # Animation complete
            animating = False
            animation_phase = 1
            snake_ladder_animation = False

def draw_players(screen, state):
    for pid, pos in state["players"].items():
        x, y = get_cell_coords(pos + 1)
        player_num = int(pid.split('_')[1])
        color = RED if player_num == 1 else BLUE
        offset = -10 if player_num == 1 else 10
        
        # If this player is being animated, use animation position
        if animating and pid == current_player_animating:
            draw_x, draw_y = current_anim_pos
        else:
            draw_x, draw_y = x + offset, y
        
        pygame.draw.circle(screen, color, (draw_x, draw_y), PLAYER_SIZE)
        player_text = small_font.render(str(player_num), True, WHITE)
        player_text_rect = player_text.get_rect(center=(draw_x, draw_y))
        screen.blit(player_text, player_text_rect)

def draw_modal(screen, modal, modal_x, modal_y, modal_width, modal_height):
    # Create a surface with alpha channel
    modal_surface = pygame.Surface((modal_width, modal_height), pygame.SRCALPHA)
    
    # Draw semi-transparent background
    pygame.draw.rect(modal_surface, (200, 200, 200, 224), (0, 0, modal_width, modal_height))
    pygame.draw.rect(modal_surface, (0, 0, 0, 255), (0, 0, modal_width, modal_height), 2)
    
    # Split text into lines and render each line
    lines = modal.split("\n")
    line_height = 25  # Space between lines
    start_y = 20  # Start text 20 pixels from top of modal
    
    for i, line in enumerate(lines):
        if i * line_height < modal_height - 40:  # Only show lines that fit in the modal
            text = small_font.render(line, True, (0, 0, 0, 255))  # Black text with full opacity
            text_rect = text.get_rect(centerx=modal_width//2, y=start_y + i * line_height)
            modal_surface.blit(text, text_rect)
    
    # Draw user input if trivia modal is active
    if active_modal == "trivia":
        input_text = small_font.render(f"Your answer: {user_answer}", True, (0, 0, 255, 255))  # Blue text with full opacity
        modal_surface.blit(input_text, (20, modal_height - 60))
    
    continue_text = small_font.render("Press ENTER to continue...", True, (0, 0, 0, 255))  # Black text with full opacity
    modal_surface.blit(continue_text, (20, modal_height - 30))
    
    screen.blit(modal_surface, (modal_x, modal_y))


def main():
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption("Snakes & Ladders")
    global font, small_font, user_answer, active_modal
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)
    homescreen = True

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption("Snakes & Ladders")
    global font
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)
    
    join_game()
    state = get_state()
    modal = ""
    
    while True:
        screen.fill(WHITE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    button_rect = pygame.Rect(330, 720, BUTTON_WIDTH, BUTTON_HEIGHT)
                    if button_rect.collidepoint(mouse_pos):
                        result = roll_dice()
                        modal = result.get("content", "")
                        state = get_state()
        
        # Draw game elements
        draw_board(screen, state)
        draw_snakes_ladders(screen, state)
        draw_dice_button(screen)
        draw_game_info(screen, state)
        
        # Draw players
        for pid, pos in state["players"].items():
            x, y = get_cell_coords(pos)
            color = RED if pid == player_id else BLUE
            offset = -10 if pid == player_id else 10
            pygame.draw.circle(screen, color, (x + CELL_SIZE//2 + offset, y + CELL_SIZE//2), PLAYER_SIZE)
        
        # Modal box
        if modal:
            pygame.draw.rect(screen, GRAY, (100, 600, 600, 150))
            lines = modal.split("\n")
            for i, line in enumerate(lines[:5]):
                text = font.render(line, True, BLACK)
                screen.blit(text, (120, 620 + i * 25))
        
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()