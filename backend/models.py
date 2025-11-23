from datetime import datetime
from config import db

SUITS = ('hearts', 'diamonds', 'clubs', 'spades')

class Range(db.Model):
    __tablename__ = 'ranges'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, default='Unnamed Range')
    role = db.Column(db.String(20), nullable=False, default='hero')  # 'hero' | 'villain'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    hands = db.relationship('RangeHand', backref='range', cascade='all, delete-orphan', lazy='joined')

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'hands': [h.to_hand_dict() for h in self.hands],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class RangeHand(db.Model):
    __tablename__ = 'range_hands'

    id = db.Column(db.Integer, primary_key=True)
    range_id = db.Column(db.Integer, db.ForeignKey('ranges.id', ondelete='CASCADE'), index=True, nullable=False)

    card1_suit = db.Column(db.String(20), nullable=False)
    card1_rank = db.Column(db.Integer, nullable=False)  # 14=A, 13=K, ... 2=2
    card2_suit = db.Column(db.String(20), nullable=False)
    card2_rank = db.Column(db.Integer, nullable=False)

    def canonicalize(self):
        """Order cards consistently to avoid duplicates - higher rank first, then by suit if equal rank"""
        if self.card2_rank > self.card1_rank:
            # Swap if card2 has higher rank
            (self.card1_rank, self.card1_suit, self.card2_rank, self.card2_suit) = (
                self.card2_rank, self.card2_suit, self.card1_rank, self.card1_suit
            )
        elif self.card1_rank == self.card2_rank and self.card2_suit > self.card1_suit:
            # If same rank, order by suit
            (self.card1_suit, self.card2_suit) = (self.card2_suit, self.card1_suit)

    def to_hand_dict(self):
        return {
            'card1': {'suit': self.card1_suit, 'rank': self.card1_rank},
            'card2': {'suit': self.card2_suit, 'rank': self.card2_rank},
        }

    @classmethod
    def from_hand_dict(cls, range_id: int, data: dict):
        h = cls(
            range_id=range_id,
            card1_suit=data['card1']['suit'],
            card1_rank=int(data['card1']['rank']),
            card2_suit=data['card2']['suit'],
            card2_rank=int(data['card2']['rank']),
        )
        h.canonicalize()
        return h