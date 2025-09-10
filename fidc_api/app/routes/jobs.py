from flask import Blueprint, jsonify
from flasgger.utils import swag_from
from app.db.models import ProcessingJob, Operation
from app.db import db
from app.schemas.schemas import ProcessingJobSchema  # Importa schema centralizado
from marshmallow import ValidationError
from app.utils.logger import get_logger

logger = get_logger(__name__)

jobs_bp = Blueprint("jobs", __name__)

@jobs_bp.route("/<job_id>/status", methods=["GET"])
@swag_from({
    "tags": ["Jobs"],
    "description": "Consulta o status de um job de processamento",
    "parameters": [{
        "name": "job_id",
        "in": "path",
        "type": "string",
        "required": True
    }],
    "responses": {
        200: {
            "description": "Status do job retornado",
            "schema": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string"},
                    "status": {"type": "string"},
                    "total_operations": {"type": "integer"},
                    "processed": {"type": "integer"},
                    "failed": {"type": "integer"},
                    "estimated_completion": {"type": ["string", "null"], "format": "date-time"}
                }
            }
        },
        404: {"description": "Job não encontrado"}
    }
})
def job_status(job_id):
    # Validação do parâmetro job_id usando Marshmallow schema centralizado
    try:
        ProcessingJobSchema().load({"job_id": job_id})
    except ValidationError as err:
        logger.warning("Job ID inválido na consulta de status", extra={"job_id": job_id})
        return jsonify({"error": "Invalid job_id", "messages": err.messages}), 400

    job = db.session.get(ProcessingJob, job_id)
    if not job:
        logger.warning("Job não encontrado na consulta de status", extra={"job_id": job_id})
        return jsonify({"error": "Job not found"}), 404

    # Busca operações relacionadas ao job
    total_operations = db.session.query(Operation).filter_by(job_id=job_id).count()
    processed = db.session.query(Operation).filter_by(job_id=job_id, status="PROCESSED").count()
    failed = db.session.query(Operation).filter_by(job_id=job_id, status="FAILED").count()

    # Estimativa de conclusão (exemplo: None, ou calcule se desejar)
    estimated_completion = job.completed_at.isoformat() if job.completed_at else None

    logger.info("Consulta de status do job realizada com sucesso", extra={
        "job_id": job_id,
        "status": job.status,
        "total_operations": total_operations,
        "processed": processed,
        "failed": failed
    })

    return jsonify({
        "job_id": job.job_id,
        "status": job.status,
        "total_operations": total_operations,
        "processed": processed,
        "failed": failed,
        "estimated_completion": estimated_completion
    })