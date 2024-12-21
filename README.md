# Zápočet pro KI/BIG u Ing. Mgr. P. Beránka

## Struktura projektu

```
flask_mongo_redis_app/
├── app/
│ ├── \_\_init\_\_.py
│ ├── config.py
│ ├── main.py
│ ├── database.py
│ ├── routes.py
│ ├── static/
│ │ ├── css/
│ │ │ └── common.css
│ │ ├── images/
│ │ ├── js/
│ │   ├── article.js
│ │   └── common.py
│ ├── templates/
│ │ ├── auth/
│ │ │ ├── login.html
│ │ │ └── register.html
│ │ ├── macros/
│ │ │ └── articles.macros.html
│ │ ├── messages/
│ │ │ └── errors.html
│ │ ├── article.html
│ │ ├── base.html
│ │ ├── best.html
│ │ ├── favourites.html
│ │ └── index.html
│ └── utils/
│   ├── common.utils.py
│   └── \_\_init\_\_.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Struktura databáze

articles:

- \_id: ObjectId
- name: string
- url: string
- cover: string
- author: string
- date: datetime
- ratings: [] - Seznam objektů `{ 'user_id:' string, 'rating': number }` hodnocení

users:

- \_id: ObjectId
- email: string
- password: string - Hashované heslo
- favourites: list - Seznam ID oblíbených článků
