import pygame
import sys

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Circle properties
start_pos = (100, 300)  # Starting position
end_pos = (600, 100)    # Target position
current_pos = list(start_pos)  # Current position (as list so we can modify it)
radius = 20
speed = 0.05  # Speed of animation (0.1 = 10% of the way each frame)                             
# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Clear screen
    screen.fill((255, 255, 255))
    
    # Update position (linear interpolation)
    current_pos[0] += (end_pos[0] - current_pos[0]) * speed
    current_pos[1] += (end_pos[1] - current_pos[1]) * speed
    
    # Draw circle at current position
    pygame.draw.circle(screen, (255, 0, 0), current_pos, radius)
    
    # Update display
    pygame.display.flip()
    clock.tick(60)  # 60 FPS