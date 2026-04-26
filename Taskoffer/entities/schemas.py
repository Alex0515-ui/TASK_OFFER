from pydantic import BaseModel, EmailStr, field_validator, Field
from entities.user_models import Role
import phonenumbers

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
