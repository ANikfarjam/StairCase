import pygame
import requests
from sys import exit
import time
import math

# Colors
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

SERVER_URL = "http://127.0.0.1:5001"
# SERVER_URL = "http://10.0.0.120:5001"
player_id = None

# Animation constants
ANIMATION_SPEED = 0.1  # Speed of animation (0.1 = 10% of the way each frame)
ANIMATION_PHASE_DURATION = 1
BACKGROUND_SCROLL_SPEED = 1 # Pixels per frame to move the sky background image

# Animation state
animating = False
current_anim_pos = [0, 0]
target_anim_pos = [0, 0]
current_player_animating = None
snake_ladder_animation = False
snake_ladder_end_pos = None
animation_phase = 1  # 1 for animating normal movement, 2 for moving up/down snake/ladder

# Background Image
background_x = 0
sky_background = pygame.image.load('graphics/blue-sky.png')
ground_background = pygame.image.load('graphics/ground.png')

# User answer input for hangman and trivia minigames
user_answer = ""
active_modal = None  # 'trivia', 'hangman', or None

screen = pygame.display.set_mode((800, 800))


def roll_dice():
    """ Handles rolling the dice for player movement across the board

    Parameters: None

    Returns: This returns a dictionary from the server's response containing game state info:
            - roll: The dice roll value (1-6)
            - before_roll: Player's position before the roll
            - new_position: Player's position after the roll
            - mini_game: Type of minigame if landed on one ('trivia' or 'hangman')
            - content: Content for minigame if applicable
            - message: Game message to display
            - game_over: Boolean indicating if game is over
            - winner: Player that won if game is over
            - current_player: Current player's turn
            - snake_ladder: Boolean indicating if landed on snake/ladder
            - snake_ladder_start: Starting position of snake/ladder
            - snake_ladder_end: Ending position of snake/ladder
    """
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
    """ Handles getting the current game state from the server

    Parameters: None

    Returns: This returns a dictionary from the server's response containing game state info:
            - players: Dictionary of player positions
            - snakes: Dictionary of snake positions
            - ladders: Dictionary of ladder positions
            - trivia_cells: List of positions that have trivia minigames
            - hangman_cells: List of positions that have hangman minigames
            - current_player: Current player's turn
            - game_over: Boolean indicating if game is over
            - winner: Player that won if game is over
    """
    return requests.get(f"{SERVER_URL}/state").json()

def get_cell_coords(pos):
    """ Handles getting the coordinates of a cell on the board

    Parameters: pos (int): The position on the board

    Returns: This returns a tuple of coordinates for the cell at the position
    """
    # Ensure pos is an integer
    pos = int(pos)
    row = (pos - 1) // BOARD_SIZE
    col = (pos - 1) % BOARD_SIZE
    x = col * CELL_SIZE + GRID_OFFSET + CELL_SIZE//2
    y = (BOARD_SIZE - 1 - row) * CELL_SIZE + GRID_OFFSET + CELL_SIZE//2
    return x, y

def draw_restart_button():
    """ 
    Handles drawing the restart button, which will show when a player wins.
    This basically allows the players to play again.

    Parameters: None

    Returns: This returns a rectangle object for the restart button.
    """
    button_rect = pygame.Rect(520, 720, BUTTON_WIDTH + 15, BUTTON_HEIGHT)
    pygame.draw.rect(screen, ORANGE, button_rect)
    pygame.draw.rect(screen, BLACK, button_rect, 2)

    button_text = font.render("Restart Game", True, BLACK)
    text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, text_rect)

    return button_rect

def draw_board(screen, state):
    """ 
    Handles drawing the 10x10 game board, and indicating which 
    cells have trivia and hangman minigames.

    Parameters: screen (pygame.Surface): The screen that will be drawn on
                state (dict): The current game state

    Returns: None
    """
    global background_x
    # Update background position
    background_x -= BACKGROUND_SCROLL_SPEED
    if background_x <= -sky_background.get_width():
        background_x = 0
    
    # Draw background (twice for seamless scrolling)
    screen.fill(WHITE)
    screen.blit(sky_background, (background_x, 0))
    screen.blit(sky_background, (background_x + sky_background.get_width(), 0))
    screen.blit(ground_background, (0, 700))
    # Draw grid
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            x = col * CELL_SIZE + GRID_OFFSET
            y = (BOARD_SIZE - 1 - row) * CELL_SIZE + GRID_OFFSET
            cell_num = row * BOARD_SIZE + col + 1

            color = LIGHT_BLUE if cell_num in state["trivia_cells"] else LIGHT_YELLOW if (row + col) % 2 == 0 else ORANGE
            # Draw filled square
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))
            # Draw square border
            pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 1)
            
            # Draw cell number

            text = font.render(str(cell_num), True, BLACK)
            text_rect = text.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2))
            screen.blit(text, text_rect)
            
            if cell_num in state["trivia_cells"]:
                trivia_text = smaller_font.render("Trivia", True, BLACK)
                text_rect = trivia_text.get_rect(centerx=x + CELL_SIZE//2, bottom=y + CELL_SIZE - 5)
                screen.blit(trivia_text, text_rect)

            # if cell_num in state["hangman_cells"]:
            #     hangman_text = smaller_font.render("Hangman", True, BLACK)
            #     text_rect = hangman_text.get_rect(centerx=x + CELL_SIZE//2, bottom=y + CELL_SIZE - 5)
            #     screen.blit(hangman_text, text_rect)

def draw_snakes_ladders(screen, state):
    """ 
    Handles drawing the snakes and ladders on the board.

    Parameters: screen (pygame.Surface): The screen that will be drawn on
                state (dict): The current game state

    Returns: None
    """
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
    """ 
    Handles drawing the roll dice button, which will only show for the current player 
    when it is their turn. 

    Parameters: screen (pygame.Surface): The screen that will be drawn on
                state (dict): The current game state

    Returns: This returns a rectangle object for the dice button.
    """
    # Only show button for current player
    if state['current_player'] != int(player_id.split('_')[1]):
        return None
    if active_modal in ["trivia", "hangman"]:
        return None
    
    button_rect = pygame.Rect(330, 720, BUTTON_WIDTH, BUTTON_HEIGHT)
    pygame.draw.rect(screen, YELLOW, button_rect)
    pygame.draw.rect(screen, BLACK, button_rect, 2)
    
    button_text = font.render("Roll Dice", True, BLACK)
    text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, text_rect)
    
    return button_rect

