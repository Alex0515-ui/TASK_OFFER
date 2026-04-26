from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from typing import Annotated
from entities.user_models import User, Wallet
from db.config import settings
from entities.schemas import CreateUserSchema, Token
from db.database import get_db
from db.config import settings


# Метод для хэширования паролей
password_verify = PasswordHash.recommended()


# ======== Хэширование паролей и сравнение их
def hash_password(password: str):
    return password_verify.hash(password)

def verify_password(password:str, hashed_password: str):
    return password_verify.verify(password, hashed_password)
# ================================================================

# Проверка на логин
def authenticate_user(email:str, password:str, db):
    user = db.query(User).filter(User.email==email).first()

    if not user:
        return False
    
    if not verify_password(password=password, hashed_password=user.password_hash):
        return False
    
    return user

def create_access_token(email:str, user_id:int, expire_time: timedelta):
    encode = {'sub': email, 'id': user_id}
    expires = datetime.now(timezone.utc) + expire_time
    encode.update({'exp': expires})
    return jwt.encode(encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)