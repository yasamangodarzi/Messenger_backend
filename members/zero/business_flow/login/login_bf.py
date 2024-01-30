from helper.config_helper import ConfigHelper
from helper.business_flow_helpers import BusinessFlow
from hashlib import md5
from uuid import uuid4
import members as service
from helper.io_helpers import RequiredFieldError, preprocess


class LoginBusinessFlowManager(BusinessFlow):
    def __init__(self, ):
        super(LoginBusinessFlowManager, self).__init__(service.service_name)
        self.cfg_helper = ConfigHelper()

        self.index = self.mongo.create_index(self.cfg_helper.get_config(service.service_name)["index_name"])

    def login_business_flow(self, data, request):
        self.mongo.get_mongo_connection()

        if 'method' not in request.keys():
            raise RequiredFieldError("method")

        method = request["method"]
        if method == "login":
            if "user" not in data.keys():
                raise RequiredFieldError("user")
            if "pass" not in data.keys():
                raise RequiredFieldError("pass")

            data = preprocess(data, service.members_schema)
            resp = self.method_login(data=data)

        else:
            raise PermissionError()

        return resp

    def method_login(self, data):
        username = data["user"]
        can_login_with_username, member = self.login_with_username(data=data, username=username)

        if not can_login_with_username:
            raise service.IncorrectLoginData('Incorrect username or password')

        resp = {
                "member_id": member["_id"],
                "member_type": member["_source"]["category"],
                # "member_first_name": member["_source"]["first_name"],
                # "member_last_name": member["_source"]["last_name"],
                # "member_username": member["_source"]["user_name"],
                "member_phone": member["_source"]["phone"],
                }

        return resp

    def login_with_username(self, data, username):
        login_result = False
        query = {"user_name": username}
        search_result = list(self.mongo.find(query=query, index_name=self.index_name))

        member = {"_source": None, "_id": None}

        if len(search_result) == 1:
            member = {"_source": search_result[0],
                      "_id": search_result[0]["_id"]}

        if member["_source"] is not None and member["_source"]["pass_hash"] != 'null':
            raw_password = data["pass"]
            md5_password = md5(raw_password.encode()).hexdigest().upper()
            login_result = service.check_password(raw_password, member)
            if login_result is False:
                login_result = service.check_password(md5_password, member)

        return login_result, member
