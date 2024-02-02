import datetime

import chat
from helper.business_flow_helpers import BusinessFlow
from helper.io_helpers import *
from group.zero.utils.utils import *
import group as service


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
        if method == "group_info":
            group_user_name = data.get("group_user_name", None)
            if group_user_name in ['null', None]:
                raise DosenotExistGroup()
            query = {"group_user_name": group_user_name}
            search_result = list(self.mongo.find(query=query, index_name=self.index_name))
            if len(search_result) == 0:
                raise DosenotExistGroup()
            search_result[0]['_id'] = str(search_result[0]['_id'])
            results = {"total": len(search_result), "result": list(search_result)}

        else:
            raise PermissionError()

        return results

    def insert_business_flow(self, data, request, member, params=None):
        self.mongo.get_mongo_connection()
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
        elif request["method"] == "add_new_message":
            if 'group_user_name' not in list(data.keys()):
                raise RequiredFieldError("group_user_name")
            query = {"group_user_name": data['group_user_name']}
            search_result = list(self.mongo.find(query=query, index_name=self.index_name))
            if len(search_result) == 0:
                raise DosenotExistGroup()
            data['sender'] = request['member_id']
            data['receiver'] = []
            data["DC_CREATE_TIME"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
            data["last_update_date"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
            for item in search_result[0]['user_ids']:
                data['receiver'].append(item)
            for item in search_result[0]['admin_ids']:
                if item not in search_result[0]['user_ids']:
                    data['receiver'].append(item)
            data['chat_id'] = data['group_user_name']
            doc = check_full_schema(data, chat.message_schema)
            doc = preprocess(doc, chat.message_schema)
            insert_response = self.mongo.insert(index_name=self.message_index_name, document=doc,
                                                insert_type='insert_one')
            result = {"id": str(insert_response.inserted_id), "result": "inserted"}


        else:
            raise PermissionError()

        return result

    def delete_business_flow(self, data, request, member, params=None):
        self.mongo.get_mongo_connection()
        if request["method"] == "delete_group":

            query = {"group_user_name": data['group_user_name']}
            search_result = list(self.mongo.find(query=query, index_name=self.index_name, limit=1))
            if len(search_result) == 0:
                raise DosenotExistGroup()
            admin_ids_list = search_result[0]['admin_ids']
            if request['member_id'] not in admin_ids_list:
                raise PermissionError()
            update_result = self.mongo.delete(index_name=self.index_name, id=search_result[0]['_id'],
                                              delete_type="delete_one")
            result = {"id": str(search_result[0]['_id']), "result": update_result.raw_result}

            return result
        elif request["method"] == "delete_user":

            query = {"group_user_name": data['group_user_name']}
            search_result = list(self.mongo.find(query=query, index_name=self.index_name, limit=1))
            if len(search_result) == 0:
                raise DosenotExistGroup()
            admin_ids_list = search_result[0]['admin_ids']
            if request['member_id'] not in admin_ids_list:
                raise PermissionError()
            if data['user_id'] in search_result[0]["user_ids"]:
                user_list = search_result[0]['user_ids']
                user_list.remove(data['user_id'])

                doc = {"user_ids": user_list}
                check_schema(doc, service.group_schema)
                doc = preprocess(doc, schema=service.group_schema)

                newvalues = {**doc}

                update_result = self.mongo.update(index_name=self.index_name, id=search_result[0]['_id'],
                                                  document=newvalues,
                                                  update_type='update_one')
                result = {"id": str(search_result[0]['_id']), "result": update_result.raw_result}
            return result

    def update_business_flow(self, data, request, member, params=None):
        self.mongo.get_mongo_connection()
        if request["method"] == "add_new_member":
            if 'group_user_name' not in list(data.keys()):
                raise RequiredFieldError("group_user_name")
            query = {"group_user_name": data['group_user_name']}
            search_result = list(self.mongo.find(query=query, index_name=self.index_name))
            if len(search_result) == 0:
                raise DosenotExistGroup()
            if search_result[0]['type'] == "pv":
                raise PermissionError()
            user_ids_list = search_result[0]['user_ids']
            admin_ids_list = search_result[0]['admin_ids']
            if request['member_id'] not in admin_ids_list:
                raise PermissionError()
            for member in data['member_ids']:
                if member not in user_ids_list:
                    user_ids_list.append(member)

            doc = {"user_ids": user_ids_list}
            check_schema(doc, service.group_schema)
            doc = preprocess(doc, schema=service.group_schema)

            newvalues = {**doc}

            update_result = self.mongo.update(index_name=self.index_name, id=search_result[0]['_id'],
                                              document=newvalues,
                                              update_type='update_one')
            result = {"id": str(search_result[0]['_id']), "result": update_result.raw_result}
            return result

        raise PermissionError()

    # return result
