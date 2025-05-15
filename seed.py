from faker import Faker
import random
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash
from app import app, db
from app.models import User, Post

fake = Faker()


def create_test_users(count=10):
    users = []
    for i in range(1, count+1):
        user = User(
            username=fake.unique.user_name(),
            email=fake.unique.email(),
            password_hash=generate_password_hash('password'),
            about_me=fake.sentence(),
            last_seen=fake.date_time_this_year()
        )
        users.append(user)
    return users


def create_test_posts(users, posts_per_user=5):
    posts = []
    for user in users:
        for _ in range(posts_per_user):
            post = Post(
                body=fake.paragraph(nb_sentences=3),
                timestamp=fake.date_time_this_year(),
                language=random.choice(['en', 'es', 'fr', 'de']),
                author=user
            )
            posts.append(post)
    return posts


# Reset and populate the database
with app.app_context():
    # Drop all tables
    db.drop_all()
    print("Dropped all tables")

    # Create all tables
    db.create_all()
    print("Created all tables")

    # Create and add users
    users = create_test_users(10)
    for user in users:
        db.session.add(user)
    print(f"Created {len(users)} users")

    # Create and add posts
    posts = create_test_posts(users)
    for post in posts:
        db.session.add(post)
    print(f"Created {len(posts)} posts")

    # Commit everything to the database
    db.session.commit()
    print("Database populated successfully!")
