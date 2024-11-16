import os
from flask import Flask, request, render_template, redirect
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://es4140:whocares123@104.196.222.236/proj1part2')
engine = create_engine(DATABASE_URL)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY='dev')

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.before_first_request
    def create_tables():
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL
                );
            """))

            #here we would create all the tables? so our entire SQL schema


    #just a page with the path /hello that displays hello,world?
    @app.route('/hello')
    def hello():
        return 'Hello, World!'


    
    @app.route('/add_user', methods=['POST'])
    def add_user():
        username = request.form['username']
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO users (username) VALUES (:username)"), {"username": username})
        return redirect('/')

    @app.route('/users')
    def users():
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, username FROM users"))
            users = [dict(row) for row in result]
        return render_template('users.html', users=users)

    return app