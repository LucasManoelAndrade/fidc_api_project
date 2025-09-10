from app.db import db
from app.db.models import Operation
from app.utils.logger import get_logger

logger = get_logger(__name__)

def create_operation(id, asset_code, operation_type, quantity, status="PENDING", execution_price=None, total_value=None, tax_paid=None):
    op = Operation(
        id=id,
        asset_code=asset_code,
        operation_type=operation_type,
        quantity=quantity,
        status=status,
        execution_price=execution_price,
        total_value=total_value,
        tax_paid=tax_paid
    )
    db.session.add(op)
    db.session.commit()
    logger.info("Operação criada", extra={"operation_id": id})
    return op

def get_operation(op_id):
    return db.session.query(Operation).filter_by(id=op_id).first()

def update_operation(op_id, **kwargs):
    op = get_operation(op_id)
    if op:
        for key, value in kwargs.items():
            if hasattr(op, key):
                setattr(op, key, value)
        db.session.commit()
        logger.info("Operação atualizada", extra={"operation_id": op_id})
    else:
        logger.warning("Tentativa de atualizar operação inexistente", extra={"operation_id": op_id})
    return op

def delete_operation(op_id):
    op = get_operation(op_id)
    if op:
        db.session.delete(op)
        db.session.commit()
        logger.info("Operação deletada", extra={"operation_id": op_id})
    else:
        logger.warning("Tentativa de deletar operação inexistente", extra={"operation_id": op_id})
    return op