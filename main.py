import pygame
import random
import math
import time
import copy
from cards import generate_uno_deck

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 1280, 720
ROWS, COLS = 10, 10
CELL_WIDTH = WIDTH // COLS
BOARD_HEIGHT_RATIO = 0.7
BOARD_HEIGHT = int(HEIGHT * BOARD_HEIGHT_RATIO)
CELL_HEIGHT = BOARD_HEIGHT // ROWS
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Game Board")

# Define color palette with more vibrant colors
COLORS = {
    "Red": (255, 80, 80),
    "Blue": (80, 120, 255),
    "Green": (80, 220, 80),
    "Yellow": (255, 220, 80),
    "Black": (50, 50, 50),
    "Background": (240, 240, 255),
    "BoardBorder": (30, 30, 60),
    "GridLine": (200, 200, 220),
}

# Player settings with improved aesthetics
PLAYER_COLORS = {
    "Player1": (220, 50, 50),    # Deeper red
    "Player2": (50, 80, 220),    # Deeper blue
    "Player3": (50, 180, 50),    # Deeper green
    "Player4": (220, 180, 40),   # Deeper yellow
}

PLAYER_GRADIENTS = {
    "Player1": [(255, 100, 100), (180, 30, 30)],  # Red gradient
    "Player2": [(100, 150, 255), (30, 60, 180)],  # Blue gradient
    "Player3": [(100, 230, 100), (30, 160, 30)],  # Green gradient
    "Player4": [(255, 230, 100), (200, 160, 30)], # Yellow gradient
}

# Game state variables
players = {
    "Player1": {"symbol": "🔴", "pos": 1, "target_pos": (0, 0), "skip_turn": False},
    "Player2": {"symbol": "🔵", "pos": 1, "target_pos": (0, 0), "skip_turn": False},
    "Player3": {"symbol": "🟢", "pos": 1, "target_pos": (0, 0), "skip_turn": False},
    "Player4": {"symbol": "🟡", "pos": 1, "target_pos": (0, 0), "skip_turn": False},
}

active_players = ["Player1", "Player2"]  # Can be expanded to include Player3 and Player4
current_player_idx = 0
current_player = active_players[current_player_idx]
game_direction = 1  # 1 for normal order, -1 for reversed
move_animation = False
animation_start_time = 0
animation_duration = 0.5  # seconds
animation_card = None
message = ""
message_timer = 0

# New variables for black card functionality
waiting_for_color_choice = False
black_card_played = False

# AI thinking flag
ai_thinking = False
ai_move_time = 0

# Load fonts with better sizes
pygame.font.init()
small_font = pygame.font.Font(None, 20)
index_font = pygame.font.Font(None, 26)
card_font = pygame.font.Font(None, 40)
title_font = pygame.font.Font(None, 48)
message_font = pygame.font.Font(None, 36)

# Grid setup (snakes and ladders style)
def create_index_grid():
    grid = [[0] * COLS for _ in range(ROWS)]
    index = 1
    for row in range(ROWS-1, -1, -1):  # Start from bottom row
        direction = range(COLS) if (ROWS-1-row) % 2 == 0 else reversed(range(COLS))
        for col in direction:
            grid[row][col] = index
            index += 1
    return grid

index_grid = create_index_grid()

# Create a colorful board
color_grid = [
    [
        random.choice([(name, rgb) for name, rgb in COLORS.items() 
                     if name not in ["Black", "Background", "BoardBorder", "GridLine"]])
        for _ in range(COLS)
    ]
    for _ in range(ROWS)
]

# Get UNO deck and remove 0 cards
def get_filtered_deck():
    deck = generate_uno_deck()
    # Filter out all "0" cards
    filtered_deck = [card for card in deck if card["label"] != "0"]
    return filtered_deck

# UNO deck without 0 cards
deck = get_filtered_deck()
random.shuffle(deck)
player_hands = {player: [deck.pop() for _ in range(7)] for player in active_players}
current_card = deck.pop()
# Make sure the starting card is not a special card
while not current_card["label"].isdigit():
    deck.append(current_card)
    random.shuffle(deck)
    current_card = deck.pop()

# Function to get row and column from position number
def get_row_col_from_pos(pos):
    pos = max(1, min(pos, ROWS * COLS))  # Ensure position is within bounds
    pos -= 1  # Convert to 0-indexed
    
    for row in range(ROWS):
        for col in range(COLS):
            if index_grid[row][col] == pos + 1:
                return row, col
    
    return 0, 0  # Default position if not found

# Update player positions based on their position number
for player in players:
    pos = players[player]["pos"]
    row, col = get_row_col_from_pos(pos)
    players[player]["target_pos"] = (row, col)

