import uuid
from hashlib import md5
import members as service
from helper.business_flow_helpers import BusinessFlow
import random

from helper.config_helper import ConfigHelper
from helper.io_helpers import *

from helper.io_helpers import check_full_schema, preprocess, RequiredFieldError, check_schema
from members.zero.utils.utils import *
from walrus import *


class FreeBusinessFlowManager(BusinessFlow):
    def __init__(self, ):
        super(FreeBusinessFlowManager, self).__init__(service.service_name)

        self.cfg_helper = ConfigHelper()

        self.index = self.mongo.create_index(self.cfg_helper.get_config(service.service_name)["index_name"])

        redis_host = self.cfg_helper.get_config("REDIS")["redis_host"]
        redis_port = self.cfg_helper.get_config("REDIS")["redis_port"]
        redis_db_number = self.cfg_helper.get_config("REDIS")["redis_db_number"]

        self.db = Database(redis_host, redis_port, redis_db_number)

    def select_business_flow(self, data, request, member, params=None):
        self.mongo.get_mongo_connection()

        method = request["method"]

        if method == "select":
            pass
        else:
            raise PermissionError()

        results = []
        return results

    def insert_business_flow(self, data, request, member, params=None):
        self.mongo.get_mongo_connection()

        if request["method"] == "register":
            check_required_key(['password_confirm', 'password', "user_name", "phone"], data)
            data["phone"] = (data["phone"]).replace(" ", "")
            new_pass = data["password"]
            new_pass_confirm = data["password_confirm"]
            if new_pass != new_pass_confirm:
                raise PermissionError()

            if len(new_pass) < 8:
                raise InvalidPasswordStructure()

            md5_password = md5(new_pass.encode()).hexdigest().upper()
            data["pass_salt"], data["pass_hash"] = service.create_salt_and_hash(md5_password)
            data["DC_CREATE_TIME"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
            data = check_full_schema(data, service.members_schema)
            data = preprocess(data, schema=service.members_schema)
            query = get_insert_check_query(data, service.members_schema)

            if len(list(self.mongo.find(query=query, index_name=self.index_name))) != 0:
                raise DuplicatedMember()

            insert_id = self.mongo.insert({**data, "_id": data["phone"]}, self.index_name, 'insert_one')
            if insert_id:
                result = {"status": "inserted_person"}
            else:
                result = {"status": "not_inserted_person"}


        else:
            raise PermissionError()

        return result

    def delete_business_flow(self, data, request, member, params=None):
        raise PermissionError()

    def update_business_flow(self, data, request, member, params=None):
        pass
    # self.mongo.get_mongo_connection()
    # result = {}
    # data = data['data']
    #
    # if request["method"] == "update":
    #     check_schema(data, service.members_schema)
    #     data = preprocess(data, schema=service.members_schema)
    #     result = update_member(data, member)
    #
    # if request["method"] == "change_password":
    #     check_required_key(["member_id", "old_password", "new_password"], data)
    #     result = change_password(data, member, self.index)
    #
    #
    # elif request["method"] == "check_verification_code_email":
    #     if "verification_code" not in data.keys():
    #         raise RequiredFieldError("verification_code")
    #     elif "email" not in data.keys():
    #         raise RequiredFieldError("email")
    #     result = check_verification_code("email", data, self.db)
    #     if result["check"]:
    #         doc = {"_id": member["_id"],
    #                "verify_email": "TRUE",
    #                "email": data["email"]
    #                }
    #         result = update_member(mongo=self.index, data=doc)
    #     else:
    #         raise InvalidVerificationCode()
    #
    #
    # elif request["method"] == "verify_email":
    #     verification_code_catch = self.db.cache("otp_forget_password")
    #     verification_code = random.randint(1000, 9999)
    #     _id = str(uuid.uuid4())
    #     verification_code_catch.set(key=data["email"], timeout=20 * 60,
    #                                 value=json.dumps({"correct": verification_code}))
    #     data["content"] = f'کد اعتبارسنجی شما :{verification_code}'
    #     return send_email(data, "اعتبارسنجی ایمیل")
    #
    #
    # else:
    #     raise PermissionError()
