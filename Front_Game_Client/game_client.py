import pygame
import requests
from sys import exit

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
    res = requests.post(f"{SERVER_URL}/roll", json={"player_id": player_id})
    return res.json()

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
        pygame.time.delay(100)

if __name__ == "__main__":
    main()
