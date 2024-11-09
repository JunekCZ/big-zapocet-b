from flask import Blueprint, render_template, jsonify, request, session
import bcrypt
from .database import db, redis_client

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def index():
    # db["articles"].insert_one({"title": title})

    # password_hash = bcrypt.hashpw("qwerty".encode("utf-8"), bcrypt.gensalt())
    # user = {
    #     "username": "john_doe",
    #     "email": "john@example.com",
    #     "password_hash": password_hash.decode("utf-8")
    # }

    # db["users"].insert_one(user)

    return render_template('index.html', title="Domů")

@main.route('/data', methods=['GET'])
def get_data():
    data = db.collection_name.find_one({}, {'_id': 0})
    if data:
        return render_template('index2.html', title="Domů", data=data, user=session.get("user", "none"))
    return jsonify({"error": "No data found"}), 404

@main.route('/data', methods=['POST'])
def save_data():
    # Získání JSON dat z požadavku
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Uložení dat do MongoDB a Redis
    # client.db.collection_name.insert_one(data)
    redis_client.set("latest_data", str(data))  # Můžete použít jiný formát ukládání
    
    return jsonify({"message": "Data saved"}), 201

@main.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('auth/login.html', title="Přihlášení")

@main.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('auth/register.html', title="Registrace")
