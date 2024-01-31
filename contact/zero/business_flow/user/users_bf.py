import datetime
from hashlib import md5
from helper.business_flow_helpers import BusinessFlow
from helper.config_helper import ConfigHelper
import contact as service
from helper.io_helpers import *
from contact.zero.utils.utils import *
import random

from members import get_member


class UserBusinessFlowManager(BusinessFlow):
    def __init__(self, ):
        super(UserBusinessFlowManager, self).__init__(service.service_name)
        self.cfg_helper = ConfigHelper()
        self.index_image_file = self.cfg_helper.get_config(service.service_name)["index_image_file"]

    def select_business_flow(self, data, request, member, params=None):
        self.mongo.get_mongo_connection()

        if 'method' not in request.keys():
            raise RequiredFieldError("method")

        method = request["method"]
        if method == "select_content":
            user_id = str(data['user_id'])
            query = {"user_id": user_id}
            search_result = list(self.mongo.find(query=query, index_name=self.index_name))
            for item in range(len(search_result)):
                del search_result[item]['_id']
                add = True
                contact_info = get_member(search_result[item]['contact_id'])
                contact_list_contact = get_contact(search_result[item]['contact_id'])
                for contact_contact_list in contact_list_contact:
                    if contact_contact_list['contact_id'] == user_id:
                        if contact_contact_list['access_photo'] in ['TRUE', True, "True", "true"]:
                            if contact_info["image"] not in ['null', None, "None"]:
                                find_image = list(self.serve_file(self.index_image_file, contact_info["image"]))
                                if len(find_image) != 0:
                                    search_result[item]["image"] = {
                                        "file_content": find_image[0]['file_content'],
                                        "file_type": find_image[0]['type'],
                                    }
                        if contact_contact_list['access_phone'] in ['TRUE', True, "True", "true"]:
                            search_result[item]["phone"] = contact_info["phone"]
                        add = False
                if add:
                    if contact_info['access_photo'] in ['TRUE', True, "True", "true"]:
                        if contact_info["image"] not in ['null', None, "None"]:
                            find_image = list(self.serve_file(self.index_image_file, contact_info["image"]))
                            if len(find_image) != 0:
                                search_result[item]["image"] = {
                                    "file_content": find_image[0]['file_content'],
                                    "file_type": find_image[0]['type'],
                                }
                    if contact_info['access_phone'] in ['TRUE', True, "True", "true"]:
                        search_result[item]["phone"] = contact_info["phone"]
                    search_result[item]["first_name"] = contact_info["first_name"]
                    search_result[item]["last_name"] = contact_info["last_name"]
                    search_result[item]["bio"] = contact_info["bio"]
                    search_result[item]["user_name"] = contact_info["user_name"]

            results = {"total": len(search_result), "result": list(search_result)}
        elif method == "select_user_by_username":
            user_name = str(data['user_name'])

            query = {"user_name": user_name}
            search_result = list(self.mongo.find(query=query, index_name=self.index_name, limit=1))
            for item in range(len(search_result)):
                del search_result[item]['pass_hash']
                del search_result[item]['pass_salt']
                del search_result[item]['category']

            results = {"total": len(search_result), "result": list(search_result)}
        else:
            raise PermissionError()

        return results

    def insert_business_flow(self, data, request, member, params=None):
        self.mongo.get_mongo_connection()
        # data = data['data']
        method = request["method"]
        if method == "add_contact":
            check_required_key(["contact_id"], data)
            data['user_id'] = member['_id']
            if "access_status" in list(data.keys()):
                if data['access_status']:
                    data['status'] = 'online'
            query = get_insert_check_query(data, service.contact_schema)
            if len(list(self.mongo.find(query=query, index_name=self.index_name))) != 0:
                raise DuplicatedConten()
            data["DC_CREATE_TIME"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
            data["last_update_date"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
            doc = check_full_schema(data, service.contact_schema)
            doc = preprocess(doc, service.contact_schema)
            insert_response = self.mongo.insert(index_name=self.index_name, document=doc, insert_type='insert_one')
            result = {"id": str(insert_response.inserted_id), "result": "inserted"}

        else:
            raise PermissionError()

        return result

    def delete_business_flow(self, data, request, member, params=None):
        self.mongo.get_mongo_connection()
        if request["method"] == "delete_content":

            query = {"contact_id": data['contact_id']}
            search_result = list(
                self.mongo.find(query=query, index_name=self.index_name, limit=1, projection={"user_id"}))
            if len(search_result) == 0:
                raise MemberNotFoundError()
            if search_result[0]['user_id'] != member['_id']:
                raise PermissionError()
            update_result = self.mongo.delete(index_name=self.index_name, id=search_result[0]['_id'],
                                              delete_type="delete_one")
            result = {"id": str(search_result[0]['_id']), "result": update_result.raw_result}

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
