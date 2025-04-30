# cards.py
import random

def generate_uno_deck():
    colors = ["Red", "Green", "Blue", "Yellow"]
    deck = []

    for color in colors:
        # Numbered cards 0–9 (two of each except 0)
        deck.append({"color": color, "label": "0"})
        for num in range(1, 10):
            deck.extend([{"color": color, "label": str(num)}] * 2)

        # Action cards
        for action in ["Skip", "Reverse", "Draw 2"]:
            deck.extend([{"color": color, "label": action}] * 2)

    # Wilds
    for _ in range(4):
        deck.append({"color": "Black", "label": "Draw 2"})
        deck.append({"color": "Black", "label": "Draw 4"})
    for _ in range(2):
            deck.append({"color": "Black", "label": "Draw 10"})
    return deck

if __name__ == "__main__":
    deck = generate_uno_deck()
    random.shuffle(deck)
    print(deck)
