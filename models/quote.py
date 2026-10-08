from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass(frozen=True)
class Quote:
    event_id: str
    instrument: str
    event_ts: datetime
    source_order: int
    bid: Decimal
    ask: Decimal
    @property
    def mid(self):
        return (self.bid + self.ask) / 2
