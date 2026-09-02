from pydantic import BaseModel


class DemoLoginRequest(BaseModel):
    merchant_id: int


class MerchantResponse(BaseModel):
    id: int
    name: str
    email: str
    industry: str
    currency: str

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    merchant: MerchantResponse

