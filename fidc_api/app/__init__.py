import os
from flask import Flask
from flasgger import Swagger

from app.db import db
from app.db import models  # Garante que os modelos sejam registrados
from app.routes import api_bp
from app.routes.health import health_bp

def create_app():
    app = Flask(__name__)

    # Config DB via .env (sem valores padrão hardcoded)
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_name = os.getenv("DB_NAME")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")

    if not all([db_user, db_pass, db_name, db_host]):
        raise RuntimeError("Variáveis de ambiente do banco de dados não configuradas corretamente.")

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Swagger
    app.config['SWAGGER'] = {
        'title': 'FIDC API',
        'uiversion': 3
    }
    Swagger(app)

    # Init DB
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Registra rotas
    app.register_blueprint(api_bp)
    app.register_blueprint(health_bp)

    return app