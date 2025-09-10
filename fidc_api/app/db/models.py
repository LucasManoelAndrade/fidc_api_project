from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app.db import db

import uuid

class FidcCash(db.Model):
    __tablename__ = "fidc_cash"

    fidc_id = db.Column(db.String, primary_key=True)
    available_cash = db.Column(db.Float, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class ProcessingJob(db.Model):
    __tablename__ = "processing_jobs"

    job_id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = db.Column(db.String, default="PROCESSING")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)


class Operation(db.Model):
    __tablename__ = "operations"

    id = db.Column(db.String, primary_key=True)
    asset_code = db.Column(db.String, nullable=False)
    operation_type = db.Column(db.String, nullable=False)  # BUY / SELL
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, default="PENDING")
    execution_price = db.Column(db.Float, nullable=True)
    total_value = db.Column(db.Float, nullable=True)
    tax_paid = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    job_id = db.Column(db.String, db.ForeignKey("processing_jobs.job_id"))  # Correção: adiciona relação com job
    fidc_id = db.Column(db.String, db.ForeignKey("fidc_cash.fidc_id"), nullable=True)  # Opcional: se quiser filtrar por FIDC na exportação