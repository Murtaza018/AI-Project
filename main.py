import pygame
import random

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 1200, 600
ROWS, COLS = 10, 10  # 10x10 Grid
CELL_WIDTH = WIDTH // COLS
CELL_HEIGHT = HEIGHT // ROWS

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Project Game")

# Define bright color shades & their names
COLORS = {
    "Red": (255, 100, 100),
    "Blue": (100, 150, 255),
    "Green": (100, 255, 100),
    "Yellow": (255, 255, 150)
}

# Generate random colors and store their names
color_grid = [[random.choice(list(COLORS.items())) for _ in range(COLS)] for _ in range(ROWS)]

# Initialize font
pygame.font.init()
font = pygame.font.Font(None, 16)  # Default font for color names
index_font = pygame.font.Font(None, 20)  # Bigger font for numbers

# Generate indexes in a snakes-and-ladders pattern
index_grid = [[0] * COLS for _ in range(ROWS)]
index = 1  # Start from 1
for row in range(ROWS):
    if row % 2 == 0:
        # Left to right
        for col in range(COLS):
            index_grid[row][col] = index
            index += 1
    else:
        # Right to left (zig-zag pattern)
        for col in range(COLS - 1, -1, -1):
            index_grid[row][col] = index
            index += 1

# Reverse rows so that 1 starts from bottom-left
index_grid.reverse()
color_grid.reverse()

# Game loop
running = True
while running:
    screen.fill((255, 255, 255))  # Clear screen

    # Draw grid with bright colors & text
    for row in range(ROWS):
        for col in range(COLS):
            color_name, color_value = color_grid[row][col]
            pygame.draw.rect(screen, color_value, (col * CELL_WIDTH, row * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT))

            # Render color name text
            text_surface = font.render(color_name, True, (0, 0, 0))  # Black text
            text_rect = text_surface.get_rect(center=(col * CELL_WIDTH + CELL_WIDTH // 2, row * CELL_HEIGHT + CELL_HEIGHT // 2))
            screen.blit(text_surface, text_rect)

            # Render index number
            index_text = index_font.render(str(index_grid[row][col]), True, (0, 0, 0))  # Black index number
            index_rect = index_text.get_rect(topleft=(col * CELL_WIDTH + 5, row * CELL_HEIGHT + 5))  # Top-left of box
            screen.blit(index_text, index_rect)

    # Draw grid lines
    for i in range(1, COLS):
        pygame.draw.line(screen, (0, 0, 0), (i * CELL_WIDTH, 0), (i * CELL_WIDTH, HEIGHT), 2)
    for i in range(1, ROWS):
        pygame.draw.line(screen, (0, 0, 0), (0, i * CELL_HEIGHT), (WIDTH, i * CELL_HEIGHT), 2)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()  # Update display

pygame.quit()
