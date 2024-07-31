from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__, template_folder='templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)  # Generates a random 24-byte secret key
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)

@app.route("/", methods=['GET', 'POST'])
def serve_login():
    global user
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pass']
        
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                session['user_id'] = user.id
                notes = Note.query.all()
                return render_template("notes.html", username=username, contents=notes)
            else:
                return render_template("index.html", greeting="Invalid Username or Password")
        else:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            notes = Note.query.all()
            return render_template("notes.html", username=username, contents=notes)
    return render_template("index.html", greeting="Welcome")

@app.route("/signup")
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pass']
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        notes = Note.query.all()
        return render_template("notes.html", username=username, contents=notes)

@app.route("/add", methods=['GET', 'POST'])
def add_note():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_note = Note(title=title, content=content)
        db.session.add(new_note)
        db.session.commit()
        
        user = User.query.filter_by(id=session.get('user_id')).first()
        notes = Note.query.all()
        return render_template("notes.html", username=user.username, contents=notes)
    return render_template("index.html")

@app.route("/delete/<int:note_id>", methods=['DELETE'])
def delete_note(note_id):
    note = Note.query.get(note_id)
    if note:
        db.session.delete(note)
        db.session.commit()
        return jsonify({'result': 'success'})
    return jsonify({'result': 'error', 'message': 'Note not found'}), 404

@app.route("/logout")
def logout():
    return render_template("index.html", greeting="Going so soon?")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
