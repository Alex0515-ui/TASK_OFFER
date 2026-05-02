from fastapi import FastAPI, HTTPException
from db.database import Base, engine
import auth.authentication as authentication
import Jobs.jobs as job
from auth.authentication import user_dependency
import Job_responses.jobs_responses as job_responses
import Deals.deals as deals
app = FastAPI()

app.include_router(authentication.router)
app.include_router(job.router)
app.include_router(job_responses.router)
app.include_router(deals.router)

Base.metadata.create_all(bind=engine)

@app.get('/')
def get_user(user: None, db: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Пользователь не найден')
    return {"user": user}