# Draw a prettier card
def draw_card(x, y, color, label, selected=False, clickable=False):
    # Card shadow
    pygame.draw.rect(screen, (50, 50, 50, 100), (x+3, y+3, 84, 124), border_radius=14)
    
    # Card background
    card_color = COLORS.get(color, (0, 0, 0))
    pygame.draw.rect(screen, card_color, (x, y, 84, 124), border_radius=14)
    
    # Selection highlight
    if selected:
        pygame.draw.rect(screen, (255, 255, 255), (x-3, y-3, 90, 130), 3, border_radius=16)
    
    # Clickable highlight
    if clickable:
        # Pulsating border effect
        pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) / 2  # 0 to 1
        highlight_color = (255, 255, 255)
        border_width = int(2 + pulse * 2)
        pygame.draw.rect(screen, highlight_color, 
                       (x-2, y-2, 88, 128), border_width, border_radius=16)
    
    # Card border
    pygame.draw.rect(screen, (0, 0, 0), (x, y, 84, 124), 2, border_radius=14)
    
    # UNO oval in the middle
    if color != "Black":
        pygame.draw.ellipse(screen, (255, 255, 255), (x+12, y+30, 60, 80))
        pygame.draw.ellipse(screen, (0, 0, 0), (x+12, y+30, 60, 80), 2)
    
    # Card text
    text_color = (255, 255, 255) if color == "Black" else (0, 0, 0)
    
    # Top left and bottom right label
    small_text = small_font.render(str(label), True, text_color)
    screen.blit(small_text, (x + 8, y + 8))
    screen.blit(pygame.transform.rotate(small_text, 180), (x + 76 - small_text.get_width(), y + 116 - small_text.get_height()))
    
    # Middle label
    text_surface = card_font.render(str(label), True, text_color)
    text_rect = text_surface.get_rect(center=(x + 42, y + 70))
    screen.blit(text_surface, text_rect)
    
    return pygame.Rect(x, y, 84, 124)  # Return the card's rect for click detection

