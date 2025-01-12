# src/theseus_alpha/trading/types.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class TradeExecution:
    asset: str
    success: bool
    order_id: Optional[int]
    error: Optional[str]
    timestamp: datetime