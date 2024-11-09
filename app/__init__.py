# __init__.py
from flask import Flask
from .database import db, redis_client
from .routes import main

def create_app():
    app = Flask(__name__)
    app.secret_key = "secret12345"

    # Registrace blueprintu pro routy
    app.register_blueprint(main)

    # Tady můžeš mít i nastavení pro Redis, ale Redis se inicializuje přímo v `database.py`

    return app
