from celery import Celery, Task
import os
from app.utils.logger import get_logger  # Logger centralizado
from app.services.asset_service import get_asset_price  # Importa do service

celery = Celery(
    "fidc_tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

logger = get_logger(__name__)  # Usa logger estruturado

@celery.task(bind=True, max_retries=3, default_retry_delay=5)
def process_operations_job(self, job_id, fidc_id, operations):
    """
    Processa operações de FIDC de forma assíncrona e atômica.
    """
    from app.db import db
    from app.db.models import FidcCash, Operation, ProcessingJob
    from datetime import datetime

    logger.info(f"Iniciando processamento do job", extra={"job_id": job_id})

    try:
        job = db.session.get(ProcessingJob, job_id)
        fidc = db.session.get(FidcCash, fidc_id)
        if not job or not fidc:
            logger.error("Job ou FIDC não encontrado", extra={"job_id": job_id, "fidc_id": fidc_id})
            return

        with db.session.begin():  # Atomicidade garantida
            processed = 0

            for op_data in operations:
                asset_price = get_asset_price(op_data["asset_code"])
                if asset_price <= 0:
                    raise Exception("Preço do ativo inválido")

                gross_value = op_data["quantity"] * asset_price

                if op_data["operation_type"] == "BUY":
                    tax = gross_value * 0.005
                    total_cost = gross_value + tax
                    if fidc.available_cash < total_cost:
                        raise Exception("Caixa insuficiente para compra")
                    fidc.available_cash -= total_cost
                    op_status = "PROCESSED"
                    total_value = total_cost
                elif op_data["operation_type"] == "SELL":
                    tax = gross_value * 0.003
                    net_proceeds = gross_value - tax
                    fidc.available_cash += net_proceeds
                    op_status = "PROCESSED"
                    total_value = net_proceeds
                else:
                    raise Exception("Tipo de operação inválido")

                operation = Operation(
                    id=op_data["id"],
                    asset_code=op_data["asset_code"],
                    operation_type=op_data["operation_type"],
                    quantity=op_data["quantity"],
                    status=op_status,
                    execution_price=asset_price,
                    total_value=total_value,
                    tax_paid=tax,
                    job_id=job_id,
                    created_at=datetime.utcnow()
                )
                db.session.add(operation)
                processed += 1
                logger.info("Operação processada", extra={"job_id": job_id, "operation_id": op_data["id"], "status": op_status})

            job.status = "COMPLETED"
            job.completed_at = datetime.utcnow()
            db.session.add(job)

        logger.info("Job finalizado com sucesso", extra={"job_id": job_id, "processed": processed})

    except Exception as exc:
        logger.error("Erro no job", extra={"job_id": job_id, "error": str(exc)})
        # Atualiza o status do job para FAILED fora da transação
        job = db.session.get(ProcessingJob, job_id)
        if job:
            job.status = "FAILED"
            job.completed_at = datetime.utcnow()
            db.session.add(job)
            db.session.commit()
        self.retry(exc=exc)