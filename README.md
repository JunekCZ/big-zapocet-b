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
│ └── templates/
│   └── index.html
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Struktura databáze

articles:

- \_id: ObjectId
- title: string
- content: string
- created_at: datetime
- avg_rating: float # Průměrné hodnocení
- rating_count: int # Počet hodnocení
- favorites: list # Seznam ID uživatelů, kteří článek označili jako oblíbený

users:

- \_id: ObjectId
- username: string
- email: string
- password: string # Hashované heslo
- favorite_articles: list # Seznam ID oblíbených článků

ratings:

- \_id: ObjectId
- user_id: ObjectId # ID uživatele, který hodnotil
- article_id: ObjectId # ID článku, který byl hodnocen
- rating: int # Hodnocení (např. 1–5)
- created_at: datetime
