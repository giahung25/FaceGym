from app.models.base import BaseModel


class Transaction(BaseModel):
    """Đại diện cho một giao dịch thanh toán."""

    PAYMENT_CASH = "cash"
    PAYMENT_TRANSFER = "transfer"
    PAYMENT_CARD = "card"

    def __init__(self, member_id, amount, subscription_id=None,
                 payment_method="cash", note=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.member_id = member_id
        self.subscription_id = subscription_id
        self.amount = amount
        self.payment_method = payment_method
        self.note = note

    def __str__(self):
        return f"Transaction(id={self.id}, member={self.member_id}, amount={self.amount})"
