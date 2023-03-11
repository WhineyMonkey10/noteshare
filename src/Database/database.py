from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import json

config = json.load(open('src/Database/config.json'))


client = MongoClient(config['uri'])
database = client[config['database']]
collection = database[config['collection']]

print(f"Connected to {config['uri']}.")

class Database:
    def __init__(self):
        self.collection = collection
        
    def insertNote(self, id, title, content):
        self.collection.insert_one({"id": id, "title": title, "content": content})
        
    def getNotes(self):
        return self.collection.find()
    
    def deleteNotes(self):
        self.collection.delete_many({})
        
    def deleteNote(self, id):
        self.collection.delete_one(id)
    
    def updateNote(self, id, newNote):
        self.collection.update_one(id, {"$set": newNote})
        
    def getNoteById(self, id):
        return self.collection.find_one({"_id": id})
    
    def getNoteByTitle(self, title):
        return self.collection.find_one({"title": title})
    
    def getNoteByContent(self, content):
        return self.collection.find_one({"content": content})
    
Database = Database()
Database.insertNote(1, "Hello", "World")