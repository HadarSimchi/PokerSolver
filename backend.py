from flask import Flask, request, jsonify
import itertools
import random
from collections import Counter

app = Flask(__name__)

# Define card ranks and suits
RANKS = "23456789TJQKA"
SUITS = "cdhs"

# Generate a standard 52-card deck
def generate_deck():
    return [rank + suit for rank in RANKS for suit in SUITS]

# Hand ranking function
def hand_rank(hand):
    ranks = sorted([RANKS.index(card[0]) for card in hand], reverse=True)
    rank_counts = Counter(ranks)
    suits = [card[1] for card in hand]
    
    is_flush = len(set(suits)) == 1
    is_straight = len(rank_counts) == 5 and (max(ranks) - min(ranks) == 4)
    
    if is_flush and is_straight:
        return (8, max(ranks))  # Straight Flush
    if 4 in rank_counts.values():
        return (7, ranks)  # Four of a Kind
    if sorted(rank_counts.values()) == [2, 3]:
        return (6, ranks)  # Full House
    if is_flush:
        return (5, ranks)  # Flush
    if is_straight:
        return (4, max(ranks))  # Straight
    if 3 in rank_counts.values():
        return (3, ranks)  # Three of a Kind
    if list(rank_counts.values()).count(2) == 2:
        return (2, ranks)  # Two Pair
    if 2 in rank_counts.values():
        return (1, ranks)  # One Pair
    return (0, ranks)  # High Card

# Monte Carlo equity calculation
def simulate_equity(hands, board=None, num_simulations=100000):  # Increased simulations for accuracy
    deck = generate_deck()
    for hand in hands:
        for card in hand:
            deck.remove(card)
    if board:
        for card in board:
            deck.remove(card)
    
    wins = [0] * len(hands)
    ties = 0
    
    for _ in range(num_simulations):
        remaining_board = random.sample(deck, 5 - len(board) if board else 5)
        full_board = board + remaining_board if board else remaining_board
        
        ranked_hands = [hand_rank(hand + full_board) for hand in hands]
        best_rank = max(ranked_hands)
        best_count = ranked_hands.count(best_rank)
        
        if best_count == 1:
            wins[ranked_hands.index(best_rank)] += 1
        else:
            ties += 1
    
    return {f"Hand {i+1} Equity": round(wins[i] / num_simulations * 100, 2) for i in range(len(hands))}, {"Tie": round(ties / num_simulations * 100, 2)}

@app.route("/api/calculate-equity", methods=["POST"])
def calculate_equity():
    data = request.json
    hands = [hand.strip().split() for hand in data.get("hands", "").split(",")]
    board = data.get("board", "").split()
    bet_sizing = data.get("betSizing", "")
    
    equity_results, tie_results = simulate_equity(hands, board)
    
    return jsonify({"equity": equity_results, "tie": tie_results, "bet_sizing": bet_sizing})

if __name__ == "__main__":
    app.run(debug=True)
