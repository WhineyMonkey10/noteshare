from src.Database.database import Database
from flask import Flask, request, render_template, session, redirect, url_for, abort, jsonify
import json
from bson.objectid import ObjectId
from waitress import serve
import stripe
import os
from dotenv import load_dotenv
Database = Database()


app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRETKEY')
app.config['STRIPE_SECRET_KEY'] = str(os.getenv('SECRETSTRIPEKEY'))
app.config['STRIPE_PUBLIC_KEY'] = str(os.getenv('PUBLISHSTRIPEKEY'))
stripe.api_key = app.config['STRIPE_SECRET_KEY']
stripePriceID = str(os.getenv('STRIPEPRICEID'))
endpoint_secret = str(os.getenv('STRIPEENDPOINTSECRET'))


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
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html')
        return render_template('login.html')
    else:
        return index()

@app.route('/privateNotes', methods=['POST', 'GET'])
def privateNotes(id, noteCreator, noteID):
    if 'logged_in' in session:
        if 'logged_in' not in session:
            return render_template('alertMessage.html', message='You must be logged in to access this note as it is private.')
        else:
            if id == noteCreator:
                note = Database.getNoteById(noteID)
                title = note['title']
                content = note['content']
                creator = Database.getNoteCreator(noteID)
                creator = Database.getUsernameFromID(creator)
                id = note['_id']
                if 'CustomID' in note:
                    id = note['CustomID']
                return render_template('note.html', noteTitle=title, noteContent=content, noteID=id, userID=creator)
            return render_template('alertMessage.html', message='You do not have access to this note.')
    else:
        return login()

@app.route('/publicNotes')
def index():
    if 'logged_in' in session:
        notes = Database.getNotes()
        customNotes = Database.getCustomNotes()
        return render_template('index.html', notes=notes, customNotes=customNotes)
    else:
        return render_template('login.html')

@app.route('/note/<id>')
def note(id):
    if Database.checkNoteExists(id) == False:
        return render_template('alertMessage.html', message='This note does not exist.')
    else:   
        def loadNote(id):
            if Database.getNoteContentByCustomID(id) == False:
                note = Database.getNoteById(id)
                customID = False
            else:
                note = Database.getNoteContentByCustomID(id)
                customID = True
            
            loaderIsOwner = Database.getNoteCreator(id)
            if loaderIsOwner == Database.getUserID(session['username']):
                loaderIsOwner = True
            else:
                loaderIsOwner = False
            title = note['title']
            content = note['content']
            if customID == False:
                creator = Database.getNoteCreator(id)
                creator = Database.getUsernameFromID(creator)
                noteID = note['_id']
            else:
                creator = Database.getNoteCreator(id)
                creator = Database.getUsernameFromID(creator)
                noteID = id
                
            protected = note['protected']
            private = note['private']
            
            if protected == "True":
                return render_template('protectednote.html', noteTitle=title, noteContent=content, noteID=noteID)

            if private == "True":
                if 'logged_in' not in session:
                    return render_template('alertMessage.html', message='You must be logged in to access this note as it is private.')
                else:
                    if Database.getNoteCreator(noteID) != Database.getUserID(session['username']):
                        return render_template('alertMessage.html', message='You do not have access to this note.')
                return privateNotes(Database.getUserID(session['username']), Database.getNoteCreator(noteID), noteID)
            
            return render_template('note.html', noteTitle=title, noteContent=content, noteID=noteID, userID=creator, loaderIsOwner=loaderIsOwner)
            
        if Database.checkNoteOwnerProStatus(id) == True and 'logged_in' not in session:
            return loadNote(id)
        elif Database.checkNoteOwnerProStatus(id) == True and 'logged_in' in session:
            return loadNote(id)
        else:
            if 'logged_in' in session:
                return loadNote(id)
            else:
                return render_template('login.html')

