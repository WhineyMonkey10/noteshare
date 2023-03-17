from src.Database.database import Database
from flask import Flask, request, render_template, session, redirect, url_for
import json
from bson.objectid import ObjectId
from waitress import serve
Database = Database()


app = Flask(__name__)
config = json.load(open('src/Database/config.json'))
app.secret_key = config['secretKey']


@app.route('/publicNotes')
def index():
    if 'logged_in' in session:
        notes = Database.getNotes()
        return render_template('index.html', notes=notes)
    else:
        return render_template('login.html')

@app.route('/note/<id>')
def note(id):
    if 'logged_in' in session:
        noteTitle = Database.getNoteById(id);noteTitle = noteTitle['title']
        noteContent = Database.getNoteById(id);noteContent = noteContent['content']
        noteID = Database.getNoteById(id);noteID = noteID['_id']
        protected = Database.getNoteById(id);protected = protected['protected']
        if protected == "True":
            return render_template('protectednote.html', noteID=noteID)
        return render_template('note.html', noteTitle=noteTitle, noteContent=noteContent, noteID=noteID)
    else:
        return render_template('login.html')

@app.route('/accessProtectedNote/<id>', methods=['POST', 'GET'])
def accessProtectedNote(id):
    if 'logged_in' in session:
        if request.method == 'POST':
            password = request.form['password']
            noteTitle = Database.getNoteById(id);noteTitle = noteTitle['title']
            noteContent = Database.getNoteById(id);noteContent = noteContent['content']
            noteID = Database.getNoteById(id);noteID = noteID['_id']
            protected = Database.getNoteById(id);protected = protected['protected']
            if protected == "True":
                if password == Database.getNoteById(id)['password']:
                    return render_template('note.html', noteTitle=noteTitle, noteContent=noteContent, noteID=noteID)
                else:
                    return render_template('protectednote.html', noteTitle=noteTitle, noteContent=noteContent, noteID=noteID)
            return render_template('note.html', noteTitle=noteTitle, noteContent=noteContent, noteID=noteID)
        return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/addNote', methods=['POST', 'GET'])
def addNote():
    if 'logged_in' in session:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            if request.form.get('isPublic') is not None:
                password = request.form['password']
                Database.insertNoteWithPassword(title, content, password)
            else:
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
                if username == "admin":
                    return render_template('admin.html')
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
    
@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if 'logged_in' in session and session['username'] == 'admin':
        return render_template('admin.html')
    else:
        if 'logged_in' in session:
            return index()
        else:
            return render_template('login.html')
    
@app.route('/deleteNote/<id>', methods=['POST', 'GET'])
def delete(id):
    if 'logged_in' in session and session['username'] == 'admin':
        Database.deleteNote({"_id": ObjectId(id)})
        return admin()
    else:
        return render_template('index.html')
    
@app.route('/manageUser', methods=['POST', 'GET'])
def manageUser():
    if 'logged_in' in session and session['username'] == 'admin':
        user = request.form['username']
        if request.form.get('deleteAcc'):
            Database.deleteAccount(user)
        # Check if the checkbox is checked
        if request.form.get('changeUsernameCheck') is not None:
            newUsername = request.form['changeUsername']
            Database.changeUsername(user, newUsername)
        if request.form.get('changePasswordCheck') is not None:
            newPassword = request.form['changePassword']
            Database.changePassword(user, newPassword)
        return redirect(url_for('admin'))
    else:
        return render_template('login.html')


@app.route('/editNote/<id>', methods=['POST', 'GET'])
def editNote(id):
    pass

@app.route('/manageNotes', methods=['POST', 'GET'])
def manageNotes():
    if 'logged_in' in session and session['username'] == 'admin':
        noteid = request.form['noteId']
        if request.form.get('deleteNote'):
            Database.deleteNote({"_id": ObjectId(noteid)})
        if request.form.get('changeTitleCheck'):
            newTitle = request.form['changeTitle']
            Database.changeTitle(noteid, newTitle)
        if request.form.get('changeContentCheck'):
            newContent = request.form['changeContent']
            Database.changeContent(noteid, newContent)
        return admin()
    else:
        return render_template('login.html')
    
@app.route('/', methods=['POST', 'GET'])
def dashboard():
    if 'logged_in' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        return render_template('login.html')
        
if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000, threads=1)
