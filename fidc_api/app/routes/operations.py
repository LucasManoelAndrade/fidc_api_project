import os
import csv
import io
from datetime import datetime
from flask import Blueprint, request, jsonify
from flasgger.utils import swag_from
from app.db.models import ProcessingJob, Operation
from app.db import db
from app.schemas.schemas import ProcessOperationsSchema, ExportOperationsSchema
from marshmallow import ValidationError
from app.utils.s3_client import get_s3_client
from app.utils.logger import get_logger

logger = get_logger(__name__)

operations_bp = Blueprint("operations", __name__)

@operations_bp.route("/process", methods=["POST"])
@swag_from({
    "tags": ["Operations"],
    "description": "Cria um job e processa operações",
    "parameters": [{
        "in": "body",
        "name": "body",
        "schema": {
            "example": {
                "fidc_id": "FIDC001",
                "operations": [
                    {
                        "id": "op_001",
                        "asset_code": "PETR4",
                        "operation_type": "BUY",
                        "quantity": 1000
                    }
                ]
            }
        }
    }],
    "responses": {
        201: {"description": "Job criado com sucesso"}
    }
})
def process_operations():
    from app.workers.tasks import process_operations_job
    data = request.get_json()
    try:
        validated = ProcessOperationsSchema().load(data)
    except ValidationError as err:
        logger.warning("Payload inválido para processamento de operações", extra={"error": err.messages})
        return jsonify({"error": "Invalid input", "messages": err.messages}), 400

    # Cria o job de processamento
    job = ProcessingJob(status="PROCESSING")
    db.session.add(job)
    db.session.commit()
    logger.info("Job de processamento criado", extra={"job_id": job.job_id})

    # Salva as operações associadas ao job
    for op_data in validated["operations"]:
        op = Operation(
            id=op_data["id"],
            asset_code=op_data["asset_code"],
            operation_type=op_data["operation_type"],
            quantity=op_data["quantity"],
            job_id=job.job_id,
            status="PENDING"
        )
        db.session.add(op)
    db.session.commit()
    logger.info("Operações associadas ao job salvas", extra={"job_id": job.job_id, "total_operations": len(validated["operations"])})

    # Dispara o processamento assíncrono (Celery)
    process_operations_job.delay(job.job_id, validated["fidc_id"], validated["operations"])
    logger.info("Processamento assíncrono disparado", extra={"job_id": job.job_id})

    return jsonify({"job_id": job.job_id, "message": "Job criado com sucesso"}), 201

@operations_bp.route("/export", methods=["POST"])
@swag_from({
    "tags": ["Operations"],
    "description": "Exporta operações de um FIDC para bucket (Minio/S3 simulado)",
    "parameters": [{
        "in": "body",
        "name": "body",
        "schema": {
            "example": {
                "fidc_id": "FIDC001",
                "start_date": "2025-09-01",
                "end_date": "2025-09-30"
            }
        }
    }],
    "responses": {
        200: {"description": "Export job iniciado"}
    }
})
def export_operations():
    data = request.get_json()
    try:
        validated = ExportOperationsSchema().load(data)
    except ValidationError as err:
        logger.warning("Payload inválido para exportação de operações", extra={"error": err.messages})
        return jsonify({"error": "Invalid input", "messages": err.messages}), 400

    # Busca operações no banco
    operations = db.session.query(Operation).filter(
        Operation.asset_code.isnot(None),
        Operation.created_at >= validated["start_date"],
        Operation.created_at <= validated["end_date"],
        Operation.fidc_id == validated["fidc_id"]
    ).all()

    logger.info("Operações buscadas para exportação", extra={
        "fidc_id": validated["fidc_id"],
        "start_date": str(validated["start_date"]),
        "end_date": str(validated["end_date"]),
        "total_operations": len(operations)
    })

    # Serializa para CSV em memória
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "asset_code", "operation_type", "quantity", "status",
        "execution_price", "total_value", "tax_paid", "created_at"
    ])
    for op in operations:
        writer.writerow([
            op.id, op.asset_code, op.operation_type, op.quantity, op.status,
            op.execution_price, op.total_value, op.tax_paid,
            op.created_at.isoformat() if op.created_at else ""
        ])
    output.seek(0)

    # Upload para Minio/S3 usando client centralizado
    s3 = get_s3_client()
    bucket = os.getenv("MINIO_BUCKET", "fidc-exports")
    filename = f"export_{validated['fidc_id']}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"

    # Cria o bucket se não existir
    try:
        s3.head_bucket(Bucket=bucket)
    except Exception:
        s3.create_bucket(Bucket=bucket)

    s3.put_object(Bucket=bucket, Key=filename, Body=output.getvalue())

    logger.info("Exportação de operações concluída e enviada ao bucket", extra={
        "fidc_id": validated["fidc_id"],
        "file": filename,
        "bucket": bucket,
        "total_operations": len(operations)
    })

    return jsonify({
        "message": f"Export job for {validated.get('fidc_id')} completed",
        "file": filename
    }), 200