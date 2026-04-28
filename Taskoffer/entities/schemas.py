from pydantic import BaseModel, EmailStr, field_validator, Field
from entities.user_models import Role, Job_type
import phonenumbers
from datetime import datetime


class CreateUserSchema(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password_hash: str
    phone_number: str
    role: Role = Role.CLIENT

    @field_validator('phone_number')
    def validate_phone_number(cls, number:str):
        try:
            parsed_num = phonenumbers.parse(number)

            if not phonenumbers.is_valid_number(parsed_num):
                raise ValueError("Неправильный формат данных номера телефона")
            
            
            return phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.E164)
        except Exception:
            raise ValueError("Номер телефона должен включать код страны: (+7...)")


class Token(BaseModel):
    access_token: str
    token_type: str

class LoginSchema(BaseModel):
    email: str
    password: str


class CreateJobSchema(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=5)
    price: int 
    type: Job_type
    expires_at: datetime
    deadline: datetime


