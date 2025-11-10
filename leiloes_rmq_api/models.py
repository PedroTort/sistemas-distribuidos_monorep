from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel


@dataclass
class AuctionModel(BaseModel):
    name: str
    current_value: float
    start_date: datetime
    end_date: datetime
    description: str | None = None

    def to_dict(self):
        return {
            "current_value": self.current_value,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "description": self.description,
            "auction_name": self.name,
        }


class BidModel(BaseModel):
    auction_name: str
    bidder_name: str
    bid_value: float
    bid_time: datetime


class AuctionSubscriptionModel(BaseModel):
    auction_name: str
    subscriber_name: str
