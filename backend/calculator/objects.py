class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    
    def __repr__(self):
        rank_map = {14: 'A', 13: 'K', 12: 'Q', 11: 'J', 10: 'T',
                    9: '9', 8: '8', 7: '7', 6: '6', 5: '5',
                    4: '4', 3: '3', 2: '2'}
        return f"{rank_map.get(self.rank, self.rank)}{self.suit[0].upper()}"
    
    def to_dict(self):
        return {"suit": self.suit, "rank": self.rank}
    
    @classmethod
    def from_dict(cls, data):
        return cls(data["suit"], data["rank"])


class Hand:
    def __init__(self, card1, card2):
        self.card1 = card1
        self.card2 = card2
    
    def __repr__(self):
        return f"Hand({self.card1}, {self.card2})"
    
    def to_dict(self):
        return {
            "card1": self.card1.to_dict(),
            "card2": self.card2.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            Card.from_dict(data["card1"]),
            Card.from_dict(data["card2"])
        )


class CardRange:
    def __init__(self):
        self.card_range = []
    
    def add(self, hand):
        """Add a hand to the range"""
        self.card_range.append(hand)
    
    def remove(self, hand):
        """Remove a hand from the range"""
        if hand in self.card_range:
            self.card_range.remove(hand)
    
    def clear(self):
        """Clear all hands from the range"""
        self.card_range = []
    
    def __len__(self):
        return len(self.card_range)
    
    def __repr__(self):
        return f"CardRange({len(self.card_range)} hands)"
    
    def to_list(self):
        return [h.to_dict() for h in self.card_range]