from pydantic import BaseModel
from typing import Literal, Optional


class WalletBalanceResponse(BaseModel):
    balance_sar: int
    disclaimer_ar: str


class WalletTopupRequest(BaseModel):
    amount_sar: Literal[10, 20, 50]


class WalletTopupResponse(BaseModel):
    provider: str
    status: Literal["configured", "not_configured"]
    next_step: str
    disclaimer_ar: str


class WalletChargeRequest(BaseModel):
    type: Literal["unlock_first_full", "scan"]
    amount_sar: Literal[1, 2]
    scan_id: Optional[str] = None


class WalletChargeResponse(BaseModel):
    charged: bool
    balance_sar: int
    reason: Optional[str] = None
    disclaimer_ar: str