@app.route('/accessProtectedNote/<id>', methods=['POST', 'GET'])
def accessProtectedNote(id):
    if Database.checkNoteExists(id) == False:
        return render_template('alertMessage.html', message='This note does not exist.')
    else:
        def loadNote(id):
            if request.method == 'POST':
                if Database.getNoteContentByCustomID(id) == False:
                    note = Database.getNoteById(id)
                    customID = False
                else:
                    note = Database.getNoteContentByCustomID(id)
                    customID = True
            
                loaderIsOwner = Database.getNoteCreator(id)
                if loaderIsOwner == Database.getUserID(session['username']):
                    loaderIsOwner = True
                else:
                    loaderIsOwner = False
                
                noteTitle = note['title']
                noteContent = note['content']
                if customID == False:
                    creator = Database.getNoteCreator(id)
                    creator = Database.getUsernameFromID(creator)
                    noteID = note['_id']
                else:
                    creator = Database.getNoteCreator(id)
                    creator = Database.getUsernameFromID(creator)
                    noteID = id
                
                protected = note['protected']
                private = note['private']
                password = request.form['protPass']

                if protected == "True" and private == "True":
                    if 'logged_in' not in session:
                        return render_template('alertMessage.html', message='You must be logged in to access this note as it is private.')
                    else:
                        noteCreator = Database.getNoteCreator(noteID)
                        if Database.getNoteCreator(noteID) != Database.getUserID(session['username']):
                            return render_template('alertMessage.html', message='You do not have access to this note.')
                    if password == Database.getNoteById(id)['password']:
                        return privateNotes(Database.getUserID(session['username']), Database.getNoteCreator(noteID), noteID)
                if protected == "True":
                    if password == Database.getNoteById(id)['password']:
                        noteCreator = Database.getNoteCreator(noteID)
                        return render_template('note.html', noteTitle=noteTitle, noteContent=noteContent, noteID=noteID, userID=noteCreator, loaderIsOwner=loaderIsOwner)
                    else:
                        return render_template('protectednote.html', noteTitle=noteTitle, noteContent=noteContent, noteID=noteID)
            else:
                return render_template('login.html')
        
        if Database.checkNoteOwnerProStatus(id) == True and 'logged_in' not in session:
            return loadNote(id)
        elif Database.checkNoteOwnerProStatus(id) == True and 'logged_in' in session:
            return loadNote(id)
        else:
            if 'logged_in' in session:
                return loadNote(id)
            else:
                return render_template('login.html')

