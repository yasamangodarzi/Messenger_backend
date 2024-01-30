import datetime
from hashlib import md5

from helper.business_flow_helpers import BusinessFlow
from helper.config_helper import ConfigHelper
import members as service
from helper.io_helpers import *
from members.zero.utils.utils import *
import random


class UserBusinessFlowManager(BusinessFlow):
    def __init__(self, ):
        super(UserBusinessFlowManager, self).__init__(service.service_name)
        self.cfg_helper = ConfigHelper()

        self.index_image_file = self.cfg_helper.get_config(service.service_name)["index_image_file"]
        # self.index_transactions = self.create_index(
        #     self.cfg_helper.get_config(service.service_name)["transactions_index_name"])

    def select_business_flow(self, data, request, member, params=None):
        self.mongo.get_mongo_connection()

        if 'method' not in request.keys():
            raise RequiredFieldError("method")

        method = request["method"]
        if method == "select_user_info":
            user_id = str(data['user_id'])

            query = {"_id": user_id}
            search_result = list(self.mongo.find(query=query, index_name=self.index_name, limit=1))
            if len(search_result) == 0:
                raise MemberNotFoundError()

            if search_result[0]["image"] not in ['null', None, "None"]:
                find_image = list(self.serve_file(self.index_image_file, search_result[0]["image"]))
                if len(find_image) != 0:
                    search_result[0]["image"] = {
                        "file_content": find_image[0]['file_content'],
                        "file_type": find_image[0]['type'],

                    }

            del search_result[0]['pass_hash']
            del search_result[0]['pass_salt']
            del search_result[0]['category']

            results = {"total": len(search_result), "result": list(search_result)}
        elif method == "select_user_by_username":
            user_name = str(data['user_name'])

            query = {"user_name": user_name}
            search_result = list(self.mongo.find(query=query, index_name=self.index_name, limit=1))
            for item in range(len(search_result)):
                if search_result[item]["image"] not in ['null', None, "None"]:
                    find_image = list(self.serve_file(self.index_image_file, search_result[item]["image"]))
                    if len(find_image) != 0:
                        search_result[item]["image"] = {
                            "file_content": find_image[0]['file_content'],
                            "file_type": find_image[0]['type'],

                        }
                del search_result[item]['pass_hash']
                del search_result[item]['pass_salt']
                del search_result[item]['category']

            results = {"total": len(search_result), "result": list(search_result)}
        else:
            raise PermissionError()

        return results

    def insert_business_flow(self, data, request, member, params=None):
        # self.get_mongo_connection()
        # data = data['data']
        # method = request["method"]
        # if method == "charge_the_account":
        #     check_required_key(["amount"], data)
        #     amount = data["amount"]
        #     mobile = member['phone']
        #     email = member['email']
        #     response = send_request(amount,
        #                             f" شارژ حساب کاربری به مبلغ {amount} ریال ",
        #                             email=email,
        #                             mobile=mobile, )
        #     return {**response, "member_id": member["_id"]}
        # elif method == "verify_payment":
        #     check_required_key(["amount", 'authority'], data)
        #     _type = 'charge_wallet'
        #     amount = data["amount"]
        #     authority = data["authority"]
        #     res = verify(amount, authority)
        #     status = res['status']
        #     if status == 100 or status == 101:
        #         query = get_insert_check_query({
        #             "authority": authority,
        #             "type": _type,
        #             "payment": amount,
        #             "member_id": member["_id"]},
        #             service.transaction_schema)
        #         if len(list(self.index_transactions.find(query))) != 0:
        #             raise DuplicatedCharge()
        #         doc = check_full_schema({**member, "authority": authority,
        #                                  "type": _type,
        #                                  "payment": amount,
        #                                  "member_id": member["_id"]}, service.transaction_schema)
        #         doc = preprocess(doc, service.transaction_schema)
        #         insert_response = self.index_transactions.insert_one(
        #             {**doc, "_id": doc['member_id'] + "_" + doc['authority']})
        #         result = {"id": insert_response.inserted_id, "result": "inserted"}
        #         myquery = {"_id": doc['member_id']}
        #         wallet_balance = 0 if "wallet_balance" not in member else member["wallet_balance"]
        #         newvalues = {"$set": {"wallet_balance": wallet_balance + int(amount)}}
        #         self.index.update_one(myquery, newvalues)
        #         return result
        # else:
        raise PermissionError()

    # return []

    def delete_business_flow(self, data, request, member, params=None):
        self.mongo.get_mongo_connection()
        if request["method"] == "delete_user":
            if data["_id"] != member['_id']:
                raise PermissionError()
            update_result = self.mongo.delete(index_name=self.index_name, id=data['_id'], delete_type="delete_one")
            result = {"id": data["_id"], "result": update_result.raw_result}

            return result

    def update_business_flow(self, data, request, member, params=None):
        self.mongo.get_mongo_connection()
        if request["method"] == "update_user_info":
            data["last_update_date"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
            blocked_fields = ["category", "pass_salt", "pass_hash", "password"]
            _id = data["_id"]
            del data["_id"]
            data_keys = list(data.keys())
            for k in data_keys:
                if k in blocked_fields:
                    del data[k]
            if 'image' in data_keys:
                image_id = self.insert_file(self.index_image_file, data['image']['file_content'],
                                            data['image']['file_type'],
                                            member["_id"] + "@" + datetime.datetime.now().strftime(
                                                "%Y%m%d_%H:%M:%S.%f"))
                image_id = image_id.inserted_id
            else:
                image_id = None
            data['image'] = image_id
            check_schema(data, service.members_schema)
            data = preprocess(data, schema=service.members_schema)

            newvalues = {**data}

            update_result = self.mongo.update(index_name=self.index_name, id=_id, document=newvalues,
                                              update_type='update_one')

            result = {"id": _id, "result": update_result.raw_result}

            return result
        elif request["method"] == "change_password":
            check_required_key(["_id", "old_password", "new_password"], data)
            result = change_password(self, data, member)
            return result

        # elif request["method"] == "change_password":
        #     check_required_key(["member_id", "old_password", "new_password"], data)
        #     result = change_password(data, member, self.index)
        # elif request["method"] == "verify_email":
        #     otp_catch = self.db.cache("otp")
        #     otp = random.randint(1000, 9999)
        #     _id = str(uuid.uuid4())
        #     otp_catch.set(key=data["email"], timeout=20 * 60,
        #                   value=json.dumps({"correct": otp}))
        #     data["content"] = f'کد اعتبارسنجی شما :{otp}'
        #     send_email(data, "اعتبارسنجی ایمیل")
        # elif request["method"] == "check_otp_email":
        #     if "otp" not in data.keys():
        #         raise RequiredFieldError("otp")
        #     elif "email" not in data.keys():
        #         raise RequiredFieldError("email")
        #
        #     result = check_otp("email", data, self.db)
        #     if result["check"]:
        #         doc = {"_id": member["_id"],
        #                "verify_email": "TRUE",
        #                "email": data["email"]
        #                }
        #         result = update_member(mongo=self.index, data=doc)
        #     else:
        #         raise InvalidOtp()
        #
        # else:
        raise PermissionError()

    # return result


def change_password(self, data, member):
    if data["_id"] != member['_id']:
        raise PermissionError()

    old_password = data["old_password"]
    md5_password = md5(old_password.encode()).hexdigest().upper()

    login_member = {"_source": member, "_id": member["_id"]}
    if not check_password(password=md5_password, member=login_member) \
            and not check_password(password=old_password, member=login_member):
        raise InvalidCurrentPassword()

    update_result = set_new_password(self, new_password=data["new_password"], member_id=member["_id"])

    result = {"id": update_result["_id"], "result": update_result["result"]}
    return result


def set_new_password(self, new_password, member_id):
    if len(new_password) < 8:
        raise InvalidPasswordStructure()

    md5_password = md5(new_password.encode()).hexdigest().upper()
    pass_salt, pass_hash = create_salt_and_hash(md5_password)
    update_body = {
        "pass_salt": pass_salt,
        "pass_hash": pass_hash

    }
    newvalues = {**update_body}

    update_result = self.mongo.update(index_name=self.index_name, id=member_id, document=newvalues,
                                      update_type='update_one')

    update_result = {"_id": member_id, "result": update_result.raw_result}
    return update_result
