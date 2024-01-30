from helper.business_flow_helpers import BusinessFlow
from helper.config_helper import ConfigHelper
from walrus import *
import members as service
from helper.io_helpers import *
from members.zero.utils.utils import *
import random


class UserBusinessFlowManager(BusinessFlow):
    def __init__(self, ):
        super(UserBusinessFlowManager, self).__init__(service.service_name)
        self.cfg_helper = ConfigHelper()
        # self.index = self.create_index(self.cfg_helper.get_config(service.service_name)["index_name"])
        # self.index_transactions = self.create_index(
        #     self.cfg_helper.get_config(service.service_name)["transactions_index_name"])

        redis_host = self.cfg_helper.get_config("REDIS")["redis_host"]
        redis_port = self.cfg_helper.get_config("REDIS")["redis_port"]
        redis_db_number = self.cfg_helper.get_config("REDIS")["redis_db_number"]

        self.db = Database(redis_host, redis_port, redis_db_number)

    def select_business_flow(self, data, request, member, params=None):
        self.mongo.get_mongo_connection()

        if 'method' not in request.keys():
            raise RequiredFieldError("method")

        method = request["method"]
        if method == "select_user_info":
            user_id = str(data['user_id'])
            if not user_id.startswith('0'):
                user_id = "0" + str(data['user_id'])
            query = {"_id": user_id}
            search_result = list(self.mongo.find(query=query, index_name=self.index_name, limit=1))
            del search_result[0]['pass_hash']
            del search_result[0]['pass_salt']
            del search_result[0]['category']

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
        raise PermissionError()

    def update_business_flow(self, data, request, member, params=None):
        # self.get_mongo_connection()
        # result = {}
        # data = data['data']
        # if request["method"] == "update":
        #     if 'email' in data.keys():
        #         data['verify_email'] = "FALSE"
        #
        #     check_schema(data, service.clubmembers_schema)
        #     data = preprocess(data, schema=service.clubmembers_schema)
        #
        #     result = update_member(data, member)
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
