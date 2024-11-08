from flask import Flask
from .database import mongo, redis_client
from .routes import main

def create_app():
    app = Flask(__name__)
    
    # Nastavení MongoDB a Redis
    app.config['MONGO_URI'] = "mongodb://mongo:27017/mydatabase"
    mongo.init_app(app)
    
    # Registrace blueprintu pro routy
    app.register_blueprint(main)
    
    return app
