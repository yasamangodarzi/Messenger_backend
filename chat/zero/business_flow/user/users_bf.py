import datetime

from bson import ObjectId

from helper.business_flow_helpers import BusinessFlow
from helper.io_helpers import *
from chat.zero.utils.utils import *

from members import get_member
import chat as service


class UserBusinessFlowManager(BusinessFlow):
    def __init__(self, ):
        super(UserBusinessFlowManager, self).__init__(service.service_name)
        self.cfg_helper = ConfigHelper()
        self.index_image_file = self.cfg_helper.get_config(service.service_name)["index_image_file"]
        self.message_index_name = self.cfg_helper.get_config(service.service_name)["message_index_name"]

    def select_business_flow(self, data, request, member, params=None):
        self.mongo.get_mongo_connection()

        if 'method' not in request.keys():
            raise RequiredFieldError("method")

        method = request["method"]
        if method == "select_chat":
            contact_id = str(data['contact_id'])
            user_id = str(request['member_id'])
            query = {"chat_id": f"{user_id}.{contact_id}"}
            search_result = list(self.mongo.find(query=query, index_name=self.index_name, limit=1))
            if len(search_result) == 0:
                query = {"chat_id": f"pv.{contact_id}.{user_id}"}
                search_result = list(self.mongo.find(query=query, index_name=self.index_name, limit=1))
                if len(search_result) == 0:
                    raise PermissionError()
            search_result[0]['_id'] = str(search_result[0]['_id'])

            results = {"total": len(search_result), "result": list(search_result)}
        elif method == "list_chat":
            user_id = str(request['member_id'])
            query = {"member_ids": {"$in": [user_id]}}
            search_result = list(self.mongo.find(query=query, index_name=self.index_name))
            if len(search_result) == 0:
                raise PermissionError()
            for item in range(len(search_result)):
                search_result[item]['_id'] = str(search_result[item]['_id'])
                search_result[item]['message_history'] = []
                query = {"chat_id": search_result[item]['chat_id']}
                search_result_message = list(self.mongo.find(query=query, index_name=self.message_index_name))
                for message in search_result_message:
                    message['_id'] = str(message['_id'])
                    search_result[item]['message_history'].append(message)

            results = {"total": len(search_result), "result": list(search_result)}
        else:
            raise PermissionError()

        return results

    def insert_business_flow(self, data, request, member, params=None):
        self.mongo.get_mongo_connection()
        method = request["method"]
        if method == "create_chat":
            contact_id = data.get("contact_id", None)
            if contact_id in [None, 'null']:
                raise RequiredFieldError("contact_id")
            user_id = request['member_id']

            data['member_ids'] = [user_id, contact_id]
            data['chat_id'] = f'{user_id}.{contact_id}'

            query = get_insert_check_query(data, service.chat_schema)
            if len(list(self.mongo.find(query=query, index_name=self.index_name))) != 0:
                raise DuplicatedChat()
            data["DC_CREATE_TIME"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
            data["last_update_date"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
            doc = check_full_schema(data, service.chat_schema)
            doc = preprocess(doc, service.chat_schema)
            insert_response = self.mongo.insert(index_name=self.index_name, document=doc, insert_type='insert_one')
            result = {"id": str(insert_response.inserted_id), "result": "inserted"}
        elif method == "add_new_message":
            if 'chat_id' not in list(data.keys()):
                raise RequiredFieldError("chat_id")
            query = {"chat_id": data['chat_id']}
            search_result = list(self.mongo.find(query=query, index_name=self.index_name))
            if len(search_result) == 0:
                raise DuplicatedChat()
            data['sender'] = request['member_id']
            data['receiver'] = []
            data["DC_CREATE_TIME"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
            data["last_update_date"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
            for item in search_result[0]['member_ids']:
                data['receiver'].append(item)
            doc = check_full_schema(data, service.message_schema)
            doc = preprocess(doc, service.message_schema)
            insert_response = self.mongo.insert(index_name=self.message_index_name, document=doc,
                                                insert_type='insert_one')
            result = {"id": str(insert_response.inserted_id), "result": "inserted"}

        else:
            raise PermissionError()

        return result

    def delete_business_flow(self, data, request, member, params=None):
        self.mongo.get_mongo_connection()
        if request["method"] == "delete_chat":

            query = {"chat_id": data['chat_id']}
            search_result = list(
                self.mongo.find(query=query, index_name=self.index_name, limit=1, projection={"member_ids"}))
            if len(search_result) == 0:
                raise DosenotExistChat()
            if member['_id'] not in search_result[0]['member_ids']:
                raise PermissionError()
            update_result = self.mongo.delete(index_name=self.index_name, id=search_result[0]['_id'],
                                              delete_type="delete_one")
            result = {"id": str(search_result[0]['_id']), "result": update_result.raw_result}
        elif request["method"] == "delete_send_message":

            query = {"chat_id": data['chat_id'], "_id":  ObjectId(data['messages_id'])}
            search_result = list(
                self.mongo.find(query=query, index_name=self.message_index_name, limit=1, projection={"sender"}))
            if len(search_result) == 0:
                raise MessageDosnotExist()
            if member['_id'] != search_result[0]['sender']:
                raise PermissionError()
            update_result = self.mongo.delete(index_name=self.message_index_name, id=search_result[0]['_id'],
                                              delete_type="delete_one")
            result = {"id": str(search_result[0]['_id']), "result": update_result.raw_result}
        else:
            raise PermissionError()

        return result

    def update_business_flow(self, data, request, member, params=None):
        self.mongo.get_mongo_connection()
        if request["method"] == "update_content_detail":
            data["last_update_date"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
            blocked_fields = ["user_id", "contact_id"]
            content_id = data["contact_id"]
            del data["contact_id"]

            if "access_status" in list(data.keys()):
                if data['access_status']:
                    data['status'] = 'online'
                    del data['access_status']
            data_keys = list(data.keys())
            for k in data_keys:
                if k in blocked_fields:
                    del data[k]
            query = {"contact_id": content_id, "user_id": request['member_id']}
            search_result = list(
                self.mongo.find(query=query, index_name=self.index_name, limit=1, projection={"user_id"}))
            if len(search_result) == 0:
                raise MemberNotFoundError()
            data["last_update_date"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")

            check_schema(data, service.contact_schema)
            data = preprocess(data, schema=service.contact_schema)

            newvalues = {**data}

            update_result = self.mongo.update(index_name=self.index_name, id=search_result[0]['_id'],
                                              document=newvalues,
                                              update_type='update_one')

            result = {"id": str(search_result[0]['_id']), "result": update_result.raw_result}

            return result
        raise PermissionError()

    # return result
