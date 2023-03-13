from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import json
from bson.objectid import ObjectId


config = json.load(open('src/Database/config.json'))


client = MongoClient(config['uri'])
database = client[config['database']]
collection = database[config['collection']]
users = database[config['userCollection']]

print(f"Connected to {config['uri']}.")

class Database:
    def __init__(self):
        self.collection = collection
        
    def insertNote(self, title, content):
        self.collection.insert_one({"title": title, "content": content})
        
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
        if users.find_one({"username": username, "password": password}):
            return True
        else:
            return False

    def register(self, username, password):
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