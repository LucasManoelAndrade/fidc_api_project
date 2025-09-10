import pytest
from fidc_api.app import create_app
from fidc_api.app.db import db
from fidc_api.app.db.models import ProcessingJob

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_job_status_not_found(client):
    # Testa resposta 404 para job inexistente
    response = client.get("/jobs/invalid-job-id/status")
    assert response.status_code == 404
    assert response.json["error"] == "Job not found"

def test_job_status_success(client):
    # Cria um job manualmente no banco
    job = ProcessingJob(status="PROCESSING")
    db.session.add(job)
    db.session.commit()

    response = client.get(f"/jobs/{job.job_id}/status")
    assert response.status_code == 200
    assert response.json["job_id"] == job.job_id
    assert response.json["status"] == "PROCESSING"
    assert response.json["total_operations"] == 0
    assert response.json["processed"] == 0
    assert response.json["failed"] == 0