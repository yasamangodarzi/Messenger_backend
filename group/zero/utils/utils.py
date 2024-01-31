# import base64
# from hashlib import sha256
# from uuid import uuid4
#
# from helper.config_helper import ConfigHelper
# from helper.database_helper import MongoDB
# from helper.io_helpers import MemberNotFoundError, RequiredFieldError, UserInputError
# from members import cfg_helper
# import members as service
#
#
# def get_member(mongo, request_sender_id):
#     query = {"_id": request_sender_id}
#     mongo = MongoDB()
#     mongo.get_mongo_connection()
#     search_result = list(mongo.find(index_name=cfg_helper.get_config(service.service_name)["index_name"], query=query))
#
#     if len(search_result) != 1:
#         raise MemberNotFoundError()
#
#     return search_result[0]
#
#
# def create_salt_and_hash(md5_password):
#     salt = str(uuid4())
#
#     bytes_obj = (md5_password + salt).encode("utf-16-le")
#
#     sha_digest = sha256(bytes_obj).digest()
#     _hash = base64.b64encode(sha_digest).decode()
#
#     return salt, _hash
#
#
from contact import cfg_helper
from helper.config_helper import ConfigHelper
from helper.database_helper import MongoDB
from helper.io_helpers import UserInputError, RequiredFieldError, MemberNotFoundError
import contact as service

def get_insert_check_query(data, schema):
    query = {}
    for key in data.keys():
        if key not in schema.keys():
            continue
        if "_check_in_insert" in schema[key].keys() and schema[key]["_check_in_insert"] is False:
            continue
        else:
            query.update({key: data[key]})
    return query


def get_contact(request_sender_id):
    query = {"user_id": request_sender_id}
    mongo = MongoDB()
    mongo.get_mongo_connection()
    search_result = list(mongo.find(index_name=cfg_helper.get_config(service.service_name)["index_name"], query=query))

    return search_result



def check_required_key(required_keys, data):
    for required_key in required_keys:
        if required_key not in data.keys():
            raise RequiredFieldError(required_key)

#
# def check_password(password, member):
#     real_hash = member["_source"]["pass_hash"]
#
#     bytes_obj = (password + member["_source"]["pass_salt"]).encode("utf-16-le")
#
#     sha_digest = sha256(bytes_obj).digest()
#     pass_hash = base64.b64encode(sha_digest)
#
#     if pass_hash.decode() == real_hash:
#         return True
#     else:
#         return False
#
#
# class InvalidPasswordStructure(UserInputError):
#     def __init__(self):
#         cfg_helper = ConfigHelper()
#         error_code_base = int(cfg_helper.get_config("CUSTOM_ERROR_CODES")["members"])
#         super(InvalidPasswordStructure, self).__init__(message="Password structure is invalid",
#                                                        error_code=error_code_base + 104)
#
#
class IncorrectType(UserInputError):
    def __init__(self):
        cfg_helper = ConfigHelper()
        error_code_base = int(cfg_helper.get_config("CUSTOM_ERROR_CODES")["group"])
        super(IncorrectType, self).__init__(message="wrong type",
                                               error_code=error_code_base + 102,
                                               persian_massage="مقدار فیلد type اشتباه است.")

#
# class IncorrectLoginData(UserInputError):
#     def __init__(self, msg):
#         cfg_helper = ConfigHelper()
#         error_code_base = int(cfg_helper.get_config("CUSTOM_ERROR_CODES")["members"])
#         super(IncorrectLoginData, self).__init__(message=msg, error_code=error_code_base + 101,
#                                                  persian_massage='نام کاربری یا رمز عبور اشتباه است.')
#
#
class DuplicatedGroup(UserInputError):
    def __init__(self):
        cfg_helper = ConfigHelper()
        error_code_base = int(cfg_helper.get_config("CUSTOM_ERROR_CODES")["group"])
        super(DuplicatedGroup, self).__init__(message="Group is already register ",
                                                 error_code=error_code_base + 102,
                                                 persian_massage="همچین اسم گروهی موجود است")
#
#
# class InvalidCurrentPassword(UserInputError):
#     def __init__(self):
#         cfg_helper = ConfigHelper()
#         error_code_base = int(cfg_helper.get_config("CUSTOM_ERROR_CODES")["members"])
#         super(InvalidCurrentPassword, self).__init__(message="Current password is invalid",
#                                                      error_code=error_code_base + 103,
#                                                      persian_massage="پسورد فعلی اشتباه وارد شده است."
#                                                      )
