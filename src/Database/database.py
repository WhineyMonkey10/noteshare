from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import json

config = json.load(open('src/Database/config.json'))
print(config)