def draw_game_info(screen, state):
    """ 
    Handles drawing important messages on top of the screen
    that indicate which player's turn it is, game over message when
    there is a winner, and a message after each roll telling the player
    how much they rolled and the new position they moved to.

    Parameters: screen (pygame.Surface): The screen that will be drawn on
                state (dict): The current game state

    Returns: None
    """
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
    """ 
    On each player's screen, draws a tiny message on the bottom left
    telling them what player number (1 or 2) they are.

    Parameters: screen (pygame.Surface): The screen that will be drawn on

    Returns: None
    """
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
    """ 
    Handles updating the animation of the player's movement across the board
    when they roll the dice.

    Parameters: None

    Returns: None
    """
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
    """ 
    Draws the players, represented as circles, on the board.
    Player 1 is red and Player 2 is blue. This also draws the 
    player circle constantly moving during an animation.

    Parameters: screen (pygame.Surface): The screen that will be drawn on
                state (dict): The current game state

    Returns: None
    """
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
    """ 
    Draws a box modal on top of the screen, which displays the minigame

    Parameters: screen (pygame.Surface): The screen that will be drawn on
                modal (str): The message to display
                modal_x (int): The x coordinate of the modal
                modal_y (int): The y coordinate of the modal
                modal_width (int): The width of the modal
                modal_height (int): The height of the modal

    Returns: None
    """
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
    
    # Draw user input if trivia or hangman modal is active
    if active_modal in ["trivia"]:
        input_text = small_font.render(f"Your answer: {user_answer}", True, (0, 0, 255, 255))  # Blue text with full opacity
        modal_surface.blit(input_text, (20, modal_height - 60))
    
    continue_text = small_font.render("Press ENTER to continue...", True, (0, 0, 0, 255))  # Black text with full opacity
    modal_surface.blit(continue_text, (20, modal_height - 30))
    
    screen.blit(modal_surface, (modal_x, modal_y))


def main(passed_player_id):
    """
    Main function that initializes Pygame, sets up the game, runs the game loop.

    Parameters: passed_player_id (str): The player ID of the current player. This is used to identify
                which player is which on each client, and is used for turn handling, rolling dice,
                submitting minigame answers. 

    Returns: None
    """
    global player_id, font, small_font, smaller_font, user_answer, active_modal
    player_id = passed_player_id
    print(player_id)
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption("Snakes & Ladders")
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)
    smaller_font = pygame.font.SysFont(None, 14)
    
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
            
            # Handle modal input
            if modal:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Submit answer and close modal
                        if active_modal == "trivia":
                            # Send answer to server
                            res = requests.post(f"{SERVER_URL}/submit_answer", json={
                                "player_id": player_id,
                                "answer": user_answer
                            })
                            print(res.json())
                            user_answer = ""  # Clear answer
                            state = get_state()  # Update game state after answer
                            last_state_update = time.time()
                        modal = ""  # Close modal
                        active_modal = None
                    elif event.key == pygame.K_BACKSPACE:
                        user_answer = user_answer[:-1]
                    elif event.unicode.isprintable():
                        user_answer += event.unicode
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    if not state['game_over']:  # Only check for dice button when game is not over
                        button_rect = draw_dice_button(screen, state)
                        if button_rect and button_rect.collidepoint(mouse_pos) and not animating:  # Only allow rolling when not animating
                            result = roll_dice()
                            modal = result.get("content", "")
                            if modal:  # If there's a modal, set the active modal type
                                active_modal = result.get("mini_game", None)
                            state = get_state()
                            last_state_update = time.time()
                    elif state['game_over']:  # Check for restart button click when game is over
                        restart_button_rect = draw_restart_button()
                        if restart_button_rect.collidepoint(mouse_pos):
                            # Send restart request to server
                            res = requests.post(f"{SERVER_URL}/new_game")
                            if res.status_code == 200:
                                state = get_state()
                                last_state_update = time.time()
        
        # Draw game elements
        draw_board(screen, state)
        draw_snakes_ladders(screen, state)
        if not state['game_over']:
            draw_dice_button(screen, state)
        draw_game_info(screen, state)
        draw_player_identification(screen)
        
        draw_players(screen, state)
        update_animation()
            
        # Draw restart button if game is over
        if state['game_over']:
            draw_restart_button()
        
        # Modal box
        if modal:
            # Calculate modal box dimensions and position
            modal_width = 700
            modal_height = 300
            modal_x = (800 - modal_width) // 2  # Center horizontally
            modal_y = (800 - modal_height) // 2  # Center vertically
            
            draw_modal(screen, modal, modal_x, modal_y, modal_width, modal_height)
        
        pygame.display.update()
        clock.tick(60)

# if __name__ == "__main__":
#     main()