@app.route('/addNote', methods=['POST', 'GET'])
def addNote():
    if 'logged_in' in session:
        if request.method == 'POST':
            title = request.form['title']
            if len(title) > 20:
                return render_template('alertMessage.html', message='Your note title must be less than 20 characters.')
            content = request.form['content']
            if request.form.get('isPrivate') is not None and request.form.get('isPublic') is not None:
                password = request.form['password']
                if password == '':
                    return render_template('alertMessage.html', message='You must enter a password if you want to make your note password protected.')
                else:
                    if Database.checkPro(session['username']):
                        if request.form.get('customIDCheck') is not None:
                            customId = request.form['customID']
                            if customId == '':
                                return render_template('alertMessage.html', message='You must enter a custom ID if you want to make your note have a custom ID.')
                            if Database.insertCustomIDNoteWithPassword(title, content, password, Database.getUserID(session['username']), "True", customId):
                                return index()
                            else:
                                return render_template('alertMessage.html', message='A note with that ID already exists.')
                        else:
                            Database.insertNoteWithPassword(title, content, password, Database.getUserID(session['username']), "True")
                    else:
                        Database.insertNoteWithPassword(title, content, password, Database.getUserID(session['username']), "True")
            
            elif request.form.get('isPrivate') is not None:
                if Database.checkPro(session['username']):
                    if request.form.get('customIDCheck') is not None:
                        customId = request.form['customID']
                        if customId == '':
                            return render_template('alertMessage.html', message='You must enter a custom ID if you want to make your note have a custom ID.')
                        if Database.insertCustomIDNote(title, content, Database.getUserID(session['username']), "True", customId):
                            return index()
                        else:
                            return render_template('alertMessage.html', message='A note with that ID already exists.')
                    else:
                        Database.insertNote(title, content, Database.getUserID(session['username']), "True")
                else:
                    Database.insertNote(title, content, Database.getUserID(session['username']), "True")
                
            elif request.form.get('isPublic') is not None:
                password = request.form['password']
                if password == '':
                    return render_template('alertMessage.html', message='You must enter a password if you want to make your note password protected.')
                if Database.checkPro(session['username']):
                    if request.form.get('customIDCheck') is not None:
                        customId = request.form['customID']
                        if customId == '':
                            return render_template('alertMessage.html', message='You must enter a custom ID if you want to make your note have a custom ID.')
                        if Database.insertCustomIDNoteWithPassword(title, content, password, Database.getUserID(session['username']), "False", customId):
                            return index()
                        else:
                            return render_template('alertMessage.html', message='A note with that ID already exists.')
                    else:
                        Database.insertNoteWithPassword(title, content, password, Database.getUserID(session['username']), "False")
                else:
                    Database.insertNoteWithPassword(title, content, password, Database.getUserID(session['username']), "False")
                
            else:
                if Database.checkPro(session['username']):
                    if request.form.get('customIDCheck') is not None:
                        customId = request.form['customID']
                        if customId == '':
                            return render_template('alertMessage.html', message='You must enter a custom ID if you want to make your note have a custom ID.')
                        if Database.insertCustomIDNote(title, content, Database.getUserID(session['username']), "False", customId):
                            return index()
                        else:
                            return render_template('alertMessage.html', message='A note with that ID already exists.')
                    else:
                        Database.insertNote(title, content, Database.getUserID(session['username']), "False")
                else:
                    Database.insertNote(title, content, Database.getUserID(session['username']), "False")
            
            return index()
        return render_template('addnote.html', pro=Database.checkPro(session['username']))
    else:
        return render_template('login.html')


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
        if request.form.get('togglePro') is not None:
            if Database.checkPro(user):
                Database.removePro(user)
            else:
                Database.setPro(user)
        if request.form.get('userSignInAs') is not None:
            session['username'] = user
            session['logged_in'] = True
            return index()
        
        return redirect(url_for('admin'))
    else:
        return render_template('login.html')


@app.route('/editNote/<id>', methods=['POST', 'GET', 'PUT'])
def editNote(id):
    if 'logged_in' in session:
        if request.method == 'POST':
            noteID = id
            if ObjectId.is_valid(noteID) or Database.checkNoteExists(noteID):
                if Database.getNoteCreator(noteID) != False:
                    if session['username'] == Database.getUsernameFromID(Database.getNoteCreator(noteID)):
                        if Database.checkNoteExists(noteID):
                            newTitle = request.form['title']
                            if Database.changeTitle(noteID, newTitle):
                                newContent = request.form['content']
                                if Database.changeContent(noteID, newContent):
                                    newCustomID = request.form['customID']
                                    if Database.changeCustomID(noteID, newCustomID):
                                        return index()
                            #if request.form.get('isPublic'):
                            #    password = request.form['password']
                            #    if Database.changePublic(noteID, "True", password):
                            #        return index()
                            #    else:
                            #        errMsg = f"Error: {Database.changePublic(noteID, 'True', password)}"
                            #        return render_template('alertMessage.html', message=errMsg)
                            #if request.form.get('isPrivate'):
                            #    if Database.changePublic(noteID, "False", ""):
                            #        return index()
                            #    else:
                            #        errMsg = f"Error: {Database.changePublic(noteID, 'False', '')}"
                            #        return render_template('alertMessage.html', message=errMsg)
                            #if request.form.get('isPrivate') and request.form.get('isPublic'):
                            #    password = request.form['password']
                            #    if Database.changePublicAndPrivate(noteID, password):
                            #        return index()
                            #    else:
                            #        errMsg = f"Error: {Database.changePublicAndPrivate(noteID, password)}"
                            #        return render_template('alertMessage.html', message=errMsg)
                        else:
                            return render_template('alertMessage.html', message="Note does not exist!")
                    else:
                        return render_template('alertMessage.html', message="You are not the owner of this note!")
                else:
                    return render_template('alertMessage.html', message="Invalid note ID!")
            else:
                return render_template('alertMessage.html', message="Invalid note ID!")
            return render_template('editNote.html', noteID=noteID)
        return render_template('editNote.html', noteID=id)
    else:
        return render_template('login.html')
        

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
        return render_template('dashboard.html', globalMessage=Database.getGlobalMessages(), username=session['username'], userID=Database.getUserID(session['username']), total=Database.getStatistics(Database.getUserID(session['username']), 'total'), public=Database.getStatistics(Database.getUserID(session['username']), 'public'), private=Database.getStatistics(Database.getUserID(session['username']), 'private'), passwordProtected=Database.getStatistics(Database.getUserID(session['username']), 'password'), userHasPro=Database.checkPro(session['username']))
    else:
        return render_template('login.html')

