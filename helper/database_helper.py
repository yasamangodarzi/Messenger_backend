import pymongo
from helper.config_helper import ConfigHelper


class MongoDB:
    def __init__(self):
        self.cfg_helper = ConfigHelper()
        self.mongo_host = self.cfg_helper.get_config("MONGO")["host"]
        self.mongo_port = self.cfg_helper.get_config("MONGO")["port"]
        self.database = self.cfg_helper.get_config("MONGO")["database"]
        self.mongo = self.get_mongo_connection()

    def get_mongo_connection(self):
        my_client = pymongo.MongoClient(f"mongodb://{self.mongo_host}:{self.mongo_port}/")
        return my_client[self.database]

    def create_index(self, raw_index_name):
        return self.mongo.mydb[raw_index_name]

    def insert(self, document, index_name, insert_type):
        if insert_type == "insert_one":
            insert_id = self.mongo.mydb[index_name].insert_one(document)
        elif insert_type == "insert_many":
            insert_id = self.mongo.mydb[index_name].insert_many(document)
        else:
            insert_id = ""
        return insert_id

    def find(self, index_name, query=None, projection=None, sort=None, limit=None):
        index = self.mongo.mydb[index_name]

        if limit is not None:
            if sort:
                return index.find(query, projection).sort(sort).limit(limit)
            else:
                return index.find(query, projection).limit(limit)
        else:
            if sort:
                return index.find(query, projection).sort(sort)
            else:
                return index.find(query, projection)

    def delete(self, id, index_name, delete_type):
        if delete_type == "delete_one":
            delete_id = self.mongo.mydb[index_name].delete_one({"_id": id})
        elif delete_type == "delete_many":
            delete_id = self.mongo.mydb[index_name].delete_many({"_id": {"$in": id}})
        else:
            delete_id = ""
        return delete_id

    def update(self, id, index_name, update_type, document):
        if update_type == "update_one":
            update_id = self.mongo.mydb[index_name].update_one({"_id": id}, {"$set": document})
        elif update_type == "update_many":
            update_id = self.mongo.mydb[index_name].update_many({"_id": {"$in": id}}, {"$set": document})
        else:
            update_id = ""
        return update_id
