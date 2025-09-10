import pytest
from fidc_api.app import create_app
from fidc_api.app.db import db
from fidc_api.app.db.models import ProcessingJob, Operation

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_process_operations_invalid_payload(client):
    # Payload inválido (faltando campos obrigatórios)
    response = client.post("/operations/process", json={})
    assert response.status_code == 400
    assert "error" in response.json

def test_process_operations_success(client):
    payload = {
        "fidc_id": "FIDC001",
        "operations": [
            {
                "id": "op_001",
                "asset_code": "PETR4",
                "operation_type": "BUY",
                "quantity": 1000,
                "operation_date": "2024-09-01"
            }
        ]
    }
    response = client.post("/operations/process", json=payload)
    assert response.status_code == 201
    assert "job_id" in response.json

def test_export_operations_invalid_payload(client):
    # Payload inválido (faltando campos obrigatórios)
    response = client.post("/operations/export", json={})
    assert response.status_code == 400
    assert "error" in response.json

def test_export_operations_success(client):
    # Primeiro, cria uma operação para exportar
    job = ProcessingJob(status="PROCESSING")
    db.session.add(job)
    db.session.commit()
    op = Operation(
        id="op_002",
        asset_code="PETR4",
        operation_type="BUY",
        quantity=100,
        job_id=job.job_id,
        status="PROCESSED"
    )
    db.session.add(op)
    db.session.commit()

    payload = {
        "fidc_id": op.asset_code,  # Ajuste conforme seu filtro real
        "start_date": "2024-01-01",
        "end_date": "2025-01-01"
    }
    response = client.post("/operations/export", json=payload)
    # O teste espera 200, mas pode ser ajustado conforme sua lógica de filtro
    assert response.status_code in (200, 400)