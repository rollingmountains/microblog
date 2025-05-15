from typing import Optional, List
import sqlalchemy as sa
from sqlalchemy.ext.mutable import MutableList
import sqlalchemy.orm as so
from datetime import datetime, timezone
from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
import jwt
from time import time


followers = sa.Table('followers',
                     db.metadata,
                     sa.Column('follower_id', sa.Integer, sa.ForeignKey(
                         'user.id'), primary_key=True),
                     sa.Column('followed_id', sa.Integer,
                               sa.ForeignKey('user.id'), primary_key=True)
                     )


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(
        sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]
                             ] = so.mapped_column(sa.String(256))
    previous_passwords: so.Mapped[Optional[List[str]]
                                  ] = so.mapped_column(MutableList.as_mutable(sa.JSON), default=list, index=True, nullable=True)
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    posts: so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author')
    following: so.WriteOnlyMapped['User'] = so.relationship(secondary=followers, primaryjoin=(
        followers.c.follower_id == id), secondaryjoin=(followers.c.followed_id == id), back_populates='followers')
    followers: so.WriteOnlyMapped['User'] = so.relationship(secondary=followers, primaryjoin=(
        followers.c.followed_id == id), secondaryjoin=(followers.c.follower_id == id), back_populates='following')

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time(
        ) + expires_in}, app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms='HS256')['reset_password']
        except Exception:
            return
        return db.session.get(User, id)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}/?d=identicon&s={size}'

    def prune_previous_passwords_list(self):
        max_limit = int(app.config['PASSWORD_HISTORY_SIZE'])
        if len(self.previous_passwords) > max_limit:
            self.previous_passwords = self.previous_passwords[-max_limit:]

    def set_password(self, password):
        new_hash = generate_password_hash(password)

        # create empty list if the password list is None
        if self.previous_passwords is None:
            self.previous_passwords = []

        # add current password to the password list
        if self.password_hash:
            self.previous_passwords.append(self.password_hash)

        # set new password
        self.password_hash = new_hash

        # prune the list
        self.prune_previous_passwords_list()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def verify_reset_password(self, password):
        max_limit = int(app.config['PASSWORD_HISTORY_SIZE'])

        # check the current password
        if check_password_hash(self.password_hash, password):
            return False

        # check the password from the list
        for item in (self.previous_passwords or [])[-(max_limit - 1):]:
            if check_password_hash(item, password):
                return False
        return True

    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery())
        return db.session.scalar(query)

    def following_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery())
        return db.session.scalar(query)

    def following_posts(self):
        Author = so.aliased(User)
        Follower = so.aliased(User)
        return (
            sa.select(Post).join(Post.author.of_type(Author)).join(
                Author.followers.of_type(Follower), isouter=True).where(sa.or_(Follower.id == self.id, Author.id == self.id)).group_by(Post).order_by(Post.timestamp.desc())
        )

    def __repr__(self):
        return f'Name: {self.username}, Email: {self.email}'


class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[int] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(User.id), index=True)
    author: so.Mapped['User'] = so.relationship(back_populates='posts')

    def __repr__(self):
        return f'Author Id: {self.user_id}, Content: {self.body}'


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
