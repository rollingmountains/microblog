from app import app, db
from app.models import User

with app.app_context():
    users = User.query.filter_by(previous_passwords=None).all()
    print(f'Found {len(users)} to users to upgrade.')

    for user in users:
        if user.password_hash:
            user.previous_passwords = [user.password_hash]

    db.session.commit()
