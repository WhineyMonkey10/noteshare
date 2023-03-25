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
        
    def insertNote(self, title, content, userID, private):
        self.collection.insert_one({"title": title, "content": content, "protected": "False", "userID": userID, "private": private})
        if private == "True":
            users.update_one({"_id": ObjectId(userID)}, {"$inc": {"privateNoteCount": 1}})
            return True
        elif private == "False":
            users.update_one({"_id": ObjectId(userID)}, {"$inc": {"publicNoteCount": 1}})
            return True
            
    def insertCustomIDNote(self, title, content, userID, private, id):
        if collection.find_one({"customID": id}):
            print("Custom ID already exists")
            return False
        else:
            self.collection.insert_one({"title": title, "content": content, "protected": "False", "userID": userID, "private": private, "CustomID": id})
            if private == "True":
                users.update_one({"_id": ObjectId(userID)}, {"$inc": {"privateNoteCount": 1}})
                return True
            elif private == "False":
                users.update_one({"_id": ObjectId(userID)}, {"$inc": {"publicNoteCount": 1}})
                return True
    
    def insertCustomIDNoteWithPassword(self, title, content, password, userID, private, id):
        if collection.find_one({"customID": id}):
            print("Custom ID already exists")
            return False
        else:
            self.collection.insert_one({"title": title, "content": content, "password": password, "protected": "True", "userID": userID, "private": private, "CustomID": id})
            if private == "True":
                users.update_one({"_id": ObjectId(userID)}, {"$inc": {"privateNoteCount": 1}})
                return True
            elif private == "False":
                users.update_one({"_id": ObjectId(userID)}, {"$inc": {"passwordNoteCount": 1}})
                return True
        
        
    def insertNoteWithPassword(self, title, content, password, userID, private):
        self.collection.insert_one({"title": title, "content": content, "password": password, "protected": "True", "userID": userID, "private": private})
        if private == "True":
            users.update_one({"_id": ObjectId(userID)}, {"$inc": {"privateNoteCount": 1}})
        elif private == "False":
            users.update_one({"_id": ObjectId(userID)}, {"$inc": {"passwordNoteCount": 1}})
    def getNotes(self):
        publicNotes = self.collection.find({"private": "False", "CustomID": {"$exists": False}})
        return publicNotes
    
    def deleteNotes(self):
        self.collection.delete_many({})
        
    def deleteNote(self, id):
        try:
            self.collection.delete_one(id)
            return True
        except:
            return False
    
    def updateNote(self, _id, newNote):
        self.collection.update_one(_id, {"$set": newNote})
        
    def getNoteById(self, id):
        try:
            if self.collection.find_one({"_id": ObjectId(id)}):
                return self.collection.find_one({"_id": ObjectId(id)})
            
        except:
            return self.collection.find_one({"CustomID": id})
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
        
    def getUserID(self, username):
        if users.find_one({"username": username}):
            return users.find_one({"username": username})["_id"]
        else:
            return False
        
    def getPrivateNotes(self, userID):
        privateNotes = []
        for note in self.collection.find({"userID": userID}):
            if note["private"] == "True":
                privateNotes.append(note)
        return privateNotes
    
    def getNoteCreator(self, noteID):
        if self.collection.find_one({"CustomID": noteID}):
            if self.collection.find_one({"CustomID": noteID}):
                userID = self.collection.find_one({"CustomID": noteID})["userID"]
                return users.find_one({"_id": ObjectId(userID)})["_id"]
        else:
            if self.collection.find_one({"_id": ObjectId(noteID)}):
                userID = self.collection.find_one({"_id": ObjectId(noteID)})["userID"]
                return users.find_one({"_id": ObjectId(userID)})["_id"]
            else:
                return False
    
    def getPasswordProtectedNotes(self, userID):
        passwordProtectedNotes = []
        for note in self.collection.find({"userID": userID}):
            if note["protected"] == "True":
                passwordProtectedNotes.append(note)
        return passwordProtectedNotes
    
    def getStatistics(self, userID, type):
        user = users.find_one({"_id": ObjectId(userID)})
        if type == "private":
            return user["privateNoteCount"]
        elif type == "public":
            return user["publicNoteCount"]
        elif type == "password":
            return user["passwordNoteCount"]
        elif type == "total":
            total_count = 0
            if "privateNoteCount" in user:
                total_count += user["privateNoteCount"]
            else:
                users.update_one({"_id": ObjectId(userID)}, {"$set": {"privateNoteCount": 0}})
            if "publicNoteCount" in user:
                total_count += user["publicNoteCount"]
            else:
                users.update_one({"_id": ObjectId(userID)}, {"$set": {"publicNoteCount": 0}})
            if "passwordNoteCount" in user:
                total_count += user["passwordNoteCount"]
            else:
                users.update_one({"_id": ObjectId(userID)}, {"$set": {"passwordNoteCount": 0}})
            return total_count
    
    def checkUsername(self, username):
        if users.find_one({"username": username}):
            return True
        else:
            return False
        
    def checkPassword(self, username, password):
        if users.find_one({"username": username}):
            if ecryptionKey != "":
                password = password.encode('utf-8')
                stored_password = users.find_one({"username": username})["password"]
                if password == encrypt.decrypt(stored_password):
                    return True
            else:
                if users.find_one({"username": username})["password"] == password:
                    return True
            return False
    
    def changeUsername(self, username, newUsername):
        if users.find_one({"username": username}):
            users.update_one({"username": username}, {"$set": {"username": newUsername}})
            return True
        else:
            return False
        
    def changePassword(self, username, newPassword):
        if users.find_one({"username": username}):
            if ecryptionKey != "":
                 newPassword = newPassword.encode('utf-8')
                 newPassword = encrypt.encrypt(newPassword)
                 users.update_one({"username": username}, {"$set": {"password": newPassword}})
                 return True
            else:
                users.update_one({"username": username}, {"$set": {"password": newPassword}})
                return True
        else:
            return False


    def setPro(self, username):
        userID = self.getUserID(username)
        if users.find_one({"_id": ObjectId(userID)}):
            if "pro" in users.find_one({"_id": ObjectId(userID)}):
                users.update_one({"_id": ObjectId(userID)}, {"$set": {"pro": True}})
            else:
                users.update_one({"_id": ObjectId(userID)}, {"$set": {"pro": True}})
    
    def removePro(self, username):
        userID = self.getUserID(username)
        if users.find_one({"_id": ObjectId(userID)}):
            if "pro" in users.find_one({"_id": ObjectId(userID)}):
                users.update_one({"_id": ObjectId(userID)}, {"$set": {"pro": False}})
            else:
                users.update_one({"_id": ObjectId(userID)}, {"$set": {"pro": False}})
                
    def checkPro(self, username):
        userID = self.getUserID(username)
        if users.find_one({"_id": ObjectId(userID)}):
            if "pro" in users.find_one({"_id": ObjectId(userID)}) and users.find_one({"_id": ObjectId(userID)})["pro"] == True:
                return True
            else:
                return False
            
    def getUsernameFromID(self, userID):
        if users.find_one({"_id": ObjectId(userID)}):
            return users.find_one({"_id": ObjectId(userID)})["username"]
        else:
            return False

    def checkNoteOwnerProStatus(self, noteID):
        userID = self.getNoteCreator(noteID)
        
        if users.find_one({"_id": ObjectId(userID)}):
            if "pro" in users.find_one({"_id": ObjectId(userID)}) and users.find_one({"_id": ObjectId(userID)})["pro"] == True:
                return True
            else:
                return False
            
    def checkNoteCustomID(self, customID):
        if self.collection.find_one({"CustomID": customID}):
            return True
        else:
            return False
    
    def getNoteByCustomID(self, customID):
        if self.collection.find_one({"CustomID": customID}):
            return self.collection.find_one({"CustomID": customID})
        else:
            return False
        
    def getCustomNotes(self):
        return self.collection.find({"CustomID": {"$exists": True}, "private": "False"})
    
    def getCustomIDByNoteID(self, noteID):
        try:
            if self.collection.find_one({"_id": ObjectId(noteID)}) != None:
                return self.collection.find_one({"_id": ObjectId(noteID)})["CustomID"]
            else:
                return False
        except:
            return False