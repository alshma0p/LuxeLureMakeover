from typing import Protocol

from app.core.config import settings


class PaymentAdapter(Protocol):
    provider: str

    def create_topup(self, amount_sar: int) -> str:
        ...


class NonePaymentAdapter:
    provider = "none"

    def create_topup(self, amount_sar: int) -> str:
        return "غير متاح حاليا"


def get_payment_adapter() -> PaymentAdapter:
    if settings.payment_provider == "none":
        return NonePaymentAdapter()
    return NonePaymentAdapter()
