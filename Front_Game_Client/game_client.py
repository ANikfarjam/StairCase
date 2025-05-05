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

SERVER_URL = "http://127.0.0.1:5000"
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

def join_game():
    global player_id
    try:
        res = requests.post(f"{SERVER_URL}/join")
        print("🔁 Response status:", res.status_code)
        print("🔁 Response body:", res.text)
        res.raise_for_status()
        player_id = res.json()["player_id"]
        print("✅ Joined as:", player_id)
    except Exception as e:
        print("❌ join_game failed:", e)
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
    row = (pos - 1) // BOARD_SIZE
    col = (pos - 1) % BOARD_SIZE
    x = col * CELL_SIZE + GRID_OFFSET + CELL_SIZE//2
    y = (BOARD_SIZE - 1 - row) * CELL_SIZE + GRID_OFFSET + CELL_SIZE//2
    return x, y
    # row = 9 - (pos // 10)
    # col = pos % 10 if (9 - row) % 2 == 0 else 9 - (pos % 10)
    # return col * CELL_SIZE + GRID_OFFSET, row * CELL_SIZE + GRID_OFFSET

def draw_board(screen, state):
    global background_x
    
    # Update background position
    background_x -= BACKGROUND_SCROLL_SPEED
    if background_x <= -sky_background.get_width():
        background_x = 0
    
    # Draw background (twice for seamless scrolling)
    screen.fill(WHITE)
    screen.blit(sky_background, (background_x, 0))
    screen.blit(sky_background, (background_x + sky_background.get_width(), 0))
    
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
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            x = col * CELL_SIZE + GRID_OFFSET
            y = (BOARD_SIZE - 1 - row) * CELL_SIZE + GRID_OFFSET
            cell_num = row * BOARD_SIZE + col + 1

            if str(cell_num) in state["snakes"]:
                # Draw snake head (start position)
                pygame.draw.circle(screen, RED, (x + CELL_SIZE//2, y + CELL_SIZE//2), 5)
                # Draw "S" for snake
                s_text = small_font.render("S", True, RED)
                s_rect = s_text.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2 + 15))
                screen.blit(s_text, s_rect)
                
                # Get end position coordinates
                end_x, end_y = get_cell_coords(state["snakes"][str(cell_num)])
                # Draw snake body (line from start to end)
                pygame.draw.line(screen, RED, (x + CELL_SIZE//2, y + CELL_SIZE//2), 
                               (end_x, end_y), 3)
                # Draw circle at end position
                pygame.draw.circle(screen, RED, (end_x, end_y), 5)
                
            elif str(cell_num) in state["ladders"]:
                # Draw ladder bottom (start position)
                pygame.draw.circle(screen, GREEN, (x + CELL_SIZE//2, y + CELL_SIZE//2), 5)
                # Draw "L" for ladder
                l_text = small_font.render("L", True, GREEN)
                l_rect = l_text.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2 + 15))
                screen.blit(l_text, l_rect)
                
                # Get end position coordinates
                end_x, end_y = get_cell_coords(state["ladders"][str(cell_num)])
                # Draw ladder (line from start to end)
                pygame.draw.line(screen, GREEN, (x + CELL_SIZE//2, y + CELL_SIZE//2), 
                               (end_x, end_y), 3)
                # Draw circle at end position
                pygame.draw.circle(screen, GREEN, (end_x, end_y), 5)

def draw_dice_button(screen, state):
    # Only show button for current player
    if state['current_player'] != int(player_id.split('_')[1]):
        return None
    
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

def main():
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption("Snakes & Ladders")
    global font, small_font
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)
    
    join_game()
    state = get_state()
    modal = ""
    
    # Add state update timer
    last_state_update = time.time()
    state_update_interval = 0.5  # Update state every 0.5 seconds

    print(state['snakes'])
    print(state['ladders'])
    
    while True:
        screen.fill(WHITE)
        
        # Check if it's time to update state
        current_time = time.time()
        if current_time - last_state_update >= state_update_interval:
            state = get_state()
            last_state_update = current_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    button_rect = draw_dice_button(screen, state)
                    if button_rect and button_rect.collidepoint(mouse_pos) and not animating:  # Only allow rolling when not animating
                        result = roll_dice()
                        modal = result.get("content", "")
                        state = get_state()
                        last_state_update = time.time()
        
        # Draw game elements
        draw_board(screen, state)
        draw_snakes_ladders(screen, state)
        draw_dice_button(screen, state)
        draw_game_info(screen, state)
        draw_player_identification(screen)
        
        # Draw players
        draw_players(screen, state)
        
        # Update animation
        update_animation()
        
        # Modal box
        if modal:
            # Calculate modal box dimensions and position
            modal_width = 600
            modal_height = 300
            modal_x = (800 - modal_width) // 2  # Center horizontally
            modal_y = (800 - modal_height) // 2  # Center vertically
            
            # Draw modal background with border
            pygame.draw.rect(screen, GRAY, (modal_x, modal_y, modal_width, modal_height))
            pygame.draw.rect(screen, BLACK, (modal_x, modal_y, modal_width, modal_height), 2)
            
            # Split text into lines and render each line
            lines = modal.split("\n")
            line_height = 30  # Space between lines
            start_y = modal_y + 20  # Start text 20 pixels from top of modal
            
            for i, line in enumerate(lines):
                if i * line_height < modal_height - 40:  # Only show lines that fit in the modal
                    text = font.render(line, True, BLACK)
                    text_rect = text.get_rect(centerx=modal_x + modal_width//2, y=start_y + i * line_height)
                    screen.blit(text, text_rect)
        
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
