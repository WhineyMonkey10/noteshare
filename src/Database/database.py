from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import json

# Import the config file in JSON format

with open('config.json') as config_file:
    config = json.load(config_file)

config.get('uri')
