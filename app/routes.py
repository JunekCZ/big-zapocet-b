from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
import bcrypt
from .database import articles, users, ratings, redis_client

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def index():
    if 'user' in session:
        return render_template('index.html', title="Domů", user=session['user'])
    return render_template('index.html', title="Domů")

@main.route('/data', methods=['GET'])
def get_data():
    data = articles.find_one({}, {'_id': 0})
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
    LOGIN_TEMPLATE = 'auth/login.html'
    LOGIN_TITLE = 'Přihlášení'

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None

        if not email or not password.strip():
            error = "missing_credentials"
        if len(password.strip()) < 4:
            error = "password_is_too_short"
        if error:
            return render_template(LOGIN_TEMPLATE, title=LOGIN_TITLE, error=error), 400

        user = users.find_one({"email": email})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user'] = {
                '_id': str(user['_id']),
                'email': user['email']
            }
            return redirect(url_for('main.index'))

        return render_template(LOGIN_TEMPLATE, title=LOGIN_TITLE, error="invalid_credentials"), 401

    return render_template(LOGIN_TEMPLATE, title=LOGIN_TITLE)

@main.route('/register', methods=['GET', 'POST'])
def register():
    REGISTER_TEMPLATE = 'auth/register.html'
    REGISTER_TITLE = 'Registrace'

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        error = None
        if(password != confirm_password):
            error = "passwords_do_not_match"
        if(len(password) < 4):
            error = "password_is_too_short"
        if(not email or not password.strip() or not confirm_password.strip()):
            error = "empty_fields"
        if(error):
            return render_template(REGISTER_TEMPLATE, title=REGISTER_TITLE, error=error), 400

        if users.find_one({"email": email}):
            return render_template(REGISTER_TEMPLATE, title=REGISTER_TITLE, error="email_in_use"), 400

        hashed_password = bcrypt.hashpw(password.strip().encode('utf-8'), bcrypt.gensalt())
        user = {
            "email": email.strip(),
            "password": hashed_password
        }
        users.insert_one(user)
        return redirect(url_for('main.login')), 201

    return render_template(REGISTER_TEMPLATE, title=REGISTER_TITLE)

@main.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'user' in session:
        session.pop('user', None)
    return redirect(url_for('main.index'))
