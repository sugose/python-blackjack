# Technical Product Specification — python-blackjack

## 1. System Overview

python-blackjack is a blackjack simulator written in Python. It models the card game Blackjack, allowing developers to simulate games, test strategies, and observe outcomes. The simulator is headless — no UI, no user input — driven entirely by code and testable end-to-end with pytest.

---

## 2. Architecture

### Modules

| Module | Responsibility |
|---|---|
| `src/cards.py` | Card and Deck — the building blocks of the game |
| `src/hand.py` | Hand — a collection of cards with a calculated value |
| `src/deal.py` | Deal logic — shuffling and dealing the opening hand |

### Data Flow

Deck (52 cards) → shuffle → deal_initial() → Player Hand (2 cards, both visible) + Dealer Hand (2 cards, 1 visible, 1 hidden)

---

## 3. Component Specifications

### Card

Represents a single playing card.

- Has a rank: 2–10, Jack, Queen, King, Ace
- Has a suit: Hearts, Diamonds, Clubs, Spades
- Has a numeric value: 2–10 = face value; Jack/Queen/King = 10; Ace = 11 or 1 (whichever keeps the hand from busting)
- Is immutable — a card does not change once created

### Deck

Represents a standard 52-card deck.

- Contains exactly one of each card (13 ranks × 4 suits)
- Can be shuffled (random order, seeded for testing)
- Cards are dealt one at a time from the top
- Raises an error if asked to deal from an empty deck

### Hand

Represents a collection of cards held by a player or dealer.

- Holds one or more cards
- Calculates its total value, handling Ace as 11 or 1 to avoid bust where possible
- Knows whether it is a blackjack (exactly 21 with 2 cards)
- Knows whether it is bust (value exceeds 21)

### deal_initial()

Deals the opening hand of a round.

- Takes a shuffled deck as input
- Returns a player hand (2 visible cards) and a dealer hand (1 visible card, 1 hidden card)
- Does not modify game state beyond removing 4 cards from the deck

---

## 4. Error Handling

- Dealing from an empty deck raises a descriptive exception
- All errors are raised explicitly — no silent failures

---

## 5. Known Unknowns

- Shuffling algorithm: standard random.shuffle for now; may need seeding strategy for reproducible simulations
- Multiple decks (shoe): not in scope yet
- Splitting, doubling down, insurance: not in scope yet
