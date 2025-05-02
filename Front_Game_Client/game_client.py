import pygame
import requests
from sys import exit

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
    row = 9 - (pos // 10)
    col = pos % 10 if (9 - row) % 2 == 0 else 9 - (pos % 10)
    return col * 60 + 100, row * 60 + 100

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption("Maropelleh Multiplayer")
    font = pygame.font.SysFont(None, 30)
    join_game()

    state = get_state()
    modal = ""
    while True:
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    result = roll_dice()
                    modal = result["content"]

        # Draw players
        state = get_state()
        for pid, pos in state["players"].items():
            x, y = get_cell_coords(pos)
            color = (255, 0, 0) if pid == player_id else (0, 0, 255)
            pygame.draw.circle(screen, color, (x + 30, y + 30), 20)

        # Modal box
        if modal:
            pygame.draw.rect(screen, (200, 200, 200), (100, 600, 600, 150))
            lines = modal.split("\n")
            for i, line in enumerate(lines[:5]):
                text = font.render(line, True, (0, 0, 0))
                screen.blit(text, (120, 620 + i * 25))

        pygame.display.update()
        pygame.time.delay(100)

if __name__ == "__main__":
    main()
