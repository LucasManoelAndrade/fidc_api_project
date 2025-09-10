from flask import Blueprint
from .operations import operations_bp
from .jobs import jobs_bp
from .health import health_bp

api_bp = Blueprint("api", __name__)
api_bp.register_blueprint(operations_bp, url_prefix="/operations")
api_bp.register_blueprint(jobs_bp, url_prefix="/jobs")
api_bp.register_blueprint(health_bp, url_prefix="/health")
