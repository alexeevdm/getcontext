from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func
from sqlalchemy import inspect
from flask_bcrypt import Bcrypt
from flask_login import current_user, login_required, LoginManager, login_user, logout_user
import random
import bot

from dotenv import load_dotenv
import os

from database import db, User, Word

load_dotenv()
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
MYSQL_DB_FLASKUSER = os.getenv("MYSQL_DB_FLASKUSER")
MYSQL_DB_FLASKPASSWORD = os.getenv("MYSQL_DB_FLASKPASSWORD")
MYSQL_DB_HOST = os.getenv("MYSQL_DB_HOST")
MYSQL_DB_NAME = os.getenv("MYSQL_DB_NAME")
FLASK_APP_HOST = os.getenv("FLASK_APP_HOST")
FLASK_APP_PORT = os.getenv("FLASK_APP_PORT")
SECRET_KEY = os.getenv('SECRET_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

app.config[
    'SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{MYSQL_DB_FLASKUSER}:{MYSQL_DB_FLASKPASSWORD}@{MYSQL_DB_HOST}/{MYSQL_DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SECRET_KEY'] = SECRET_KEY

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if user already exists
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        # Create new user instance
        new_user = User(username=username, email=email)
        new_user.set_password(password)  # Set hashed password

        # Add user to database
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get_or_404(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Login successful
            session['user_id'] = user.id
            login_user(user)
            flash('Login successful!', 'success')
            print('Login successful!')
            return render_template('dashboard.html', current_user=user)
        else:
            # Invalid credentials
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')


@login_required
def get_user_words():
    user_words = (
        Word.query
        .filter_by(user_id=current_user.id)
        .order_by(func.random())  # For SQLite (random ordering)
        .all()
    )
    return user_words


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    # Route logic
    return render_template('dashboard.html', current_user=current_user)


def training__no_words_template():
    return render_template('training.html',
                           examples="No words available",
                           show_word=False,
                           word_id=None)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/training')
@login_required
def training(word=None, word_id=None, update_examples=False):
    random_word = None
    examples = None
    if not word and not word_id:
        user_words = Word.query.filter_by(user_id=current_user.id).all()

        if user_words:
            random_word = random.choice(user_words)
            word = random_word.word
            word_id = random_word.id
            examples = random_word.examples
        else:
            return training__no_words_template()

    if examples is None or update_examples and word_id is not None:
        _word = None
        if random_word:
            _word = random_word
        else:
            _word = Word.query.get(word_id)
        examples = bot.get_5_examples(_word.word)
        _word.examples = examples
        db.session.commit()

    return render_template('training.html',
                           examples=examples,
                           show_word=False,
                           word=word,
                           word_id=word_id)


@app.route('/my_collection')
def collection():
    words = get_user_words()
    return render_template('my_collection.html')


@app.route('/training__remove_word/<int:word_id>', methods=['POST'])
def training__remove_word(word_id):
    word = Word.query.get_or_404(word_id)
    db.session.delete(word)
    db.session.commit()

    return redirect(url_for('training'))


@app.route('/training__update_examples', methods=['POST'])
def training__new_example():
    word = request.form['word']
    word_id = request.form['word_id']
    if word:
        return training(word=word, word_id=word_id, update_examples=True)
    else:
        return training__no_words_template()


@app.route('/training__next_word', methods=['POST'])
def training__next_word():
    return training()


@app.route('/training__get_synonyms', methods=['POST'])
def training__get_synonyms():
    word = request.form['word']
    synonyms = bot.get_synonyms(word)
    if word:
        return render_template('training.html',
                               examples=request.form['examples'],
                               word=word,
                               show_synonyms=True,
                               word_id=request.form['word_id'],
                               synonyms=synonyms)
    return training()


@app.route('/training__get_definition', methods=['POST'])
def training__get_definition():
    word = request.form['word']
    definition = bot.get_difinition(word)
    if word:
        return render_template('training.html',
                               examples=request.form['examples'],
                               word=word,
                               show_definition=True,
                               word_id=request.form['word_id'],
                               definition=definition)
    return training()


@app.route('/training__get_translation', methods=['POST'])
def training__get_translation():
    word = request.form['word']
    translation = bot.get_translation(word)
    if word:
        return render_template('training.html',
                               examples=request.form['examples'],
                               word=word,
                               show_translation=True,
                               word_id=request.form['word_id'],
                               translation=translation)
    return training()


@app.route('/training__get_collocations', methods=['POST'])
def training__get_collocations():
    return training()


@app.route('/training__get_other_forms', methods=['POST'])
def training__get_other_forms():
    return training()


@app.route('/training__get_phrases_and_idioms', methods=['POST'])
def training__get_phrases_and_idioms():
    return training()


@app.route('/my_collection__add_word', methods=['POST'])
def my_collection__add_word():
    # Retrieve the new word from the form data
    new_word = request.form['new_word']
    # Create a new Message object and add it to the database
    word = Word(word=new_word,
                user_id=current_user.id,
                examples=bot.get_5_examples(new_word))
    db.session.add(word)
    db.session.commit()
    return render_template('my_collection.html', word_added=True, word=new_word)


def initialize_database():
    with app.app_context():
        engine = db.engine
        inspector = inspect(engine)
        if not inspector.has_table('users') and not inspector.has_table('words'):
            db.create_all()


if __name__ == '__main__':
    initialize_database()
    app.run(host=FLASK_APP_HOST, port=FLASK_APP_PORT, debug=True)