@app.route('/privateNoteList/<userID>', methods=['POST', 'GET'])
def privateNoteList(userID):
    if 'logged_in' in session:
        userID = Database.getUserID(session['username'])
        note = Database.getPrivateNotes(userID)
        customIdNotes = Database.getPrivateNotesWithCustomID(userID)
        return render_template('privatenotes.html', notes = note, userID=Database.getUserID(session['username']), customIdNotes=customIdNotes)
    else:
        return render_template('login.html')

@app.route('/passwordProtectedNoteList/<userID>', methods=['POST', 'GET'])
def passwordProtectedNoteList(userID):
    if 'logged_in' in session:
        userID = Database.getUserID(session['username'])
        norma_notes = Database.getPasswordProtectedNotes(userID)
        return render_template('passwordProtectedNoteList.html', notes = norma_notes, userID=Database.getUserID(session['username']), customIdNotes=Database.getPasswordProtectedNotesWithCustomID(userID))
    else:
        return render_template('login.html')

@app.route('/manageProfile', methods=['POST', 'GET'])
def manageProfile():
    if 'logged_in' in session:
        return render_template('manageProfile.html', message="")

@app.route('/editProfile', methods=['POST', 'GET'])
def editProfile():
    if 'logged_in' in session:
        newUsername = request.form['username']
        newPassword = request.form['password']
        userID = Database.getUserID(session['username'])

        if Database.checkUsername(session['username']):
             if Database.checkPassword(session['username'],session['password']):
                if Database.changePassword(session['username'], newPassword):
                    if Database.changeUsername(session['username'], newUsername):
                        session['username'] = newUsername
                        session['password'] = newPassword
                        return render_template('manageProfile.html', message="Profile updated successfully")
                    else:
                        return render_template('manageProfile.html', message="Error updating password")
                else:
                    return render_template('manageProfile.html', message="Error updating username")
        else:
            return render_template('manageProfile.html', message="Error updating profile")
    else:
        return render_template('login.html')
        
        

@app.route('/deleteProfile', methods=['POST', 'GET'])
def deleteProfile():
    if 'logged_in' in session:
        if request.method == 'POST':
            if Database.deleteAccount(session['username']):
                session.pop('username', None)
                session.pop('password', None)
                session.pop('logged_in', None)
                return render_template('login.html')
            else:
                return render_template('manageProfile.html', message="Error deleting account")
    else:
        return login()

@app.route('/userDeleteNote', methods=['POST', 'GET'])
def userDeleteNote():
    if 'logged_in' in session:
        if ObjectId.is_valid(request.form['noteID']):
            if Database.getNoteCreator(request.form['noteID']) != None:
                if Database.getNoteCreator(request.form['noteID']) == Database.getUserID(session['username']):
                    if Database.deleteNote({"_id": ObjectId(request.form['noteID'])}):
                        return render_template('manageProfile.html', message="Successfully deleted note")
                    else:
                        return render_template('manageProfile.html', message="Error deleting note")
                else:
                    return render_template('manageProfile.html', message="You do not have permission to delete this note or it does not exist")
            else:
                return render_template('manageProfile.html', message="Note does not exist")
        else:
            return render_template('manageProfile.html', message="Not a valid note ID")
    else:
        return render_template('login.html')
    
