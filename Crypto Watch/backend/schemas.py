from pydantic import BaseModel, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value):
        if not value.strip():
            raise ValueError("Name cannot be empty")
        return value.strip()

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be 72 bytes or fewer.")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be 72 bytes or fewer.")
        return value


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class WatchlistCreate(BaseModel):
    coin_id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=150)
    symbol: str = Field(min_length=1, max_length=30)


class LumpsumRequest(BaseModel):
    investment: float = Field(gt=0)
    annual_return: float = Field(ge=-99.99, le=1000)
    years: float = Field(gt=0, le=100)


class SipRequest(BaseModel):
    monthly_investment: float = Field(gt=0)
    annual_return: float = Field(ge=-99.99, le=1000)
    years: int = Field(gt=0, le=100)
