# filepath: c:\aplic\Lucas\fidc_project\fidc_api\app\routes\health.py
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200