from src.Database.database import Database
from flask import Flask, request, jsonify, render_template, session
import json
Database = Database()


app = Flask(__name__)
config = json.load(open('src/Database/config.json'))
app.secret_key = config['secretKey']


@app.route('/')
def index():
    if 'logged_in' in session:
        notes = Database.getNotes()
        return render_template('index.html', notes=notes)
    else:
        return render_template('login.html')

# Page to load the note when user clicks on the title
@app.route('/note/<id>')
def note(id):
    if 'logged_in' in session:
        noteTitle = Database.getNoteById(id);noteTitle = noteTitle['title']
        noteContent = Database.getNoteById(id);noteContent = noteContent['content']
        noteID = Database.getNoteById(id);noteID = noteID['_id']
        return render_template('note.html', noteTitle=noteTitle, noteContent=noteContent, noteID=noteID)
    else:
        return render_template('login.html')

@app.route('/addNote', methods=['POST', 'GET'])
def addNote():
    if 'logged_in' in session:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            Database.insertNote(title, content)
            return index()
        return render_template('addnote.html')
    else:
        return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'logged_in' not in session:
        if request.method == 'GET':
            return render_template('login.html')
        if request.method == 'POST':
            username = request.form['Username']
            password = request.form['Password']
            if Database.login(username, password):
                session['username'] = username
                session['password'] = password
                session['logged_in'] = True
                return index()
            else:
                return render_template('login.html')
        return render_template('login.html')
    else:
        return index()

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('username', None)
    session.pop('password', None)
    session.pop('logged_in', None)
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if 'logged_in' not in session:
        if request.method == 'GET':
            return render_template('register.html')
        if request.method == 'POST':
            username = request.form['Username']
            password = request.form['Password']
            if Database.register(username, password):
                return render_template('login.html')
            else:
                return render_template('register.html')
        return render_template('register.html')
    else:
        return index()




app.run(host='0.0.0.0', port=5000)