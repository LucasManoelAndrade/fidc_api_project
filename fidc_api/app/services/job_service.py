from app.db import db
from app.db.models import ProcessingJob
from app.utils.logger import get_logger

logger = get_logger(__name__)

def create_job(status="PROCESSING"):
    job = ProcessingJob(status=status)
    db.session.add(job)
    db.session.commit()
    logger.info("Job criado", extra={"job_id": job.job_id})
    return job

def get_job(job_id):
    return db.session.query(ProcessingJob).filter_by(job_id=job_id).first()

def update_job_status(job_id, status, completed_at=None):
    job = get_job(job_id)
    if job:
        job.status = status
        job.completed_at = completed_at
        db.session.commit()
        logger.info("Status do job atualizado", extra={"job_id": job_id, "status": status})
    else:
        logger.warning("Tentativa de atualizar job inexistente", extra={"job_id": job_id})
    return job

def delete_job(job_id):
    job = get_job(job_id)
    if job:
        db.session.delete(job)
        db.session.commit()
        logger.info("Job deletado", extra={"job_id": job_id})
    else:
        logger.warning("Tentativa de deletar job inexistente", extra={"job_id": job_id})
    return job