import datetime
from hashlib import md5
from helper.business_flow_helpers import BusinessFlow
from helper.config_helper import ConfigHelper
from helper.io_helpers import *
from group.zero.utils.utils import *
import random

from members import get_member
import group as service


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
        if method == "select_group":
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
        elif method == "select_pv_info":
            contact_id = str(data['contact_id'])
            user_id = request['member_id']
            query = {"group_user_name": f"pv.{user_id}.{contact_id}", "type": "pv"}
            search_result = list(self.mongo.find(query=query, index_name=self.index_name, limit=1))
            if len(search_result) == 0:
                query = {"group_user_name": f"pv.{contact_id}.{user_id}", "type": "pv"}
                search_result = list(self.mongo.find(query=query, index_name=self.index_name, limit=1))
                if len(search_result) == 0:
                    raise PermissionError()

            results = {"total": len(search_result), "result": list(search_result)}
        else:
            raise PermissionError()

        return results

    def insert_business_flow(self, data, request, member, params=None):
        self.mongo.get_mongo_connection()
        # data = data['data']
        method = request["method"]
        if method == "create_group":
            if 'type' not in list(data.keys()):
                raise RequiredFieldError("type")
            if data['type'] == 'pv':
                if len(data['member_ids']) != 1:
                    raise IncorrectType()
                user_id = request['member_id']
                member_id = data['member_ids'][0]
                data['admin_ids'] = [user_id, member_id]
                data['user_ids'] = [user_id, member_id]
                data['group_user_name'] = f'pv.{user_id}.{member_id}'
            elif data['type'] == 'group':
                if 'group_name' not in list(data.keys()):
                    raise RequiredFieldError("group_name")
                if 'group_user_name' not in list(data.keys()):
                    raise RequiredFieldError("group_user_name")
                data['admin_ids'] = [request['member_id']]
                data['user_ids'] = [request['member_id']]
                for member in data['member_ids']:
                    data['user_ids'].append(member)
            del data['member_ids']

            query = get_insert_check_query(data, service.group_schema)
            if len(list(self.mongo.find(query=query, index_name=self.index_name))) != 0:
                raise DuplicatedGroup()
            data["DC_CREATE_TIME"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
            data["last_update_date"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
            doc = check_full_schema(data, service.group_schema)
            doc = preprocess(doc, service.group_schema)
            insert_response = self.mongo.insert(index_name=self.index_name, document=doc, insert_type='insert_one')
            result = {"id": str(insert_response.inserted_id), "result": "inserted"}
        elif method == "add_new_member":
            if 'group_user_name' not in list(data.keys()):
                raise RequiredFieldError("group_user_name")
            query = {"group_user_name": data['group_user_name']}
            search_result = list(self.mongo.find(query=query, index_name=self.index_name))
            if len(search_result) == 0:
                raise DosenotExistGroup()
            if search_result[0]['type'] == "pv":
                raise PermissionError()
            user_ids_list = search_result[0]['user_ids']
            for member in data['member_ids']:
                user_ids_list.append(member)
            doc = check_full_schema({"user_ids": user_ids_list}, service.contact_schema)
            doc = preprocess(doc, service.group_schema)
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
