import pymongo
from helper.config_helper import ConfigHelper
from helper.database_helper import MongoDB


class BusinessFlow:
    def __init__(self, service_name):
        self.cfg_helper = ConfigHelper()
        self.service_name = service_name.upper()
        self.mongo = MongoDB()

        if "index_name" in self.cfg_helper.get_config(self.service_name).keys():
            self.index_name = self.cfg_helper.get_config(self.service_name)["index_name"]

    def insert_business_flow(self, data, request, member, params=None):
        pass

    def update_business_flow(self, data, request, member, params=None):
        pass

    def delete_business_flow(self, data, request, member, params=None):
        pass

    def select_business_flow(self, data, request, member, params=None):
        pass

    def insert_file(self, raw_index_name, file, _type, _id):
        self.mongo.get_mongo_connection()
        self.mongo.create_index(raw_index_name=raw_index_name)
        document = {"file_content": file, "type": _type, "_id": _id}
        return self.mongo.insert(document, raw_index_name, "insert_one")

    def serve_file(self, raw_index_name, _id):
        self.mongo.get_mongo_connection()
        self.mongo.create_index(raw_index_name=raw_index_name)
        document = {"_id": _id}
        return self.mongo.find(index_name=raw_index_name,query=document)
