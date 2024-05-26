from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.dialects.postgresql import JSONB

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # settings = db.Column(JSONB)
    is_active = db.Column(db.Boolean, default=True)
    # created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    # last_login = db.Column(db.DateTime)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def is_active(self):
        return self.is_active

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True


class Word(db.Model):
    __tablename__ = 'words'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    word = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    examples = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    repeated = db.Column(db.Integer, default=0)         # X times repeated
    repeat_initial_at = db.Column(db.DateTime)          # initial learning
    repeat_first_review = db.Column(db.DateTime)        # day 1
    repeat_second_review = db.Column(db.DateTime)       # day 3
    repeat_third_review = db.Column(db.DateTime)        # day 7
    repeat_fourth_review = db.Column(db.DateTime)       # day 14
    repeat_fifth_review = db.Column(db.DateTime)        # day 30
    repeat_subsequent = db.Column(db.DateTime)          # every 30 days
    # pronunciation
    # definition
    # synonyms

    user = db.relationship('User', backref=db.backref('words', lazy=True))

    def __repr__(self):
        return f"Word('{self.word}')"






