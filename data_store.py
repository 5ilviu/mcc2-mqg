from pymongo import MongoClient

__author__ = 'silviu'


class Database:
    def __init__(self):
        client = MongoClient(port=27017)
        db = client.get_database("mcc")
        self.users = db.get_collection("users")
        self.questions = db.get_collection("questions")