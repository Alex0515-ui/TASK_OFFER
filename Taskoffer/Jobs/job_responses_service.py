from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from entities.models import *
from entities.schemas import CreateJobResponseSchema

class JobResponseService:

    # Создание заявки
    @staticmethod
    def create_bind_response(data: CreateJobResponseSchema, db: Session, worker_id: int):

        job = db.query(Job).filter(Job.id == data.job_id).first()
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Работа не найдена')
        
        if job.owner_id == worker_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Нельзя откликаться на свою работу!')
        
        if job.status != Job_status.IN_SEARCH:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Можно откликнуться только на свободную работу')
        
        existing_response = db.query(JobResponse).filter(JobResponse.job_id == data.job_id, JobResponse.worker_id == worker_id).first()
        if existing_response:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Вы уже оставляли заявку на эту работу')
        
        job_response = JobResponse(**data.model_dump(), worker_id=worker_id)

        db.add(job_response)
        db.commit()
        db.refresh(job_response)

        return job_response


    # Принятие заявки
    @staticmethod
    def accept_response(db: Session, response_id: int, client_id: int):
        response = db.query(JobResponse).filter(JobResponse.id == response_id).first()
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Заявка не найдена')
        
        if response.job.owner_id != client_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Нельзя принять заявку на чужую работу')
        
        response.status = Response_status.ACCEPTED
        response.job.status = Job_status.ACCEPTED
        response.job.worker_id = response.worker_id

        db.query(JobResponse).filter(               # Отклоняем другие заявки
            JobResponse.job_id == response.job.id, 
            JobResponse.id != response_id
        ).update({'status': Response_status.REJECTED})

        db.commit()

        return {"message": "Работник назначен, теперь работа начнется!"}



    # Получение всех оставленных заявок
    @staticmethod
    def get_my_worker_responses(db: Session, worker_id: int, type: Job_type = None, job_status : Job_status = None, response_status: Response_status = None, offset: int = 0, limit: int = 10):
        responses = db.query(JobResponse).join(Job).filter(JobResponse.worker_id == worker_id)
        if type:
            responses = responses.filter(Job.type==type)

        if job_status:
            responses = responses.filter(Job.status==job_status)

        if response_status:
            responses = responses.filter(JobResponse.status == response_status)

        return responses.order_by(JobResponse.created_at.desc()).offset(offset).limit(limit).all()
    

    # Получение заявок от работников
    @staticmethod
    def get_my_client_responses(db: Session, client_id: int, job_id: int = None, type: Job_type = None, response_status: Response_status = None, offset: int = 0, limit: int = 10):
        responses = db.query(JobResponse).join(Job).filter(Job.owner_id == client_id)

        if type:
            responses = responses.filter(Job.type == type)

        if response_status:
            responses = responses.filter(JobResponse.status == response_status)

        if job_id:
            responses = responses.filter(Job.id == job_id)

        return responses.order_by(JobResponse.created_at.desc()).offset(offset).limit(limit).all()
    

    # Просмотр заявки работника
    @staticmethod
    def get_client_response(db: Session, response_id: int, client_id: int):
        response = db.query(JobResponse).join(Job).filter(JobResponse.id == response_id, Job.owner_id == client_id).first()
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Заявка не найдена')
        
        return response
    

    # Просмотр своей заявки
    @staticmethod
    def get_worker_response(db: Session, response_id: int, worker_id: int):
        response = db.query(JobResponse).filter(JobResponse.id == response_id, JobResponse.worker_id == worker_id).first()
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Заявка не найдена')
        
        return response
    
    
    # Отклонение заявки работника
    @staticmethod
    def reject_response(db: Session, response_id: int, client_id: int):
        response = db.query(JobResponse).filter(JobResponse.id == response_id).first()
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = 'Заявка не найдена')
        
        if response.job.owner_id != client_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Вы не можете отклонить заявку на чужую работу')
        
        job = db.query(Job).filter(Job.id == response.job.id).first()
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = 'Работа не найдена')
        
        if job.status == Job_status.DONE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Работа уже завершена')
        elif job.status == Job_status.CANCELLED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Работа уже отменена')
        
        response.status = Response_status.REJECTED
        db.commit()

        return {"message": "Заявка успешно отклонена"}
    

    





    
