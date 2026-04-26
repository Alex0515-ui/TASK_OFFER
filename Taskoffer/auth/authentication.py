from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Annotated
from sqlalchemy.orm import Session

from entities.user_models import User, Wallet
from db.config import settings
from entities.schemas import CreateUserSchema, Token
from db.database import get_db
from auth.auth_methods import *

router = APIRouter(prefix="/auth", tags=['auth'])

db_dependency = Annotated[Session, Depends(get_db)]

# Достает токен из заголовка запроса(Типо: Authorization Bearer: Токен мой)
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token') 


# Регистрация пользователя
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(db: Annotated[Session, Depends(get_db)], create_user_data: CreateUserSchema):

    user = User(
        name=create_user_data.name,
        email=create_user_data.email,
        phone_number=create_user_data.phone_number,
        password_hash=hash_password(create_user_data.password_hash)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    wallet = Wallet(user_id=user.id, user=user)
    db.add(wallet)
    db.commit()

    return {"message": "Пользователь создался успешно!"}


@router.post("/token", response_model=Token)
async def login(data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]):
    user = authenticate_user(email=data.username, password=data.password, db=db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь с такой почтой не существует")

    token = create_access_token(email=user.email, user_id=user.id, expire_time=timedelta(minutes=30))

    return {"access_token": token, 'token_type': 'bearer'}


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get('sub')
        user_id = payload.get('id')

        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Неполноценные данные пользователя')

        return {'email': email, 'id': user_id}
    
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Неправильные данные пользователя')
    

user_dependency = Annotated[dict, Depends(get_current_user)]