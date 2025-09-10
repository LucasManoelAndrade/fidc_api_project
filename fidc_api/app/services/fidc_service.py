from app.db import db
from app.db.models import FidcCash
from datetime import datetime
from app.utils.logger import get_logger

logger = get_logger(__name__)

def create_fidc_cash(fidc_id, available_cash=0.0):
    cash = FidcCash(fidc_id=fidc_id, available_cash=available_cash)
    db.session.add(cash)
    db.session.commit()
    logger.info("FIDC cash criado", extra={"fidc_id": fidc_id})
    return cash

def get_fidc_cash(fidc_id):
    return db.session.query(FidcCash).filter_by(fidc_id=fidc_id).first()

def update_fidc_cash(fidc_id, available_cash):
    cash = get_fidc_cash(fidc_id)
    if cash:
        cash.available_cash = available_cash
        cash.updated_at = datetime.utcnow()
        db.session.commit()
        logger.info("FIDC cash atualizado", extra={"fidc_id": fidc_id})
    else:
        logger.warning("Tentativa de atualizar FIDC cash inexistente", extra={"fidc_id": fidc_id})
    return cash

def delete_fidc_cash(fidc_id):
    cash = get_fidc_cash(fidc_id)
    if cash:
        db.session.delete(cash)
        db.session.commit()
        logger.info("FIDC cash deletado", extra={"fidc_id": fidc_id})
    else:
        logger.warning("Tentativa de deletar FIDC cash inexistente", extra={"fidc_id": fidc_id})
    return cash