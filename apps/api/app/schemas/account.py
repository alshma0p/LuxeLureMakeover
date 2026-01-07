from pydantic import BaseModel


class AccountDeleteResponse(BaseModel):
    deleted: bool
    disclaimer_ar: str
