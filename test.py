from src.Database.database import *
Database = Database()

print(Database.getUsernameFromID(Database.getNoteCreator("6423f95653fa91d194e9b093")))