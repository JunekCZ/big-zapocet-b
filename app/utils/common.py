from flask import session

def get_articles_with_default_data(data):
    if len(data) > 0:
        for article in data:
            article['_id'] = str(article['_id'])
            ratings = article.get('ratings', [])
            total_rating = sum(rating['rating'] for rating in ratings)
            article['ratings'] = ratings
            article['rating'] = total_rating / len(ratings) if len(ratings) > 0 else -1
            article['total_rating'] = total_rating
            article['date'] = article['date'].strftime('%d.%m.%Y %H:%M')
    return data

def fill_users_data_into_article_array(data):
    if 'user' in session and len(data) > 0:
        for article in data:
            # Převod ObjectId na string, pokud je potřeba
            article['_id'] = str(article['_id'])
            article['is_favourite'] = article['_id'] in session['user']['favourites']
            ratings = article['ratings']
            article['user_rating'] = next((rating['rating'] for rating in ratings if rating['user_id'] == session['user']['_id']), 0)
    return data