import pymongo
from pymongo import MongoClient
import json


class MongoDB:

    mongodb_client = None
    orion_project_database = None

    def __init__(self):
        try:
            self.mongodb_client = MongoClient(host='', port=)
            self.orion_project_database = self.mongodb_client.orion_project
        except Exception as error:
            print("[ERROR]  When creating MongoDB Client Connection:", error)

    def insert_document_into_database(self, document_id, extracted_str):
        try:
            mongodb_document = {"document_id": document_id, "data": extracted_str}
            self.orion_project_database.lien_collection.insert_one(mongodb_document)
            print("Successfully inserted into MongoDB")

        except Exception as error:
            print("Failed inserting into MongoDB")
            print(error)
