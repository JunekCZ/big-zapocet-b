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

@main.route('/', methods=['GET', 'POST'])
def index():
    data = get_articles_with_default_data()

    user_query = None
    radio = -1
    if request.method == 'POST':
        user_query = request.form.get('search-text', '').strip()  # Získá data z inputu
        radio = int(request.form.get('default-radio'))

    # Filtrování článků podle dotazu
    if user_query:
        data = [article for article in data if user_query.lower() in article['name'].lower()]

    # Filtrování dle nejnovějších
    if radio == 0:
        data = sorted(data, key=lambda x: x['date'], reverse=True)

    # Filtrování dle nejstarších
    if radio == 1:
        data = sorted(data, key=lambda x: x['date'])

    # Filtrování dle nejoblíbenějších
    if radio == 2:
        data = sorted(data, key=lambda x: sum(rating.get('rating', 0.0) for rating in x.get('ratings', [])), reverse=True)

    # Filtrování dle nejméně oblíbených
    if radio == 3:
        data = sorted(data, key=lambda x: sum(rating.get('rating', 0.0) for rating in x.get('ratings', [])))


    if 'user' in session and len(data) > 0:
        for article in data:
            # Převod ObjectId na string, pokud je potřeba
            article['_id'] = str(article['_id'])
            article['is_favourite'] = article['_id'] in session['user']['favourites']
            ratings = article['ratings']
            article['user_rating'] = next((rating['rating'] for rating in ratings if rating['user_id'] == session['user']['_id']), 0)
    return render_template('index.html', title="Domů", user=session.get('user', None), articles=data)

def get_articles_with_default_data():
    data = list(articles.find())
    if len(data) > 0:
        for article in data:
            # Převod ObjectId na string, pokud je potřeba
            article['_id'] = str(article['_id'])
            ratings = article.get('ratings', [])
            total_rating = sum(rating['rating'] for rating in ratings)
            article['ratings'] = ratings
            article['rating'] = total_rating / len(ratings) if len(ratings) > 0 else -1
            article['total_rating'] = total_rating

            # article['date'] = article['date'].strftime('%d.%m.%Y')
            # article['ratings'] = len(article['ratings'])
            # article['rating_avg'] = sum(article['rating']) / len(article['rating']) if article['rating'] else
    return data

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

@main.route('/rateArticle', methods=['POST'])
def rate_article():
    from bson import ObjectId
    from flask import jsonify, request, session

    # Načtení dat z JSON requestu
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No data provided"}), 400

    # Kontrola, zda je uživatel přihlášen
    session_user = session.get('user')
    if not session_user:
        return jsonify({"error": "User not logged in"}), 401

    # Získání ID článku
    article_id = json_data.get('article_id')
    if not article_id:
        return jsonify({"error": "Article ID not provided"}), 400

    # Získání hodnocení
    rating = json_data.get('rating')
    if not rating:
        return jsonify({"error": "Rating not provided"}), 400

    # Validace hodnocení (1-5)
    try:
        rating = int(rating)
        if rating < 1:
            rating = 1
        elif rating > 5:
            rating = 5
    except ValueError:
        return jsonify({"error": "Rating must be an integer"}), 400

    # Převod ID uživatele a článku
    user_id = str(session_user.get('_id'))
    try:
        article_id = ObjectId(article_id)
    except Exception:
        return jsonify({"error": "Invalid article ID"}), 400

    pipeline = [
        {'$match': {'_id': article_id}},  # Najdeme článek podle ID
        {
            '$set': {
                'ratings': {
                    '$concatArrays': [
                        {
                            '$filter': {
                                'input': {'$ifNull': ['$ratings', []]},
                                'as': 'rating',
                                'cond': {'$ne': ['$$rating.user_id', user_id]}
                            }
                        },
                        [{'user_id': user_id, 'rating': rating}]  # Přidáme nové/aktualizované hodnocení
                    ]
                }
            }
        },
        {
            '$merge': {
                'into': 'articles',  # Aktualizujeme kolekci articles
                'whenMatched': 'merge',  # Spojení do existujícího dokumentu
                'whenNotMatched': 'discard'  # Neaktualizujeme nic, pokud dokument neexistuje
            }
        }
    ]

    try:
        # Provádíme agregaci a aktualizujeme dokument
        articles.aggregate(pipeline)

        return jsonify({"success": "Rating updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
                'favourites': user.get('favourites', []),
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
