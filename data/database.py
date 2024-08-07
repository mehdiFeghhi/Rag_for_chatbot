from pymongo import MongoClient

# Create a connection using MongoClient
client = MongoClient('localhost', 27017)

# Specify the database to be used
db = client['Rag']

