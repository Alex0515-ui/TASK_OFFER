from apscheduler.schedulers.background import BackgroundScheduler
from entities.models import Job, Job_status
from datetime import datetime
from sqlalchemy import update
from config.database import SessionLocal
import logging


scheduler = BackgroundScheduler()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Авто закрытие работ если время размещения прошло
def close_expired_jobs():
    
    with SessionLocal() as db:
        now = datetime.now()
        jobs_close = (
                update(Job)
                .where(
                    Job.status == Job_status.IN_SEARCH,
                    Job.expires_at < now
                )
                .values(status=Job_status.EXPIRED)
            ) 
        
        result = db.execute(jobs_close)
        db.commit()
        logger.info(f"Задачи просроченные закрыты: {result.rowcount}")


scheduler.add_job(close_expired_jobs, 'interval', minutes=1)


