import pygame
import random
import math
import time
import copy
from cards import generate_uno_deck

# AI Bot Class - Simplified to ensure it works
class MinimaxAIBot:
    def __init__(self, player_name="Player2"):
        self.player_name = player_name
        self.thinking = False
        self.last_move_time = 0
        self.thinking_delay = 2.0  # 2 seconds delay for thinking animation
        self.max_depth = 3  # Maximum depth for minimax search
    
    def start_thinking(self):
        """Start the thinking process and set the thinking flag"""
        self.thinking = True
        self.last_move_time = time.time()
        return "AI is thinking..."
    
    def is_ready_to_move(self):
        """Check if the AI is ready to make a move after thinking"""
        return self.thinking and (time.time() - self.last_move_time >= self.thinking_delay)
    
    def find_best_move(self, player_hand):
        """Find the best move using minimax with alpha-beta pruning"""
        # Find playable cards
        playable_cards = []
        for i, card in enumerate(player_hand):
            if can_play_card(card):
                playable_cards.append((i, card))
        
        if not playable_cards:
            return None  # No playable cards, need to draw
        
        # Use minimax with alpha-beta pruning to find the best move
        best_score = float('-inf')
        best_move = None
        
        # Create a copy of the game state for simulation
        game_state = self._create_game_state()
        
        for idx, card in playable_cards:
            # Simulate playing this card
            new_state = self._simulate_play_card(game_state, card, True)
            score = self._minimax(new_state, 1, False, float('-inf'), float('inf'))
            
            if score > best_score:
                best_score = score
                best_move = idx
        
        return best_move
    
    def _create_game_state(self):
        """Create a simplified copy of the current game state"""
        state = {
            'players': copy.deepcopy(players),
            'player_hands': {p: player_hands[p].copy() for p in active_players},
            'current_card': current_card.copy(),
            'current_player_idx': current_player_idx,
            'deck_size': len(deck)
        }
        return state
    
    def _minimax(self, state, depth, is_maximizing, alpha, beta):
        """
        Minimax algorithm with alpha-beta pruning
        
        Parameters:
        - state: Current game state
        - depth: Current depth in the search tree
        - is_maximizing: True if maximizing player's turn, False otherwise
        - alpha: Alpha value for pruning
        - beta: Beta value for pruning
        
        Returns:
        - Score of the best move
        """
        # Terminal conditions
        if depth >= self.max_depth or self._is_game_over(state):
            return self._evaluate_state(state)
        
        # Get current player
        current_p = "Player2" if is_maximizing else "Player1"
        
        # Get playable cards for the current player
        playable_cards = []
        for card in state['player_hands'][current_p]:
            if self._can_play_card(card, state['current_card']):
                playable_cards.append(card)
        
        # If no playable cards, simulate drawing
        if not playable_cards:
            # In a real implementation, we would simulate drawing and continue
            # For simplicity, we'll use a moderate score
            return 0 if is_maximizing else 50
        
        if is_maximizing:
            max_eval = float('-inf')
            for card in playable_cards:
                new_state = self._simulate_play_card(state, card, is_maximizing)
                eval = self._minimax(new_state, depth + 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = float('inf')
            for card in playable_cards:
                new_state = self._simulate_play_card(state, card, is_maximizing)
                eval = self._minimax(new_state, depth + 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval
    
    def _simulate_play_card(self, state, card, is_maximizing):
        """Simulate playing a card and return the resulting state"""
        # Create a deep copy of the state to modify
        new_state = copy.deepcopy(state)
        
        # Determine which player is playing
        player = "Player2" if is_maximizing else "Player1"
        
        # Remove card from hand
        if card in new_state['player_hands'][player]:
            new_state['player_hands'][player].remove(card)
        
        # Update current card
        new_state['current_card'] = card.copy()
        
        # Apply card effects based on its label
        if card["label"].isdigit():
            # Move player forward
            steps = int(card["label"])
            new_state['players'][player]["pos"] += steps
        elif card["label"] == "Skip" or card["label"] == "Reverse":
            # Skip opponent's turn (in this game both have the same effect)
            opponent = "Player1" if is_maximizing else "Player2"
            new_state['players'][opponent]["skip_turn"] = True
        elif card["label"].startswith("Draw"):
            # Move opponent backward
            opponent = "Player1" if is_maximizing else "Player2"
            draw_count = int(card["label"].split()[1])
            new_state['players'][opponent]["pos"] = max(1, new_state['players'][opponent]["pos"] - draw_count)
            
            # For non-black Draw cards, also simulate opponent drawing cards
            if card["color"] != "Black" and new_state['deck_size'] > 0:
                new_state['deck_size'] -= min(draw_count, new_state['deck_size'])
                # We don't actually need to add cards to the hand in simulation
        
        # Update positions, ensuring they stay within bounds
        for p in new_state['players']:
            pos = new_state['players'][p]["pos"]
            pos = max(1, min(pos, ROWS * COLS))
            new_state['players'][p]["pos"] = pos
            
            # Update target position for visualization
            row, col = 0, 0  # This is just a placeholder in simulation
            new_state['players'][p]["target_pos"] = (row, col)
        
        return new_state
    
    def _can_play_card(self, card, current):
        """Check if a card can be played on the current card"""
        # Black cards can be played on anything
        if card["color"] == "Black":
            return True
        
        # Same color or same label
        if card["color"] == current["color"] or card["label"] == current["label"]:
            return True
        
        # Current card is black (any card can be played)
        if current["color"] == "Black":
            return True
        
        return False
    
    def _is_game_over(self, state):
        """Check if the game is over in the current state"""
        # Check if any player has reached the end or has no cards
        for player in ["Player1", "Player2"]:
            if state['players'][player]["pos"] >= ROWS * COLS:
                return True
            if len(state['player_hands'][player]) == 0:
                return True
        return False
    
    def _evaluate_state(self, state):
        """
        Evaluate the game state from AI's perspective
        A higher score means a better position for the AI
        """
        # Get positions
        ai_pos = state['players']["Player2"]["pos"]
        human_pos = state['players']["Player1"]["pos"]
        
        # Position difference (higher is better for AI)
        position_score = ai_pos - human_pos
        
        # Card advantage (fewer cards is better)
        ai_cards = len(state['player_hands']["Player2"])
        human_cards = len(state['player_hands']["Player1"]) if "Player1" in state['player_hands'] else 0
        card_score = human_cards - ai_cards
        
        # Distance to goal
        ai_distance = ROWS * COLS - ai_pos
        human_distance = ROWS * COLS - human_pos
        distance_score = human_distance - ai_distance
        
        # Special cards in hand are valuable
        special_card_score = 0
        for card in state['player_hands']["Player2"]:
            if card["label"] == "Skip" or card["label"] == "Reverse":
                special_card_score += 5
            elif card["label"].startswith("Draw"):
                special_card_score += 10
            elif card["color"] == "Black":
                special_card_score += 15
        
        # Win/loss states
        if ai_pos >= ROWS * COLS:
            return 1000  # AI wins
        if human_pos >= ROWS * COLS:
            return -1000  # Human wins
        
        # Combine all factors with appropriate weights
        total_score = (
            position_score * 3 + 
            card_score * 2 + 
            distance_score * 5 + 
            special_card_score
        )
        
        return total_score
    
    def choose_color(self):
        """Choose the best color after playing a black card"""
        # Count colors in hand
        color_counts = {"Red": 0, "Blue": 0, "Green": 0, "Yellow": 0}
        for card in player_hands[self.player_name]:
            if card["color"] in color_counts:
                color_counts[card["color"]] += 1
        
        # Choose most common color
        best_color = max(color_counts.items(), key=lambda x: x[1])[0] if any(color_counts.values()) else "Red"
        return best_color
# Create AI bot instance
# Replace the existing AIBot class with MinimaxAIBot

# Initialize the AI bot with MinimaxAIBot