# Draw the deck of cards (face down)
def draw_deck(x, y, clickable=True):
    # Draw multiple stacked cards to give depth
    for i in range(3):
        offset = i * 3
        # Shadow
        pygame.draw.rect(screen, (50, 50, 50, 100), 
                       (x+3+offset, y+3-offset, 84, 124), 
                       border_radius=14)
        
        # Card back
        pygame.draw.rect(screen, (50, 50, 150), 
                       (x+offset, y-offset, 84, 124), 
                       border_radius=14)
        
        # Card border
        pygame.draw.rect(screen, (0, 0, 0), 
                       (x+offset, y-offset, 84, 124), 
                       2, border_radius=14)
        
        # UNO logo on back
        if i == 2:  # Only on top card
            pygame.draw.ellipse(screen, (200, 50, 50), (x+12+offset, y+30-offset, 60, 80))
            pygame.draw.ellipse(screen, (0, 0, 0), (x+12+offset, y+30-offset, 60, 80), 2)
            text = card_font.render("UNO", True, (255, 255, 255))
            text_rect = text.get_rect(center=(x+42+offset, y+70-offset))
            screen.blit(text, text_rect)
    
    # Pulsating highlight if clickable and deck not empty
    if clickable and len(deck) > 0:
        pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) / 2  # 0 to 1
        highlight_color = (255, 255, 255)
        border_width = int(2 + pulse * 2)
        pygame.draw.rect(screen, highlight_color, 
                       (x+6-2, y-6-2, 88, 128), 
                       border_width, border_radius=16)
    
    # Display deck count
    count_text = index_font.render(f"{len(deck)} cards", True, (255, 255, 255))
    screen.blit(count_text, (x + 42 - count_text.get_width() // 2, y + 130))
    
    return pygame.Rect(x+6, y-6, 84, 124)  # Return the top card's rect for click detection

# Draw a prettier player piece
def draw_player(player_name, row, col, offset=(0, 0)):
    # Calculate center position of the cell
    base_x = col * CELL_WIDTH + CELL_WIDTH // 2
    base_y = row * CELL_HEIGHT + CELL_HEIGHT // 2 + board_y_offset
    
    # Apply offset for multiple players in same cell
    x = base_x + offset[0]
    y = base_y + offset[1]
    
    radius = min(CELL_WIDTH, CELL_HEIGHT) // 4
    
    # Highlight current player
    if player_name == current_player:
        glow_radius = radius + 5
        for i in range(3):
            alpha = 150 - i * 50
            pygame.draw.circle(screen, (*PLAYER_COLORS[player_name], alpha), (x, y), glow_radius - i)
    
    # Draw shadow
    pygame.draw.circle(screen, (50, 50, 50, 100), (x+2, y+2), radius)
    
    # Draw gradient piece
    colors = PLAYER_GRADIENTS[player_name]
    for i in range(radius, 0, -1):
        ratio = i / radius
        r = int(colors[0][0] * ratio + colors[1][0] * (1 - ratio))
        g = int(colors[0][1] * ratio + colors[1][1] * (1 - ratio))
        b = int(colors[0][2] * ratio + colors[1][2] * (1 - ratio))
        pygame.draw.circle(screen, (r, g, b), (x, y), i)
    
    # Draw border
    pygame.draw.circle(screen, (0, 0, 0), (x, y), radius, 2)
    
    # Draw player number inside
    text = small_font.render(player_name[-1], True, (255, 255, 255))
    text_rect = text.get_rect(center=(x, y))
    screen.blit(text, text_rect)

# Calculate positions to avoid overlap when multiple players on same cell
def get_player_offsets(player_count):
    if player_count == 1:
        return [(0, 0)]
    elif player_count == 2:
        return [(-10, -10), (10, 10)]
    elif player_count == 3:
        return [(0, -15), (-13, 8), (13, 8)]
    else:  # 4 or more
        return [(-12, -12), (12, -12), (-12, 12), (12, 12)]

# Check if a card can be played on the current card
def can_play_card(card):
    global black_card_played
    
    # If a black card was just played, any card can be played
    if black_card_played:
        return True
    
    # Number cards
    if card["label"].isdigit() and current_card["label"].isdigit():
        return card["label"] == current_card["label"] or card["color"] == current_card["color"]
    
    # Same action card
    if card["label"] == current_card["label"]:
        return True
    
    # Same color
    if card["color"] == current_card["color"]:
        return True
    
    # Black cards can be played on anything
    if card["color"] == "Black":
        return True
    
    # Current card is black
    if current_card["color"] == "Black":
        return True
    
    return False

# Draw color selection buttons
def draw_color_selection():
    button_width = 100
    button_height = 50
    spacing = 20
    total_width = 4 * button_width + 3 * spacing
    start_x = (WIDTH - total_width) // 2
    y = HEIGHT // 2 - button_height // 2
    
    color_buttons = []
    
    for i, color in enumerate(["Red", "Blue", "Green", "Yellow"]):
        x = start_x + i * (button_width + spacing)
        rect = pygame.Rect(x, y, button_width, button_height)
        
        # Draw button
        pygame.draw.rect(screen, COLORS[color], rect, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2, border_radius=10)
        
        # Draw text
        text = index_font.render(color, True, (0, 0, 0) if color == "Yellow" else (255, 255, 255))
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
        
        color_buttons.append((rect, color))
    
    # Draw prompt
    prompt = message_font.render("Select a color", True, (30, 30, 100))
    prompt_rect = prompt.get_rect(center=(WIDTH // 2, y - 40))
    screen.blit(prompt, prompt_rect)
    
    return color_buttons

# Handle the effects of playing a card
def apply_card_effect(card, player_idx):
    global current_player_idx, game_direction, message, waiting_for_color_choice, black_card_played
    
    # If it's a number card, move the player
    if card["label"].isdigit():
        steps = int(card["label"])
        players[active_players[player_idx]]["pos"] += steps
        message = f"{active_players[player_idx]} moves {steps} steps"
    
    # Special cards
    elif card["label"] == "Skip":
        next_player_idx = (player_idx + game_direction) % len(active_players)
        players[active_players[next_player_idx]]["skip_turn"] = True
        message = f"{active_players[next_player_idx]} turn skipped!"
    
    elif card["label"] == "Reverse":
        # Modified: Reverse now works as Skip
        next_player_idx = (player_idx + game_direction) % len(active_players)
        players[active_players[next_player_idx]]["skip_turn"] = True
        message = f"Reverse used as Skip! {active_players[next_player_idx]} turn skipped!"
    
    elif card["label"].startswith("Draw"):
        next_player_idx = (player_idx + game_direction) % len(active_players)
        draw_count = int(card["label"].split()[1])
        next_player = active_players[next_player_idx]
        
        # Draw cards make the next player move backward (whether colored or black)
        players[next_player]["pos"] = max(1, players[next_player]["pos"] - draw_count)
        # Update target position immediately
        row, col = get_row_col_from_pos(players[next_player]["pos"])
        players[next_player]["target_pos"] = (row, col)
        
        # For black Draw cards, the current player gets to play again
        if card["color"] == "Black":
            message = f"{next_player} moves back {draw_count} steps! {current_player} gets another turn!"
            black_card_played = True
            waiting_for_color_choice = True
        else:
            message = f"{next_player} moves back {draw_count} steps!"
            # For colored Draw cards, the next player also draws cards
            for _ in range(min(draw_count, len(deck))):
                if deck:
                    player_hands[next_player].append(deck.pop())
            message += f" and draws {draw_count} cards!"
    
    # Make sure position is within bounds
    players[active_players[player_idx]]["pos"] = max(1, min(players[active_players[player_idx]]["pos"], ROWS * COLS))
    
    # Update player's target position
    row, col = get_row_col_from_pos(players[active_players[player_idx]]["pos"])
    players[active_players[player_idx]]["target_pos"] = (row, col)
    
    # Check for win condition
    if players[active_players[player_idx]]["pos"] >= ROWS * COLS:
        message = f"{active_players[player_idx]} WINS!"
        return True
    
    return False

# Get the next player's turn
def advance_turn():
    global current_player_idx, current_player, message_timer, black_card_played
    
    # Reset black card flag when advancing turn
    black_card_played = False
    
    next_idx = (current_player_idx + game_direction) % len(active_players)
    
    # Skip players who have a skip_turn flag
    while players[active_players[next_idx]]["skip_turn"]:
        players[active_players[next_idx]]["skip_turn"] = False  # Reset the skip flag
        message = f"{active_players[next_idx]}'s turn is skipped!"
        message_timer = 120  # Show message for 2 seconds
        next_idx = (next_idx + game_direction) % len(active_players)
    
    current_player_idx = next_idx
    current_player = active_players[current_player_idx]

# Play a selected card from the player's hand
def play_card(card_idx):
    global current_card, move_animation, animation_start_time, animation_card, message_timer, waiting_for_color_choice, black_card_played
    
    card = player_hands[current_player][card_idx]
    
    # Check if the card can be played
    if can_play_card(card):
        # Remove card from hand
        player_hands[current_player].pop(card_idx)
        
        # Set animation
        animation_card = card
        move_animation = True
        animation_start_time = time.time()
        
        # Apply card effect
        game_over = apply_card_effect(card, current_player_idx)
        
        # Update the current card after animation finishes
        current_card = card
        
        # Set message timer
        message_timer = 120  # Show message for 2 seconds
        
        # Check if the game is over
        if game_over:
            return
        
        # Check if hand is empty (player wins)
        if len(player_hands[current_player]) == 0:
            message = f"{current_player} WINS!"
            message_timer = 300  # Show message for 5 seconds
            return
        
        # If we're waiting for color choice, don't advance turn
        if waiting_for_color_choice:
            return
        
        # If black card was played and this is the second card, now advance turn
        if black_card_played:
            black_card_played = False
            advance_turn()
            return
        
        # Advance to the next player for normal cards
        advance_turn()
        
        # If the next player's hand is empty, draw a card
        if len(player_hands[current_player]) == 0:
            if deck:
                player_hands[current_player].append(deck.pop())
    else:
        message = "Can't play that card!"
        message_timer = 120  # Show message for 2 seconds

# Draw a card from the deck for the current player
def draw_from_deck():
    global message, message_timer, black_card_played
    
    if len(deck) > 0:
        # Add animation for drawing (could be implemented later)
        
        # Add card to player's hand
        new_card = deck.pop()
        player_hands[current_player].append(new_card)
        
        message = f"{current_player} draws a card"
        message_timer = 120
        
        # Check if the drawn card can be played
        if can_play_card(new_card):
            message += " - you can play it!"
        else:
            # If card can't be played and not after black card, advance turn
            if not black_card_played:
                advance_turn()
    else:
        message = "Deck is empty!"
        message_timer = 120

# Set a color for the current card (after playing a black card)
def set_card_color(color):
    global current_card, waiting_for_color_choice, message, message_timer
    
    # Update the current card's color
    current_card["color"] = color
    waiting_for_color_choice = False
    
    message = f"Color changed to {color}! Play another card."
    message_timer = 120

# AI Bot Class with Minimax and Alpha-Beta Pruning
# class AIBot:
#     def __init__(self, player_name="Player2"):
#         self.player_name = player_name
#         self.thinking = False
#         self.last_move_time = 0
#         self.thinking_delay = 2.0  # 2 seconds delay
#         self.max_depth = 3  # Maximum depth for minimax search
    
#     def start_thinking(self):
#         self.thinking = True
#         self.last_move_time = time.time()
#         return "AI is thinking..."
    
#     def is_ready_to_move(self):
#         return self.thinking and (time.time() - self.last_move_time >= self.thinking_delay)
    
#     def find_best_move(self, player_hand):
#         # Find playable cards
#         playable_cards = []
#         for i, card in enumerate(player_hand):
#             if can_play_card(card):
#                 playable_cards.append((i, card))
        
#         if not playable_cards:
#             return None  # No playable cards, need to draw
        
#         # Use minimax with alpha-beta pruning to find the best move
#         best_score = float('-inf')
#         best_move = None
        
#         # Create a copy of the game state for simulation
#         game_state = self._create_game_state()
        
#         for idx, card in playable_cards:
#             # Simulate playing this card
#             score = self._minimax(game_state, card, 0, True, float('-inf'), float('inf'))
            
#             if score > best_score:
#                 best_score = score
#                 best_move = idx
        
#         return best_move
    
#     def _create_game_state(self):
#         # Create a simplified copy of the current game state
#         state = {
#             'players': copy.deepcopy(players),
#             'player_hands': {p: player_hands[p].copy() for p in active_players},
#             'current_card': current_card.copy(),
#             'current_player_idx': current_player_idx,
#             'deck_size': len(deck)
#         }
#         return state
    
#     def _minimax(self, state, card, depth, is_maximizing, alpha, beta):
#         # Terminal conditions
#         if depth >= self.max_depth:
#             return self._evaluate_state(state)
        
#         # Simulate playing the card
#         new_state = self._simulate_play_card(state, card, is_maximizing)
        
#         # Check if game is over after this move
#         if self._is_game_over(new_state):
#             return 1000 if is_maximizing else -1000
        
#         # Recursively evaluate possible moves
#         if is_maximizing:
#             max_eval = float('-inf')
#             for next_card in self._get_playable_cards(new_state, not is_maximizing):
#                 eval = self._minimax(new_state, next_card, depth + 1, False, alpha, beta)
#                 max_eval = max(max_eval, eval)
#                 alpha = max(alpha, eval)
#                 if beta <= alpha:
#                     break  # Beta cutoff
#             return max_eval
#         else:
#             min_eval = float('inf')
#             for next_card in self._get_playable_cards(new_state, not is_maximizing):
#                 eval = self._minimax(new_state, next_card, depth + 1, True, alpha, beta)
#                 min_eval = min(min_eval, eval)
#                 beta = min(beta, eval)
#                 if beta <= alpha:
#                     break  # Alpha cutoff
#             return min_eval
    
#     def _simulate_play_card(self, state, card, is_maximizing):
#         # Create a copy of the state to modify
#         new_state = copy.deepcopy(state)
        
#         # Determine which player is playing
#         player = "Player2" if is_maximizing else "Player1"
#         player_idx = 1 if is_maximizing else 0
        
#         # Remove card from hand
#         if card in new_state['player_hands'][player]:
#             new_state['player_hands'][player].remove(card)
        
#         # Update current card
#         new_state['current_card'] = card
        
#         # Apply card effects
#         if card["label"].isdigit():
#             # Move player forward
#             steps = int(card["label"])
#             new_state['players'][player]["pos"] += steps
#         elif card["label"] == "Skip" or card["label"] == "Reverse":
#             # Skip opponent's turn
#             opponent = "Player1" if is_maximizing else "Player2"
#             new_state['players'][opponent]["skip_turn"] = True
#         elif card["label"].startswith("Draw"):
#             # Move opponent backward
#             opponent = "Player1" if is_maximizing else "Player2"
#             draw_count = int(card["label"].split()[1])
#             new_state['players'][opponent]["pos"] = max(1, new_state['players'][opponent]["pos"] - draw_count)
        
#         # Update positions
#         for p in new_state['players']:
#             pos = new_state['players'][p]["pos"]
#             pos = max(1, min(pos, ROWS * COLS))
#             new_state['players'][p]["pos"] = pos
        
#         return new_state
    
#     def _get_playable_cards(self, state, is_maximizing):
#         # Get playable cards for the specified player
#         player = "Player2" if is_maximizing else "Player1"
#         playable = []
        
#         for card in state['player_hands'][player]:
#             if self._can_play_card(card, state['current_card']):
#                 playable.append(card)
        
#         return playable
    
#     def _can_play_card(self, card, current):
#         # Check if a card can be played on the current card
#         if card["color"] == "Black":
#             return True
#         if card["color"] == current["color"] or card["label"] == current["label"]:
#             return True
#         if current["color"] == "Black":
#             return True
#         return False
    
#     def _is_game_over(self, state):
#         # Check if any player has reached the end or has no cards
#         for player in ["Player1", "Player2"]:
#             if state['players'][player]["pos"] >= ROWS * COLS:
#                 return True
#             if len(state['player_hands'][player]) == 0:
#                 return True
#         return False
    
#     def _evaluate_state(self, state):
#         # Evaluate the game state from AI's perspective
#         ai_pos = state['players']["Player2"]["pos"]
#         human_pos = state['players']["Player1"]["pos"]
        
#         # Position difference (higher is better for AI)
#         position_score = ai_pos - human_pos
        
#         # Card advantage (fewer cards is better)
#         ai_cards = len(state['player_hands']["Player2"])
#         human_cards = len(state['player_hands']["Player1"])
#         card_score = human_cards - ai_cards
        
#         # Distance to goal
#         ai_distance = ROWS * COLS - ai_pos
#         human_distance = ROWS * COLS - human_pos
#         distance_score = human_distance - ai_distance
        
#         # Special cards in hand are valuable
#         special_card_score = 0
#         for card in state['player_hands']["Player2"]:
#             if card["label"] == "Skip" or card["label"] == "Reverse":
#                 special_card_score += 5
#             elif card["label"].startswith("Draw"):
#                 special_card_score += 10
#             elif card["color"] == "Black":
#                 special_card_score += 15
        
#         # Combine all factors with appropriate weights
#         total_score = (
#             position_score * 3 + 
#             card_score * 2 + 
#             distance_score * 5 + 
#             special_card_score
#         )
        
#         return total_score
    
#     def choose_color(self):
#         # Count colors in hand
#         color_counts = {"Red": 0, "Blue": 0, "Green": 0, "Yellow": 0}
#         for card in player_hands[self.player_name]:
#             if card["color"] in color_counts:
#                 color_counts[card["color"]] += 1
        
#         # Choose most common color
#         best_color = max(color_counts.items(), key=lambda x: x[1])[0] if any(color_counts.values()) else "Red"
#         return best_color

# AI Bot Class - Simplified to ensure it works
class AIBot:
    def __init__(self, player_name="Player2"):
        self.player_name = player_name
        self.thinking = False
        self.last_move_time = 0
        self.thinking_delay = 2.0  # 2 seconds delay
    
    def start_thinking(self):
        self.thinking = True
        self.last_move_time = time.time()
        return "AI is thinking..."
    
    def is_ready_to_move(self):
        return self.thinking and (time.time() - self.last_move_time >= self.thinking_delay)
    
    def find_best_move(self, player_hand):
        # Find playable cards - simplified approach
        playable_cards = []
        for i, card in enumerate(player_hand):
            if can_play_card(card):
                playable_cards.append((i, card))
        
        if not playable_cards:
            return None  # No playable cards, need to draw
        
        # Sort by value (higher numbers and special cards first)
        def card_value(card_tuple):
            idx, card = card_tuple
            if card["label"].isdigit():
                return int(card["label"])
            elif card["label"] == "Skip" or card["label"] == "Reverse":
                return 10
            elif card["label"].startswith("Draw"):
                return 15
            return 5
        
        playable_cards.sort(key=card_value, reverse=True)
        return playable_cards[0][0]  # Return index of best card

    def choose_color(self):
        # Count colors in hand
        color_counts = {"Red": 0, "Blue": 0, "Green": 0, "Yellow": 0}
        for card in player_hands[self.player_name]:
            if card["color"] in color_counts:
                color_counts[card["color"]] += 1
        
        # Choose most common color
        best_color = max(color_counts.items(), key=lambda x: x[1])[0] if any(color_counts.values()) else "Red"
        return best_color

# Create AI bot instance
ai_bot = AIBot()

# AI makes a move
# def ai_make_move():
#     global message, message_timer, ai_thinking, waiting_for_color_choice, current_card
    
#     # Safety check - only make a move if it's actually Player 2's turn
#     if current_player != "Player2":
#         message = "Error: AI tried to play during Player 1's turn!"
#         message_timer = 120
#         ai_thinking = False
#         return

#     # Reset AI thinking flag
#     ai_thinking = False
    
#     # If waiting for color choice, select a color
#     if waiting_for_color_choice:
#         color = ai_bot.choose_color()
#         message = f"AI chooses {color}"
#         message_timer = 120
#         set_card_color(color)
#         return
    
#     # Find best card to play using minimax
#     best_card_idx = ai_bot.find_best_move(player_hands["Player2"])
    
#     if best_card_idx is not None:
#         # Play the best card
#         card = player_hands["Player2"][best_card_idx]
#         message = f"AI plays {card['color']} {card['label']}"
#         message_timer = 120
#         play_card(best_card_idx)
#     else:
#         # Draw a card if no playable cards
#         message = "AI draws a card"
#         message_timer = 120
#         draw_from_deck()

# AI makes a move - simplified and with more debugging
def ai_make_move():
    global message, message_timer, ai_thinking, waiting_for_color_choice, current_card
    
    # Reset AI thinking flag
    ai_thinking = False
    
    # Debug message
    print(f"AI making move. Current player: {current_player}, Waiting for color: {waiting_for_color_choice}")
    
    # Safety check - only make a move if it's actually Player 2's turn
    if current_player != "Player2":
        message = f"Error: AI tried to play during {current_player}'s turn!"
        message_timer = 120
        print(message)
        return
    
    # If waiting for color choice, select a color
    if waiting_for_color_choice:
        color = ai_bot.choose_color()
        message = f"AI chooses {color}"
        message_timer = 120
        set_card_color(color)
        print(f"AI chose color: {color}")
        return
    
    # Find best card to play
    if len(player_hands["Player2"]) > 0:
        best_card_idx = ai_bot.find_best_move(player_hands["Player2"])
        
        if best_card_idx is not None:
            # Play the best card
            card = player_hands["Player2"][best_card_idx]
            message = f"AI plays {card['color']} {card['label']}"
            message_timer = 120
            print(f"AI playing card: {card['color']} {card['label']}")
            play_card(best_card_idx)
        else:
            # Draw a card if no playable cards
            message = "AI draws a card"
            message_timer = 120
            print("AI drawing card (no playable cards)")
            draw_from_deck()
    else:
        message = "AI has no cards!"
        message_timer = 120
        print("AI has no cards!")

# Game loop
running = True
clock = pygame.time.Clock()
selected_card = -1

while running:
    screen.fill(COLORS["Background"])
    
    # Define board area
    board_y_offset = 70  # Padding from the top
    
    # Draw title
    title = title_font.render("UNO Game Board", True, (30, 30, 100))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 10))
    
    # Draw current player indicator
    player_text = index_font.render(f"Current Turn: {current_player}", True, PLAYER_COLORS[current_player])
    screen.blit(player_text, (20, 10))
    
    # Draw board background
    pygame.draw.rect(screen, (220, 220, 240), 
                    (0, board_y_offset, WIDTH, BOARD_HEIGHT), 
                    border_radius=5)
    
    # Draw border around the board
    pygame.draw.rect(screen, COLORS["BoardBorder"], 
                    (0, board_y_offset, WIDTH, BOARD_HEIGHT), 
                    4, border_radius=5)

    # Drawing the board cells
    for row in range(ROWS):
        for col in range(COLS):
            color_name, color_val = color_grid[row][col]
            rect_x = col * CELL_WIDTH
            rect_y = row * CELL_HEIGHT + board_y_offset
            
            # Cell with rounded corners
            pygame.draw.rect(screen, color_val, 
                           (rect_x + 2, rect_y + 2, CELL_WIDTH - 4, CELL_HEIGHT - 4),
                           border_radius=5)
            
            # Cell index and color name
            name = small_font.render(color_name, True, (0, 0, 0))
            idx = index_font.render(str(index_grid[row][col]), True, (0, 0, 0))
            
            screen.blit(name, name.get_rect(center=(rect_x + CELL_WIDTH // 2, rect_y + CELL_HEIGHT // 2 + 10)))
            screen.blit(idx, (rect_x + 8, rect_y + 8))

    # Draw grid lines
    for i in range(1, COLS):
        pygame.draw.line(screen, COLORS["GridLine"], 
                      (i * CELL_WIDTH, board_y_offset), 
                      (i * CELL_WIDTH, BOARD_HEIGHT + board_y_offset), 2)
    for i in range(1, ROWS):
        pygame.draw.line(screen, COLORS["GridLine"], 
                      (0, i * CELL_HEIGHT + board_y_offset), 
                      (WIDTH, i * CELL_HEIGHT + board_y_offset), 2)

    # Group players by position to handle overlapping
    positions = {}
    for player in active_players:
        row, col = players[player]["target_pos"]
        pos_key = (row, col)
        if pos_key not in positions:
            positions[pos_key] = []
        positions[pos_key].append(player)
    
    # Draw players with appropriate offsets
    for pos, player_list in positions.items():
        row, col = pos
        offsets = get_player_offsets(len(player_list))
        for i, player in enumerate(player_list):
            draw_player(player, row, col, offsets[i])

    # Player hand area
    hand_bg_y = BOARD_HEIGHT + board_y_offset + 20
    hand_bg_height = HEIGHT - hand_bg_y - 20
    
    # Redistribute space for hand area, current card, and draw deck
    hand_width = WIDTH * 0.65  # Reduced to make room for deck
    card_area_width = WIDTH * 0.20
    deck_area_width = WIDTH * 0.15
    
    # Player hand background
    pygame.draw.rect(screen, (220, 220, 230), 
                   (20, hand_bg_y, hand_width - 30, hand_bg_height), 
                   border_radius=10)
    
    # Player hand label
    hand_label = index_font.render(f"{current_player}'s Hand", True, (0, 0, 0))
    screen.blit(hand_label, (hand_width/2 - hand_label.get_width()/2, hand_bg_y + 10))
    
    # Player hand cards
    hand_y = hand_bg_y + 40
    current_hand = player_hands[current_player]
    card_spacing = min(90, (hand_width - 100) // max(len(current_hand), 1)) if current_hand else 90
    start_x = ((hand_width - 10) - ((len(current_hand) - 1) * card_spacing + 84)) // 2 if current_hand else (hand_width - 10) // 2 - 42
    
    card_rects = []
    for i, card in enumerate(current_hand):
        is_selected = (i == selected_card)
        is_playable = can_play_card(card)
        card_rect = draw_card(start_x + i * card_spacing, hand_y, card["color"], card["label"], 
                             selected=is_selected, clickable=is_playable)
        card_rects.append(card_rect)
    
    # Current card panel
    current_card_x = hand_width
    current_card_y = hand_bg_y
    
    # Draw the current card panel
    pygame.draw.rect(screen, (220, 220, 230), 
                   (current_card_x, current_card_y, card_area_width - 10, hand_bg_height), 
                   border_radius=10)
    
    # Current card label
    label = index_font.render("Current Card", True, (0, 0, 0))
    label_x = current_card_x + (card_area_width - 10) / 2 - label.get_width() / 2
    screen.blit(label, (label_x, hand_bg_y + 10))
    
    # Draw deck panel
    deck_x = hand_width + card_area_width - 10
    deck_y = hand_bg_y
    pygame.draw.rect(screen, (220, 220, 230), 
                   (deck_x, deck_y, deck_area_width - 10, hand_bg_height), 
                   border_radius=10)
    
    # Deck label
    deck_label = index_font.render("Draw Deck", True, (0, 0, 0))
    deck_label_x = deck_x + (deck_area_width - 10) / 2 - deck_label.get_width() / 2
    screen.blit(deck_label, (deck_label_x, hand_bg_y + 10))
    
    # Draw the draw deck
    deck_rect = draw_deck(deck_x + (deck_area_width - 10) / 2 - 42, hand_y, clickable=True)
    
    # Draw the current card (with animation if active)
    if move_animation and time.time() - animation_start_time < animation_duration:
        # Calculate animation progress (0 to 1)
        progress = (time.time() - animation_start_time) / animation_duration
        
        # Start position (from hand)
        start_x = WIDTH // 2
        start_y = hand_y
        
        # End position (current card position)
        end_x = current_card_x + (card_area_width - 10) / 2 - 42
        end_y = hand_y
        
        # Calculate current position
        anim_x = start_x + (end_x - start_x) * progress
        anim_y = start_y - 50 * math.sin(math.pi * progress)  # Arc motion
        
        # Draw the animating card
        draw_card(anim_x, anim_y, animation_card["color"], animation_card["label"])
        
        # Check if animation is done
        if progress >= 1.0:
            move_animation = False
    else:
        # Draw the regular current card
        card_x = current_card_x + (card_area_width - 10) / 2 - 42  # Center the card
        draw_card(card_x, hand_y, current_card["color"], current_card["label"])
    
    # Display color selection if waiting for choice
    if waiting_for_color_choice:
        color_buttons = draw_color_selection()
    
    # Display message if timer is active
    if message_timer > 0:
        message_timer -= 1
        message_surface = message_font.render(message, True, (30, 30, 100))
        message_rect = message_surface.get_rect(center=(WIDTH // 2, board_y_offset // 2 + 35))
        # Add semi-transparent background
        msg_bg = pygame.Rect(message_rect)
        msg_bg.inflate_ip(20, 10)
        pygame.draw.rect(screen, (255, 255, 255, 150), msg_bg, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 150), msg_bg, 2, border_radius=10)
        screen.blit(message_surface, message_rect)

    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if waiting for color selection
            if waiting_for_color_choice:
                for button_rect, color in color_buttons:
                    if button_rect.collidepoint(event.pos):
                        set_card_color(color)
                        break
            else:
                # Only process clicks if it's Player1's turn and AI is not thinking
                if current_player == "Player1" and not ai_thinking:
                    # Check if player clicked on a card in their hand
                    for i, card_rect in enumerate(card_rects):
                        if card_rect.collidepoint(event.pos):
                            # Try to play the card
                            if can_play_card(current_hand[i]):
                                play_card(i)
                            else:
                                selected_card = i
                                message = "Can't play that card!"
                                message_timer = 60
                            break
                    
                    # Check if player clicked on the draw deck
                    if deck_rect.collidepoint(event.pos) and len(deck) > 0:
                        draw_from_deck()
        
        elif event.type == pygame.KEYDOWN:
            # Manual controls for testing
            if event.key == pygame.K_SPACE:
                if current_player == "Player1" and selected_card >= 0 and selected_card < len(current_hand):
                    play_card(selected_card)
                    selected_card = -1
            
            elif event.key == pygame.K_LEFT:
                if current_player == "Player1" and len(current_hand) > 0:
                    selected_card = max(selected_card - 1, 0) if selected_card > 0 else len(current_hand) - 1
            
            elif event.key == pygame.K_RIGHT:
                if current_player == "Player1" and len(current_hand) > 0:
                    selected_card = (selected_card + 1) % len(current_hand)
            
            # Test draws
            elif event.key == pygame.K_d:
                if current_player == "Player1":
                    draw_from_deck()
            
            # Switch player for testing
            elif event.key == pygame.K_TAB:
                advance_turn()
                message = f"{current_player}'s turn"
                message_timer = 60
            
            # Escape to quit
            elif event.key == pygame.K_ESCAPE:
                running = False

    # If it's Player2's turn and not waiting for color choice, let AI make a move
    # if current_player == "Player2" and not waiting_for_color_choice and not move_animation:
    #     if not ai_thinking:
    #         # Set AI thinking flag and start timer
    #         ai_thinking = True
    #         ai_move_time = time.time()
    #         message = "AI is thinking..."
    #         message_timer = 120
    #     elif ai_thinking and time.time() - ai_move_time >= 2.0:  # 2 second delay
    #         # Make the move after the delay
    #         ai_make_move()

    # If it's Player2's turn and not waiting for color choice, let AI make a move
    if current_player == "Player2" and not move_animation:
        if not ai_thinking:
            # Set AI thinking flag and start timer
            ai_thinking = True
            ai_move_time = time.time()
            message = "AI is thinking..."
            message_timer = 120
            print("AI started thinking")
        elif ai_thinking and time.time() - ai_move_time >= 2.0:  # 2 second delay
            # Make the move after the delay
            print("AI ready to make move after delay")
            ai_make_move()

    pygame.display.flip()
    clock.tick(60)  # 60 FPS

pygame.quit()
