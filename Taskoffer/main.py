from fastapi import FastAPI, HTTPException
from db.database import Base, engine
import auth.authentication as authentication
from auth.authentication import user_dependency

app = FastAPI()
app.include_router(authentication.router)

Base.metadata.create_all(bind=engine)

@app.get('/')
def get_user(user: None, db: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Пользователь не найден')
    return {"user": user}