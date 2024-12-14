from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
import bcrypt
from .database import articles, users, redis_client
import datetime
from bson import ObjectId
import logging
logging.basicConfig(level=logging.DEBUG)

LOGIN_TEMPLATE = 'auth/login.html'
LOGIN_TITLE = 'Přihlášení'
REGISTER_TEMPLATE = 'auth/register.html'
REGISTER_TITLE = 'Registrace'

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def index():
    if 'user' in session:
        data = list(articles.find())
        if len(data) > 0:
            for article in data:
                # Převod ObjectId na string, pokud je potřeba
                article['_id'] = str(article['_id'])
                article['is_favourite'] = article['_id'] in session['user']['favourites']

                # article['date'] = article['date'].strftime('%d.%m.%Y')
                # article['rating'] = len(article['rating'])
                # article['rating_avg'] = sum(article['rating']) / len(article['rating']) if article['rating'] else
        return render_template('index.html', title="Domů", user=session['user'], articles=data)
    return render_template('index.html', title="Domů")

@main.route('/favourites', methods=['GET'])
def favourites():
    if 'user' in session:
        user = session['user']
        favourite_ids = [ObjectId(fav) for fav in user['favourites']]
        favourites = list(articles.find({"_id": {"$in": favourite_ids}}))
        return render_template('favourites.html', title="Oblíbené", articles=favourites)
    return render_template(LOGIN_TEMPLATE, title=LOGIN_TITLE)

@main.route('/addArticleToFavourites', methods=['POST'])
def add_article_to_favourites():
    json_data = request.get_json()
    if(not json_data):
        return jsonify({"error": "No data provided"}), 400

    session_user = session.get('user')
    if not session_user:
        return jsonify({"error": "User not logged in"}), 401

    article_id = json_data.get('article_id')
    if not article_id:
        return jsonify({"error": "Article ID not provided"}), 400

    user_id = ObjectId(session_user.get('_id'))
    # find users favourites
    data = users.find_one({'_id': user_id}, {'favourites': 1})
    if not data:
        return jsonify({"error": "User does not exist"}), 404

    favourites = data.get('favourites', [])

    # find article in favourites array
    if article_id not in favourites:
        # update users favourites
        update = users.update_one({'_id': user_id}, {'$push': {'favourites': article_id}})
        if update.modified_count == 0:
            return jsonify({"error": "Failed to update favourites"}), 500

        session_user['favourites'].append(article_id)
        session['user'] = session_user
        return jsonify({"message": "Article added to favourites"}), 200

    # Remove article from favourites
    update = users.update_one({'_id': user_id}, {'$pull': {'favourites': article_id}})
    if update.modified_count == 0:
        return jsonify({"error": "Failed to remove from favourites"}), 500

    if 'favourites' in session_user and article_id in session_user['favourites']:
        session_user['favourites'].remove(article_id)
    session['user'] = session_user
    return jsonify({"message": "Article removed from favourites"}), 200

@main.route('/article', methods=['GET', 'POST'])
def article():
    if 'user' not in session:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        cover = request.form['cover']
        author = session['user']['_id']
        article = {
            'name': name,
            'url': url,
            'cover': cover,
            'author': author,
            'date': datetime.datetime.now(),
            'rating': [],
        }
        articles.insert_one(article)
        return redirect(url_for('main.index'))

    return render_template('article.html', title="Přidat / upravit článek", user=session['user'])

@main.route('/login', methods=['GET', 'POST'])
def login():
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
                'email': user['email'],
                'favourites': user['favourites']
            }
            return redirect(url_for('main.index'))

        return render_template(LOGIN_TEMPLATE, title=LOGIN_TITLE, error="invalid_credentials"), 401

    return render_template(LOGIN_TEMPLATE, title=LOGIN_TITLE)

@main.route('/register', methods=['GET', 'POST'])
def register():
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
