from src.Database.database import Database
from flask import Flask, request, jsonify, render_template

Database = Database()
Database.insertNote("Jello is", "Yummy")

app = Flask(__name__)

@app.route('/')
def index():
    if request.session.get('logged_in') == True:
        notes = Database.getNotes()
        return render_template('index.html', notes=notes)
    else:
        return render_template('login.html')

# Page to load the note when user clicks on the title
@app.route('/note/<id>')
def note(id):
    if request.session.get('logged_in') == True:
        noteTitle = Database.getNoteById(id);noteTitle = noteTitle['title']
        noteContent = Database.getNoteById(id);noteContent = noteContent['content']
        noteID = Database.getNoteById(id);noteID = noteID['_id']
        return render_template('note.html', noteTitle=noteTitle, noteContent=noteContent, noteID=noteID)
    else:
        return render_template('login.html')

@app.route('/addNote', methods=['POST', 'GET'])
def addNote():
    if request.session.get('logged_in') == True:
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
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form['Username']
        password = request.form['Password']
        if Database.login(username, password):
            request.session['username'] = username
            request.session['password'] = password
            request.session['logged_in'] = True
            return index()
        else:
            return render_template('login.html')
    return render_template('login.html')

app.run(host='0.0.0.0', port=5000)