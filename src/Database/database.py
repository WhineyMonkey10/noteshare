from pymongo import MongoClient, srv_resolver
from pymongo.errors import ConnectionFailure
import json
from bson.objectid import ObjectId
from cryptography.fernet import Fernet
import codecs

config = json.load(open('src/Database/config.json'))



client = MongoClient(config['uri'])
database = client[config['database']]
collection = database[config['collection']]
users = database[config['userCollection']]
ecryptionKey = config['encryptionKey']


if ecryptionKey != "":
    encrypt = Fernet(codecs.encode((ecryptionKey).encode('utf-8'), 'base64'))     

print(f"Connected to {config['uri']}.")
    

class Database:
    def __init__(self):
        self.collection = collection
        
    def insertNote(self, title, content):
        self.collection.insert_one({"title": title, "content": content, "protected": "False"})
        
    def insertNoteWithPassword(self, title, content, password):
        self.collection.insert_one({"title": title, "content": content, "password": password, "protected": "True"})
        
    def getNotes(self):
        return self.collection.find()
    
    def deleteNotes(self):
        self.collection.delete_many({})
        
    def deleteNote(self, id):
        self.collection.delete_one(id)
    
    def updateNote(self, _id, newNote):
        self.collection.update_one(_id, {"$set": newNote})
        
    def getNoteById(self, id):
        return self.collection.find_one({"_id": ObjectId(id)})
    
    def getNoteByTitle(self, title):
        return self.collection.find_one({"title": title})
    
    def getNoteByContent(self, content):
        return self.collection.find_one({"content": content})
    def login(self, username, password):
        if ecryptionKey != "":
            password = password.encode('utf-8')
            if users.find_one({"username": username}):
                stored_password = users.find_one({"username": username})["password"]
                if password == encrypt.decrypt(stored_password):
                    return True
            else:
                return False
        return False
    
    def register(self, username, password):
        if ecryptionKey != "":
            password = password.encode('utf-8')
            password = encrypt.encrypt(password)
        if users.find_one({"username": username}):
            return False
        else:
            users.insert_one({"username": username, "password": password})
            return True

    def deleteAccount(self, username):
        if users.find_one({"username": username}):
            users.delete_one({"username": username})
            return True
        else:
            return False
        
    def changeUsername(self, username, newUsername):
        if users.find_one({"username": username}):
            users.update_one({"username": username}, {"$set": {"username": newUsername}})
            return True
        else:
            return False
        
    def changePassword(self, username, newPassword):
        if ecryptionKey != "":
            newPassword = newPassword.encode('utf-8')
            newPassword = encrypt.encrypt(newPassword)
        if users.find_one({"username": username}):
            users.update_one({"username": username}, {"$set": {"password": newPassword}})
            return True
        else:
            return False
        
    def changeTitle(self, id, newTitle):
        if self.collection.find_one({"_id": ObjectId(id)}):
            self.collection.update_one({"_id": ObjectId(id)}, {"$set": {"title": newTitle}})
            return True
        else:
            return False
    
    def changeContent(self, id, newContent):
        if self.collection.find_one({"_id": ObjectId(id)}):
            self.collection.update_one({"_id": ObjectId(id)}, {"$set": {"content": newContent}})
            return True
        else:
            return False
