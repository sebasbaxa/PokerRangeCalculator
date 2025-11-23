from collections import defaultdict
from .objects import *

class utils:

    def find_straight_flush(self, cards):

        # Group cards by suit
        suits = defaultdict(list)
        for card in cards:
            suits[card.suit].append(card)

        # Check each suit for a straight flush
        for suit, suited_cards in suits.items():
            if len(suited_cards) < 5:
                continue

            # Sort cards by rank
            suited_cards.sort(key=lambda x: x.rank)

            # Add Ace as rank 1 if it exists
            if suited_cards[-1].rank == 14:
                suited_cards.append(Card(suited_cards[-1].suit, 1))

            # Check for straight flush
            for i in range(len(suited_cards) - 5, -1, -1):
                if (suited_cards[i].rank + 1 == suited_cards[i + 1].rank and
                    suited_cards[i].rank + 2 == suited_cards[i + 2].rank and
                    suited_cards[i].rank + 3 == suited_cards[i + 3].rank and
                    suited_cards[i].rank + 4 == suited_cards[i + 4].rank):
                    return suited_cards[i:i+5]

        return None

    def find_four_of_a_kind(self, cards):

        # Group cards by rank
        ranks = defaultdict(list)
        for card in cards:
            ranks[card.rank].append(card)

        # Check for four of a kind
        for rank, rank_cards in ranks.items():
            if len(rank_cards) == 4:
                return rank_cards

        return None

    def find_full_house(self, cards):

        # Group cards by rank
        ranks = defaultdict(list)
        for card in cards:
            ranks[card.rank].append(card)

        # Check for three of a kind
        highest_three = 0
        for rank, rank_cards in ranks.items():
            if len(rank_cards) == 3:
                if rank > highest_three:
                    highest_three = rank
        if highest_three == 0:
            return None
        three_of_a_kind = ranks[highest_three]

        if three_of_a_kind is None:
            return None

        # Check for a pair
        highest_pair = 0
        for rank, rank_cards in ranks.items():
            if len(rank_cards) >= 2 and rank_cards[0] != three_of_a_kind[0]:
                if rank > highest_pair:
                    highest_pair = rank
        if highest_pair == 0:
            return None
        pair = ranks[highest_pair]
        return three_of_a_kind + pair[:2]
        
    def find_flush(self, cards):

        # Group by suits
        suits = defaultdict(list)
        for card in cards:
            suits[card.suit].append(card)
        for suits, suited_cards in suits.items():
            if len(suited_cards) >= 5:
                suited_cards.sort(key=lambda x: x.rank)
                return suited_cards[-5:]

    def find_straight(self, cards):

        # Sort cards by rank
        cards.sort(key=lambda x: x.rank)

        # Add Ace as rank 1 if it exists
        if cards[-1].rank == 14:
            cards.append(Card(cards[-1].suit, 1))

        # Check for straight
        for i in range(len(cards) - 5, -1, -1):
            if (cards[i].rank + 1 == cards[i + 1].rank and
                cards[i].rank + 2 == cards[i + 2].rank and
                cards[i].rank + 3 == cards[i + 3].rank and
                cards[i].rank + 4 == cards[i + 4].rank):
                return cards[i:i+5]

        return None

    def find_three_of_a_kind(self, cards):

        # Group cards by rank
        ranks = defaultdict(list)
        for card in cards:
            ranks[card.rank].append(card)

        # Check for three of a kind
        highest_rank = 0
        for rank, rank_cards in ranks.items():
            if len(rank_cards) == 3 and rank > highest_rank:
                highest_rank = rank
        if highest_rank != 0:
            # Collect remaining cards that are not part of the three of a kind
            remaining_cards = [card for card in cards if card.rank != highest_rank]
            remaining_cards.sort(key=lambda x: x.rank, reverse=True)
            return ranks[highest_rank] + remaining_cards[:2]

        return None

    def find_two_pair(self, cards):
        
        # Group cards by rank
        ranks = defaultdict(list)
        for card in cards:
            ranks[card.rank].append(card)

        # Check for two pairs
        kicker = 0
        card = None
        pairs = []
        for rank, rank_cards in ranks.items():
            if len(rank_cards) >= 2:
                pairs.append(rank_cards)
            else:
                if rank > kicker:
                    kicker = rank
                    card = rank_cards[0]
        if len(pairs) >= 2:
            pairs.sort(key=lambda x: x[0].rank, reverse=True)
            return pairs[0] + pairs[1] + [card]

        return None

    def find_pair(self, cards):
        
        # Group cards by rank
        ranks = defaultdict(list)
        for card in cards:
            ranks[card.rank].append(card)

        # Check for a pair and get the top three cards
        top_rank = 0
        for rank, rank_cards in ranks.items():
            if len(rank_cards) == 2 and rank > top_rank:
                top_rank = rank
        top_pair = ranks[top_rank] 
        if top_pair:
             # Collect remaining cards that are not part of the pair
            remaining_cards = [card for card in cards if card.rank != top_rank]
            remaining_cards.sort(key=lambda x: x.rank, reverse=True)
            top_three_remaining = remaining_cards[:3]
            return top_pair + top_three_remaining
        return None

    def find_high_card(self, cards):
        cards.sort(key=lambda x: x.rank, reverse=True)
        return cards[:5]

    def find_best_hand(self, cards):

        # Check for straight flush
        straight_flush = self.find_straight_flush(cards)
        if straight_flush:
            return 9, straight_flush

        # Check for four of a kind
        four_of_a_kind = self.find_four_of_a_kind(cards)
        if four_of_a_kind:
            return 8, four_of_a_kind

        # Check for full house
        full_house = self.find_full_house(cards)
        if full_house:
            return 7, full_house

        # Check for flush
        flush = self.find_flush(cards)
        if flush:
            return 6, flush

        # Check for straight
        straight = self.find_straight(cards)
        if straight:
            return 5, straight

        # Check for three of a kind
        three_of_a_kind = self.find_three_of_a_kind(cards)
        if three_of_a_kind:
            return 4, three_of_a_kind

        # Check for two pair
        two_pair = self.find_two_pair(cards)
        if two_pair:
            return 3, two_pair

        # Check for pair
        pair = self.find_pair(cards)
        if pair:
            return 2, pair

        # High card
        high_card = self.find_high_card(cards)
        return 1, high_card

    def compare_combos(self, hand1, hand2):

        hand1_type = hand1[0]
        hand2_type = hand2[0]
        best_hand1 = hand1[1]
        best_hand2 = hand2[1]
        if hand1_type > hand2_type:
            return 1
        elif hand1_type < hand2_type:
            return -1
        else:
            for card1, card2 in zip(best_hand1, best_hand2):
                if card1.rank > card2.rank:
                    return 1
                elif card1.rank < card2.rank:
                    return -1
        return 0

    def display_best_hand(self, cards):
        hand_type, best_hand = self.find_best_hand(cards)
        print(hand_type)
        for card in best_hand:
            print(str(card))

class MakeRange:
    """Generate all possible hand combinations for a given hand type"""
    
    def pocket_pair(self, rank):
        """Generate all 6 combinations of a pocket pair"""
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        hands = []
        for i in range(len(suits)):
            for j in range(i + 1, len(suits)):
                c1 = Card(suits[i], rank)
                c2 = Card(suits[j], rank)
                hands.append(Hand(c1, c2))
        return hands
    
    def suited_hand(self, rank1, rank2):
        """Generate all 4 suited combinations"""
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        hands = []
        for suit in suits:
            c1 = Card(suit, rank1)
            c2 = Card(suit, rank2)
            hands.append(Hand(c1, c2))
        return hands
    
    def offsuit_hand(self, rank1, rank2):
        """Generate all 12 offsuit combinations"""
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        hands = []
        for s1 in suits:
            for s2 in suits:
                if s1 != s2:
                    c1 = Card(s1, rank1)
                    c2 = Card(s2, rank2)
                    hands.append(Hand(c1, c2))
        return hands