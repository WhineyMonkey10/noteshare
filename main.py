from src.Database.database import Database
from flask import Flask, request, jsonify, render_template

Database = Database()
Database.insertNote("Jello is", "Yummy")

app = Flask(__name__)

@app.route('/')
def index():
    notes = Database.getNotes()
    return render_template('index.html', notes=notes)

# Page to load the note when user clicks on the title
@app.route('/note/<id>')
def note(id):
    noteTitle = Database.getNoteById(id);noteTitle = noteTitle['title']
    noteContent = Database.getNoteById(id);noteContent = noteContent['content']
    noteID = Database.getNoteById(id);noteID = noteID['_id']
    return render_template('note.html', noteTitle=noteTitle, noteContent=noteContent, noteID=noteID)

@app.route('/addNote', methods=['POST', 'GET'])
def addNote():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        Database.insertNote(title, content)
        return index()
    return render_template('addnote.html')

app.run(host='0.0.0.0', port=5000)