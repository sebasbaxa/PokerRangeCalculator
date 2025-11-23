from .objects import Card
import random
from itertools import combinations
from collections import Counter
from typing import List, Tuple

SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
RANKS = list(range(2, 15))


def _card_key(card: Card) -> tuple:
    return (card.suit, card.rank)


def _clone_card(card: Card) -> Card:
    return Card(card.suit, card.rank)


def _normalize_card(card) -> Card:
    if isinstance(card, Card):
        return _clone_card(card)
    if isinstance(card, dict):
        return Card(card['suit'], card['rank'])
    raise ValueError(f"Unsupported card representation: {card}")


def _is_straight(ranks: List[int]) -> Tuple[bool, int]:
    unique = sorted(set(ranks), reverse=True)
    # Handle wheel straight (A,5,4,3,2)
    if 14 in unique:
        unique.append(1)
    for i in range(len(unique) - 4):
        window = unique[i:i + 5]
        if window[0] - window[4] == 4:
            return True, max(window)
    return False, 0


def _evaluate_five(cards) -> Tuple[int, List[int]]:
    ranks = [card.rank for card in cards]
    suits = [card.suit for card in cards]
    rank_counter = Counter(ranks)
    counts = sorted(rank_counter.values(), reverse=True)
    ordered_ranks = sorted(rank_counter.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

    is_flush = len(set(suits)) == 1
    straight, straight_high = _is_straight(ranks)

    # Straight flush
    if is_flush and straight:
        return (8, [straight_high])

    # Four of a kind
    if counts == [4, 1]:
        quad_rank = ordered_ranks[0][0]
        kicker = max([r for r in ranks if r != quad_rank])
        return (7, [quad_rank, kicker])

    # Full house
    if counts == [3, 2]:
        trips_rank = ordered_ranks[0][0]
        pair_rank = ordered_ranks[1][0]
        return (6, [trips_rank, pair_rank])

    # Flush
    if is_flush:
        return (5, sorted(ranks, reverse=True))

    # Straight
    if straight:
        return (4, [straight_high])

    # Three of a kind
    if counts == [3, 1, 1]:
        trips_rank = ordered_ranks[0][0]
        kickers = sorted([r for r in ranks if r != trips_rank], reverse=True)
        return (3, [trips_rank] + kickers)

    # Two pair
    if counts == [2, 2, 1]:
        pair_ranks = sorted([r for r, c in rank_counter.items() if c == 2], reverse=True)
        kicker = max([r for r in ranks if r not in pair_ranks])
        return (2, pair_ranks + [kicker])

    # One pair
    if counts == [2, 1, 1, 1]:
        pair_rank = ordered_ranks[0][0]
        kickers = sorted([r for r in ranks if r != pair_rank], reverse=True)
        return (1, [pair_rank] + kickers)

    # High card
    return (0, sorted(ranks, reverse=True))


def _evaluate_seven(cards) -> Tuple[int, List[int]]:
    best = None
    for combo in combinations(cards, 5):
        value = _evaluate_five(combo)
        if best is None or value > best:
            best = value
    if best is None:
        raise ValueError("Unable to evaluate hand with fewer than five cards")
    return best

class RunSimulations:
    def __init__(self, hero_range, villain_range, board, num_simulations):
        self.hero_range = hero_range
        self.villain_range = villain_range
        self.num_simulations = num_simulations
        self.base_board = []
        for card in board or []:
            self.base_board.append(_normalize_card(card))

        if len(self.base_board) > 5:
            raise ValueError("Board cannot contain more than five cards")

        board_keys = {_card_key(card) for card in self.base_board}
        if len(board_keys) != len(self.base_board):
            raise ValueError("Board contains duplicate cards")

    def run(self):
        """Run simulations and return (hero_win_rate, villain_win_rate, split_rate)."""
        if not self.hero_range.card_range or not self.villain_range.card_range:
            return (0.0, 0.0, 0.0)

        hero_wins = 0
        villain_wins = 0
        splits = 0

        completed = 0
        attempts = 0
        # Avoid infinite retries when ranges contain conflicting hands
        max_attempts = max(self.num_simulations * 10, 100)

        base_board_keys = {_card_key(card) for card in self.base_board}

        while completed < self.num_simulations and attempts < max_attempts:
            attempts += 1

            hero_hand = random.choice(self.hero_range.card_range)
            villain_hand = random.choice(self.villain_range.card_range)

            hero_cards = [_clone_card(hero_hand.card1), _clone_card(hero_hand.card2)]
            villain_cards = [_clone_card(villain_hand.card1), _clone_card(villain_hand.card2)]

            used = set(base_board_keys)
            conflict = False

            for card in hero_cards + villain_cards:
                key = _card_key(card)
                if key in used:
                    conflict = True
                    break
                used.add(key)

            if conflict:
                continue

            available_cards = [
                Card(suit, rank)
                for suit in SUITS
                for rank in RANKS
                if (suit, rank) not in used
            ]

            board_cards = [_clone_card(card) for card in self.base_board]
            cards_needed = 5 - len(board_cards)

            if cards_needed > 0:
                random.shuffle(available_cards)
                drawn = available_cards[:cards_needed]
                if len(drawn) < cards_needed:
                    continue
                board_cards.extend(drawn)

            hero_eval_cards = hero_cards + board_cards
            villain_eval_cards = villain_cards + board_cards

            hero_value = _evaluate_seven(hero_eval_cards)
            villain_value = _evaluate_seven(villain_eval_cards)

            if hero_value > villain_value:
                hero_wins += 1
            elif villain_value > hero_value:
                villain_wins += 1
            else:
                splits += 1

            completed += 1

        if completed == 0:
            return (0.0, 0.0, 0.0)

        return (
            hero_wins / completed,
            villain_wins / completed,
            splits / completed
        )