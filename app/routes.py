from flask import Blueprint, jsonify, request
from .database import mongo, redis_client

main = Blueprint('main', __name__)

@main.route('/data', methods=['GET'])
def get_data():
    # Získání dat z MongoDB
    data = mongo.db.collection_name.find_one({}, {'_id': 0})  # Místo 'collection_name' zadejte vaši kolekci
    if data:
        return jsonify(data), 200
    return jsonify({"error": "No data found"}), 404

@main.route('/data', methods=['POST'])
def save_data():
    # Získání JSON dat z požadavku
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Uložení dat do MongoDB a Redis
    mongo.db.collection_name.insert_one(data)
    redis_client.set("latest_data", str(data))  # Můžete použít jiný formát ukládání
    
    return jsonify({"message": "Data saved"}), 201
