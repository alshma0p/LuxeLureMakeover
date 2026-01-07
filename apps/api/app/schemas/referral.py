from pydantic import BaseModel


class ReferralCreateResponse(BaseModel):
    ref_code: str
    ref_link: str
    invite_required: int
    invite_completed: int
    disclaimer_ar: str


class ReferralCompleteResponse(BaseModel):
    ref_code: str
    invite_required: int
    invite_completed: int
    unlocked: bool
    disclaimer_ar: str
