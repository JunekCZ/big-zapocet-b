from flask import Blueprint, render_template, jsonify, request
import bcrypt
from .database import db, redis_client

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def index():
    title = "Moje Flask aplikace"
    # db["articles"].insert_one({"title": title})

    # password_hash = bcrypt.hashpw("qwerty".encode("utf-8"), bcrypt.gensalt())
    # user = {
    #     "username": "john_doe",
    #     "email": "john@example.com",
    #     "password_hash": password_hash.decode("utf-8")
    # }

    # db["users"].insert_one(user)

    return render_template('index.html', title=title)

@main.route('/data', methods=['GET'])
def get_data():
    data = db.collection_name.find_one({}, {'_id': 0})
    if data:
        title = "Moje Flask aplikace2"
        return render_template('index2.html', title=title, data=data)
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