@app.route('/editDeleteNote', methods=['POST', 'GET'])
def editDeleteNote():
    if 'logged_in' in session:
        note_id = request.args.get('noteID')
        if ObjectId.is_valid(note_id):
            if Database.getNoteCreator(note_id) != None:
                if Database.getNoteCreator(note_id) == Database.getUserID(session['username']):
                    if Database.deleteNote({"_id": ObjectId(note_id)}):
                        return render_template('alertMessage.html', message="Successfully deleted note")
                    else:
                        return render_template('alertMessage.html', message="Error deleting note")
                else:
                    return render_template('alertMessage.html', message="You do not have permission to delete this note or it does not exist")
            else:
                return render_template('alertMessage.html', message="Note does not exist")
        else:
            return render_template('alertMessage.html', message="Invalid note ID")
    else:
        return render_template('login.html')


@app.route('/thanks', methods=['POST', 'GET'])
def thanks():
    if 'logged_in' in session:
        return render_template('paymentComplete.html')
    else:
        return render_template('login.html')
    
    
@app.route('/purchase', methods=['POST', 'GET'])
def purchase():
    if 'logged_in' in session:
        stripeSession = stripe.checkout.Session.create(
            payment_intent_data={
                  "metadata": {"username": session['username']}
                },
            line_items=[{
                'price': stripePriceID,
                'quantity': 1,
            }],

          mode='payment',
          success_url=url_for('dashboard', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
          cancel_url=url_for('purchase', _external=True),
          )
        return render_template('checkout.html', checkout_session_id=stripeSession['id'], checkout_public_key=app.config['STRIPE_PUBLIC_KEY'])
    else:
        return render_template('login.html')


@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    event = None

    try:
        event_data = json.loads(payload.decode("utf-8"))
        event = stripe.Event.construct_from(
          event_data, stripe.api_key
        )
    except ValueError as e:
        return '', 400

    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        metadata = payment_intent.metadata
        username = metadata['username']
        Database.setPro(username)

    elif event.type == 'payment_method.attached':
        payment_method = event.data.object
        print('PaymentMethod was attached to a Customer!')
        
    elif event.type == "charge.succeeded":
        return url_for('dashboard')
    else:
        print('Unhandled event type {}'.format(event.type))

    return jsonify(success=True)

@app.route('/adminDangerZone', methods=['POST', 'GET'])
def adminDangerZone():
    if 'logged_in' in session and session['username'] == 'admin':
        message = request.form['globalBanner']
        if request.form.get('delGlobalMessage') is not None:
            deleteMessage = True
        else:
            deleteMessage = False
        
        if request.form.get('globalMessage') is not None:
            setMessage = True
        else:
            setMessage = False
        
        if setMessage:
            if Database.addGlobalMessage(message):
                return admin()
            else:
                return render_template('alertMessage.html', message="Error setting global message, one already exists")
        elif deleteMessage:
            if Database.removeGlobalMessage():
                return admin()
            else:
                return render_template('alertMessage.html', message="Error deleting global message")
        
        return render_template('admin.html')


@app.errorhandler(Exception)
def handle_error(e):
    return render_template('alertMessage.html', Admessage="Error: " + str(e), message="Uh oh! Something went wrong, please try again later. If this error persists, please contact us at support@mynote.ink", advanced=True)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('alertMessage.html', Admessage="Error: " + str(e), message="Uh oh! Something went wrong, please try again later. If this error persists, please contact us at support@mynote.ink", advanced=True)

@app.route('/advancedError', methods=['POST', 'GET'])
def advancedError(message):
    return render_template('advancedError.html', message=message)


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000, threads=1)