import datetime
import importlib
import sys

import jwt
from flask import Flask, Blueprint, jsonify
from flask import request as request_flask

from helper.communication_helpers import clear_response
from helper.config_helper import ConfigHelper
from helper.io_helpers import RequiredFieldError

app = Flask(__name__)

user_blueprint = Blueprint('api', __name__, url_prefix='/StudentScientificSociety/api')


@user_blueprint.route('/register', methods=['POST'])
def user_register():
    cfg_helper = ConfigHelper()
    method_type = "register"
    try:
        order_data = request_flask.json
        if 'service' not in order_data.keys():
            raise RequiredFieldError("service")
        index = order_data['service']
        api_key = order_data['api_key']
        config_key = index.upper()
        if config_key not in cfg_helper.config.keys():
            raise RequiredFieldError("service")
        order_data['data']['method'] = method_type
        dynamic_module = importlib.import_module(config_key.lower())

        class_ = config_key.split("_")
        class_name = ''
        for j in class_:
            class_name += (j[0].upper() + j[1:].lower())
        source = authenticate(api_key)
        if source is None:
            raise NotAuthenticatedException()
        size = 1000 if "size" not in order_data else order_data["size"]
        from_ = 0 if "from" not in order_data else order_data["from"]
        request_ = {"broker_type": cfg_helper.get_config("DEFAULT")["broker_type"], "source": source,
                    "method": method_type, "ip": request_flask.remote_addr, "api_key": api_key, "size": size,
                    "from": from_,
                    "member_id": '090000000', "data": order_data["data"]
                    }

        worker = getattr(dynamic_module, "MembersInsertWorker")
        response = clear_response(worker().serve_request(request_))
        if not response['is_successful']:
            return jsonify({"status": response['error_code'], "method_type": method_type,
                            "response": response, 'error_description': response['error_description']})
        else:
            return jsonify({"status": 200, "method_type": method_type, "response": response})
    except NotAuthenticatedException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except NotAuthorizedException as e:
        return jsonify({"status": 405, "method_type": method_type, "error": str(e)})
    except PermissionDeniedException as e:
        return jsonify({"status": 403, "method_type": method_type, "error": str(e)})
    except RequiredFieldError as e:
        return jsonify({"status": e.error_code, "method_type": method_type, "error": str(e)})
    except InvalidInputException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except KeyError as e:
        return jsonify({"status": 401, "method_type": method_type,
                        "error": "key %s is not passed" % str(e)})
    except:
        return jsonify({"status": 500, "method_type": None, "error": "General Error"})


@user_blueprint.route('/login', methods=['POST'])
def user_login():
    cfg_helper = ConfigHelper()
    method_type = "login"
    try:
        order_data = request_flask.json
        if 'service' not in order_data.keys():
            raise RequiredFieldError("service")
        index = order_data['service']
        api_key = order_data['api_key']
        config_key = index.upper()
        if config_key not in cfg_helper.config.keys():
            raise RequiredFieldError("service")
        order_data['data']['method'] = method_type
        dynamic_module = importlib.import_module(config_key.lower())

        class_ = config_key.split("_")
        class_name = ''
        for j in class_:
            class_name += (j[0].upper() + j[1:].lower())
        source = authenticate(api_key)
        if source is None:
            raise NotAuthenticatedException()
        size = 1000 if "size" not in order_data else order_data["size"]
        from_ = 0 if "from" not in order_data else order_data["from"]
        request_ = {"broker_type": cfg_helper.get_config("DEFAULT")["broker_type"], "source": source,
                    "method": method_type, "ip": request_flask.remote_addr, "api_key": api_key, "size": size,
                    "from": from_, "member_id": '', "data": order_data["data"]
                    }

        worker = getattr(dynamic_module, "MembersLoginWorker")
        response = clear_response(worker().serve_request(request_))
        payload = {'member_id': response['member_id']}
        jwt_token = create_jwt_token(payload)
        jwt_token_str = jwt_token.decode('utf-8')
        if not response['is_successful']:
            return jsonify({"status": response['error_code'], "method_type": method_type,
                            "response": response, 'error_description': response['error_description']})
        else:
            return jsonify({"status": 200, "token": jwt_token_str, "method_type": method_type, "response": response})
    except NotAuthenticatedException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except NotAuthorizedException as e:
        return jsonify({"status": 405, "method_type": method_type, "error": str(e)})
    except PermissionDeniedException as e:
        return jsonify({"status": 403, "method_type": method_type, "error": str(e)})
    except RequiredFieldError as e:
        return jsonify({"status": e.error_code, "method_type": method_type, "error": str(e)})
    except InvalidInputException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except KeyError as e:
        return jsonify({"status": 401, "method_type": method_type,
                        "error": "key %s is not passed" % str(e)})
    except:
        return jsonify({"status": 500, "method_type": None, "error": "General Error"})


# User
user_auth_blueprint = Blueprint('user', __name__, url_prefix='/StudentScientificSociety/api/user')


@user_auth_blueprint.route('/<string:user_id>', methods=['GET'])
def user_info(user_id):
    cfg_helper = ConfigHelper()
    method_type = 'select_user_info'
    try:
        order_data = request_flask.json
        if 'service' not in order_data.keys():
            raise RequiredFieldError("service")
        index = order_data['service']
        api_key = order_data['api_key']
        if 'token' not in order_data.keys():
            raise RequiredFieldError("token")
        token = order_data['token']
        payload = authorize(api_key, token)
        config_key = index.upper()
        if config_key not in cfg_helper.config.keys():
            raise RequiredFieldError("service")
        order_data['data']['method'] = method_type
        dynamic_module = importlib.import_module(config_key.lower())

        class_ = config_key.split("_")
        class_name = ''
        for j in class_:
            class_name += (j[0].upper() + j[1:].lower())
        source = authenticate(api_key)
        order_data["data"]['user_id'] = user_id
        if source is None:
            raise NotAuthenticatedException()
        if payload['member_id'] != user_id:
            raise NotAuthenticatedException()

        size = 1000 if "size" not in order_data else order_data["size"]
        from_ = 0 if "from" not in order_data else order_data["from"]
        request_ = {"broker_type": cfg_helper.get_config("DEFAULT")["broker_type"], "source": source,
                    "method": method_type, "ip": request_flask.remote_addr, "api_key": api_key, "size": size,
                    "from": from_, "member_id": payload['member_id'], "data": order_data["data"]
                    }

        worker = getattr(dynamic_module, "MembersSelectWorker")
        response = clear_response(worker().serve_request(request_))
        if not response['is_successful']:
            return jsonify({"status": response['error_code'], "method_type": method_type,
                            "response": response, 'error_description': response['error_description']})
        else:
            return jsonify({"status": 200, "method_type": method_type, "response": response})
    except NotAuthenticatedException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except NotAuthorizedException as e:
        return jsonify({"status": 405, "method_type": method_type, "error": str(e)})
    except PermissionDeniedException as e:
        return jsonify({"status": 403, "method_type": method_type, "error": str(e)})
    except RequiredFieldError as e:
        return jsonify({"status": e.error_code, "method_type": method_type, "error": str(e)})
    except InvalidInputException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except KeyError as e:
        return jsonify({"status": 401, "method_type": method_type,
                        "error": "key %s is not passed" % str(e)})
    except:
        return jsonify({"status": 500, "method_type": None, "error": "General Error"})


@user_auth_blueprint.route('/<string:user_id>', methods=['PATCH'])
def change_user_info(user_id):
    cfg_helper = ConfigHelper()
    method_type = 'update_user_info'
    try:
        order_data = request_flask.json
        if 'service' not in order_data.keys():
            raise RequiredFieldError("service")
        index = order_data['service']
        api_key = order_data['api_key']
        if 'token' not in order_data.keys():
            raise RequiredFieldError("token")
        token = order_data['token']
        payload = authorize(api_key, token)
        config_key = index.upper()
        if config_key not in cfg_helper.config.keys():
            raise RequiredFieldError("service")
        dynamic_module = importlib.import_module(config_key.lower())

        class_ = config_key.split("_")
        class_name = ''
        for j in class_:
            class_name += (j[0].upper() + j[1:].lower())
        source = authenticate(api_key)
        order_data["data"]['_id'] = user_id
        if source is None:
            raise NotAuthenticatedException()
        if payload['member_id'] != user_id:
            raise NotAuthenticatedException()

        size = 1000 if "size" not in order_data else order_data["size"]
        from_ = 0 if "from" not in order_data else order_data["from"]
        request_ = {"broker_type": cfg_helper.get_config("DEFAULT")["broker_type"], "source": source,
                    "method": method_type, "ip": request_flask.remote_addr, "api_key": api_key, "size": size,
                    "from": from_, "member_id": payload['member_id'], "data": order_data["data"]
                    }

        worker = getattr(dynamic_module, "MembersUpdateWorker")
        response = clear_response(worker().serve_request(request_))
        if not response['is_successful']:
            return jsonify({"status": response['error_code'], "method_type": method_type,
                            "response": response, 'error_description': response['error_description']})
        else:
            return jsonify({"status": 200, "method_type": method_type, "response": response})
    except NotAuthenticatedException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except NotAuthorizedException as e:
        return jsonify({"status": 405, "method_type": method_type, "error": str(e)})
    except PermissionDeniedException as e:
        return jsonify({"status": 403, "method_type": method_type, "error": str(e)})
    except RequiredFieldError as e:
        return jsonify({"status": e.error_code, "method_type": method_type, "error": str(e)})
    except InvalidInputException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except KeyError as e:
        return jsonify({"status": 401, "method_type": method_type,
                        "error": "key %s is not passed" % str(e)})
    except:
        return jsonify({"status": 500, "method_type": None, "error": "General Error"})


@user_auth_blueprint.route('/<string:user_id>', methods=['PUT'])
def change_password(user_id):
    cfg_helper = ConfigHelper()
    method_type = 'change_password'
    try:
        order_data = request_flask.json
        if 'service' not in order_data.keys():
            raise RequiredFieldError("service")
        index = order_data['service']
        api_key = order_data['api_key']
        if 'token' not in order_data.keys():
            raise RequiredFieldError("token")
        token = order_data['token']
        payload = authorize(api_key, token)
        config_key = index.upper()
        if config_key not in cfg_helper.config.keys():
            raise RequiredFieldError("service")
        dynamic_module = importlib.import_module(config_key.lower())

        class_ = config_key.split("_")
        class_name = ''
        for j in class_:
            class_name += (j[0].upper() + j[1:].lower())
        source = authenticate(api_key)
        order_data["data"]['_id'] = user_id
        if source is None:
            raise NotAuthenticatedException()
        if payload['member_id'] != user_id:
            raise NotAuthenticatedException()

        size = 1000 if "size" not in order_data else order_data["size"]
        from_ = 0 if "from" not in order_data else order_data["from"]
        request_ = {"broker_type": cfg_helper.get_config("DEFAULT")["broker_type"], "source": source,
                    "method": method_type, "ip": request_flask.remote_addr, "api_key": api_key, "size": size,
                    "from": from_, "member_id": payload['member_id'], "data": order_data["data"]
                    }

        worker = getattr(dynamic_module, "MembersUpdateWorker")
        response = clear_response(worker().serve_request(request_))
        if not response['is_successful']:
            return jsonify({"status": response['error_code'], "method_type": method_type,
                            "response": response, 'error_description': response['error_description']})
        else:
            return jsonify({"status": 200, "method_type": method_type, "response": response})
    except NotAuthenticatedException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except NotAuthorizedException as e:
        return jsonify({"status": 405, "method_type": method_type, "error": str(e)})
    except PermissionDeniedException as e:
        return jsonify({"status": 403, "method_type": method_type, "error": str(e)})
    except RequiredFieldError as e:
        return jsonify({"status": e.error_code, "method_type": method_type, "error": str(e)})
    except InvalidInputException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except KeyError as e:
        return jsonify({"status": 401, "method_type": method_type,
                        "error": "key %s is not passed" % str(e)})
    except:
        return jsonify({"status": 500, "method_type": None, "error": "General Error"})


@user_auth_blueprint.route('/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    cfg_helper = ConfigHelper()
    method_type = 'delete_user'
    try:
        order_data = request_flask.json
        if 'service' not in order_data.keys():
            raise RequiredFieldError("service")
        index = order_data['service']
        api_key = order_data['api_key']
        if 'token' not in order_data.keys():
            raise RequiredFieldError("token")
        token = order_data['token']
        payload = authorize(api_key, token)
        config_key = index.upper()
        if config_key not in cfg_helper.config.keys():
            raise RequiredFieldError("service")
        dynamic_module = importlib.import_module(config_key.lower())

        class_ = config_key.split("_")
        class_name = ''
        for j in class_:
            class_name += (j[0].upper() + j[1:].lower())
        source = authenticate(api_key)
        order_data["data"]['_id'] = user_id
        if source is None:
            raise NotAuthenticatedException()
        if payload['member_id'] != user_id:
            raise NotAuthenticatedException()

        size = 1000 if "size" not in order_data else order_data["size"]
        from_ = 0 if "from" not in order_data else order_data["from"]
        request_ = {"broker_type": cfg_helper.get_config("DEFAULT")["broker_type"], "source": source,
                    "method": method_type, "ip": request_flask.remote_addr, "api_key": api_key, "size": size,
                    "from": from_, "member_id": payload['member_id'], "data": order_data["data"]
                    }

        worker = getattr(dynamic_module, "MembersDeleteWorker")
        response = clear_response(worker().serve_request(request_))
        if not response['is_successful']:
            return jsonify({"status": response['error_code'], "method_type": method_type,
                            "response": response, 'error_description': response['error_description']})
        else:
            return jsonify({"status": 200, "method_type": method_type, "response": response})
    except NotAuthenticatedException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except NotAuthorizedException as e:
        return jsonify({"status": 405, "method_type": method_type, "error": str(e)})
    except PermissionDeniedException as e:
        return jsonify({"status": 403, "method_type": method_type, "error": str(e)})
    except RequiredFieldError as e:
        return jsonify({"status": e.error_code, "method_type": method_type, "error": str(e)})
    except InvalidInputException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except KeyError as e:
        return jsonify({"status": 401, "method_type": method_type,
                        "error": "key %s is not passed" % str(e)})
    except:
        return jsonify({"status": 500, "method_type": None, "error": "General Error"})


@user_auth_blueprint.route('/', methods=['GET'])
def search():
    cfg_helper = ConfigHelper()
    method_type = 'select_user_by_username'
    try:
        order_data = request_flask.json
        order_data["data"]['user_name'] = request_flask.args.get('keyword')
        if 'service' not in order_data.keys():
            raise RequiredFieldError("service")
        index = order_data['service']
        api_key = order_data['api_key']
        if 'token' not in order_data.keys():
            raise RequiredFieldError("token")
        token = order_data['token']
        payload = authorize(api_key, token)
        config_key = index.upper()
        if config_key not in cfg_helper.config.keys():
            raise RequiredFieldError("service")
        order_data['data']['method'] = method_type
        dynamic_module = importlib.import_module(config_key.lower())
        class_ = config_key.split("_")
        class_name = ''
        for j in class_:
            class_name += (j[0].upper() + j[1:].lower())
        source = authenticate(api_key)
        if source is None:
            raise NotAuthenticatedException()

        size = 1000 if "size" not in order_data else order_data["size"]
        from_ = 0 if "from" not in order_data else order_data["from"]
        request_ = {"broker_type": cfg_helper.get_config("DEFAULT")["broker_type"], "source": source,
                    "method": method_type, "ip": request_flask.remote_addr, "api_key": api_key, "size": size,
                    "from": from_, "member_id": payload['member_id'], "data": order_data["data"]
                    }

        worker = getattr(dynamic_module, "MembersSelectWorker")
        response = clear_response(worker().serve_request(request_))
        if not response['is_successful']:
            return jsonify({"status": response['error_code'], "method_type": method_type,
                            "response": response, 'error_description': response['error_description']})
        else:
            return jsonify({"status": 200, "method_type": method_type, "response": response})
    except NotAuthenticatedException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except NotAuthorizedException as e:
        return jsonify({"status": 405, "method_type": method_type, "error": str(e)})
    except PermissionDeniedException as e:
        return jsonify({"status": 403, "method_type": method_type, "error": str(e)})
    except RequiredFieldError as e:
        return jsonify({"status": e.error_code, "method_type": method_type, "error": str(e)})
    except InvalidInputException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except KeyError as e:
        return jsonify({"status": 401, "method_type": method_type,
                        "error": "key %s is not passed" % str(e)})
    except:
        return jsonify({"status": 500, "method_type": None, "error": "General Error"})


@user_auth_blueprint.route('/<string:user_id>/contacts', methods=['GET'])
def get_contacts(user_id):
    cfg_helper = ConfigHelper()
    method_type = 'select_content'
    try:
        order_data = request_flask.json
        if 'service' not in order_data.keys():
            raise RequiredFieldError("service")
        index = order_data['service']
        api_key = order_data['api_key']
        if 'token' not in order_data.keys():
            raise RequiredFieldError("token")
        token = order_data['token']
        payload = authorize(api_key, token)
        config_key = index.upper()
        if config_key not in cfg_helper.config.keys():
            raise RequiredFieldError("service")
        order_data['data']['method'] = method_type
        dynamic_module = importlib.import_module(config_key.lower())

        class_ = config_key.split("_")
        class_name = ''
        for j in class_:
            class_name += (j[0].upper() + j[1:].lower())
        source = authenticate(api_key)
        order_data["data"]['user_id'] = user_id
        if source is None:
            raise NotAuthenticatedException()
        if payload['member_id'] != user_id:
            raise NotAuthenticatedException()

        size = 1000 if "size" not in order_data else order_data["size"]
        from_ = 0 if "from" not in order_data else order_data["from"]
        request_ = {"broker_type": cfg_helper.get_config("DEFAULT")["broker_type"], "source": source,
                    "method": method_type, "ip": request_flask.remote_addr, "api_key": api_key, "size": size,
                    "from": from_, "member_id": payload['member_id'], "data": order_data["data"]
                    }

        worker = getattr(dynamic_module, "ContentSelectWorker")
        response = clear_response(worker().serve_request(request_))
        if not response['is_successful']:
            return jsonify({"status": response['error_code'], "method_type": method_type,
                            "response": response, 'error_description': response['error_description']})
        else:
            return jsonify({"status": 200, "method_type": method_type, "response": response})
    except NotAuthenticatedException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except NotAuthorizedException as e:
        return jsonify({"status": 405, "method_type": method_type, "error": str(e)})
    except PermissionDeniedException as e:
        return jsonify({"status": 403, "method_type": method_type, "error": str(e)})
    except RequiredFieldError as e:
        return jsonify({"status": e.error_code, "method_type": method_type, "error": str(e)})
    except InvalidInputException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except KeyError as e:
        return jsonify({"status": 401, "method_type": method_type,
                        "error": "key %s is not passed" % str(e)})
    except:
        return jsonify({"status": 500, "method_type": None, "error": "General Error"})


@user_auth_blueprint.route('/<string:user_id>/contacts', methods=['POST'])
def insert_contact(user_id):
    cfg_helper = ConfigHelper()
    method_type = 'add_contact'
    try:
        order_data = request_flask.json
        if 'service' not in order_data.keys():
            raise RequiredFieldError("service")
        index = order_data['service']
        api_key = order_data['api_key']
        if 'token' not in order_data.keys():
            raise RequiredFieldError("token")
        token = order_data['token']
        payload = authorize(api_key, token)
        config_key = index.upper()
        if config_key not in cfg_helper.config.keys():
            raise RequiredFieldError("service")
        order_data['data']['method'] = method_type
        dynamic_module = importlib.import_module(config_key.lower())

        class_ = config_key.split("_")
        class_name = ''
        for j in class_:
            class_name += (j[0].upper() + j[1:].lower())
        source = authenticate(api_key)
        order_data["data"]['contact_id'] = user_id
        if source is None:
            raise NotAuthenticatedException()
        if payload['member_id'] != user_id:
            raise NotAuthenticatedException()

        size = 1000 if "size" not in order_data else order_data["size"]
        from_ = 0 if "from" not in order_data else order_data["from"]
        request_ = {"broker_type": cfg_helper.get_config("DEFAULT")["broker_type"], "source": source,
                    "method": method_type, "ip": request_flask.remote_addr, "api_key": api_key, "size": size,
                    "from": from_, "member_id": payload['member_id'], "data": order_data["data"]
                    }

        worker = getattr(dynamic_module, "ContentInsertWorker")
        response = clear_response(worker().serve_request(request_))
        if not response['is_successful']:
            return jsonify({"status": response['error_code'], "method_type": method_type,
                            "response": response, 'error_description': response['error_description']})
        else:
            return jsonify({"status": 200, "method_type": method_type, "response": response})
    except NotAuthenticatedException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except NotAuthorizedException as e:
        return jsonify({"status": 405, "method_type": method_type, "error": str(e)})
    except PermissionDeniedException as e:
        return jsonify({"status": 403, "method_type": method_type, "error": str(e)})
    except RequiredFieldError as e:
        return jsonify({"status": e.error_code, "method_type": method_type, "error": str(e)})
    except InvalidInputException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except KeyError as e:
        return jsonify({"status": 401, "method_type": method_type,
                        "error": "key %s is not passed" % str(e)})
    except:
        return jsonify({"status": 500, "method_type": None, "error": "General Error"})


@user_auth_blueprint.route('/<string:user_id>/contacts/<string:contact_id>', methods=['DELETE'])
def delete_contact(user_id, contact_id):
    cfg_helper = ConfigHelper()
    method_type = 'delete_content'
    try:
        order_data = request_flask.json
        if 'service' not in order_data.keys():
            raise RequiredFieldError("service")
        index = order_data['service']
        api_key = order_data['api_key']
        if 'token' not in order_data.keys():
            raise RequiredFieldError("token")
        token = order_data['token']
        payload = authorize(api_key, token)
        config_key = index.upper()
        if config_key not in cfg_helper.config.keys():
            raise RequiredFieldError("service")
        order_data['data']['method'] = method_type
        dynamic_module = importlib.import_module(config_key.lower())

        class_ = config_key.split("_")
        class_name = ''
        for j in class_:
            class_name += (j[0].upper() + j[1:].lower())
        source = authenticate(api_key)
        order_data["data"]['user_id'] = user_id
        order_data["data"]['contact_id'] = contact_id
        if source is None:
            raise NotAuthenticatedException()
        if payload['member_id'] != user_id:
            raise NotAuthenticatedException()
        size = 1000 if "size" not in order_data else order_data["size"]
        from_ = 0 if "from" not in order_data else order_data["from"]
        request_ = {"broker_type": cfg_helper.get_config("DEFAULT")["broker_type"], "source": source,
                    "method": method_type, "ip": request_flask.remote_addr, "api_key": api_key, "size": size,
                    "from": from_, "member_id": payload['member_id'], "data": order_data["data"]
                    }

        worker = getattr(dynamic_module, "ContentDeleteWorker")
        response = clear_response(worker().serve_request(request_))
        if not response['is_successful']:
            return jsonify({"status": response['error_code'], "method_type": method_type,
                            "response": response, 'error_description': response['error_description']})
        else:
            return jsonify({"status": 200, "method_type": method_type, "response": response})
    except NotAuthenticatedException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except NotAuthorizedException as e:
        return jsonify({"status": 405, "method_type": method_type, "error": str(e)})
    except PermissionDeniedException as e:
        return jsonify({"status": 403, "method_type": method_type, "error": str(e)})
    except RequiredFieldError as e:
        return jsonify({"status": e.error_code, "method_type": method_type, "error": str(e)})
    except InvalidInputException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except KeyError as e:
        return jsonify({"status": 401, "method_type": method_type,
                        "error": "key %s is not passed" % str(e)})
    except:
        return jsonify({"status": 500, "method_type": None, "error": "General Error"})


@user_auth_blueprint.route('/contacts/<string:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    cfg_helper = ConfigHelper()
    method_type = 'update_content_detail'
    try:
        order_data = request_flask.json
        if 'service' not in order_data.keys():
            raise RequiredFieldError("service")
        index = order_data['service']
        api_key = order_data['api_key']
        if 'token' not in order_data.keys():
            raise RequiredFieldError("token")
        token = order_data['token']
        payload = authorize(api_key, token)
        config_key = index.upper()
        if config_key not in cfg_helper.config.keys():
            raise RequiredFieldError("service")
        dynamic_module = importlib.import_module(config_key.lower())

        class_ = config_key.split("_")
        class_name = ''
        for j in class_:
            class_name += (j[0].upper() + j[1:].lower())
        source = authenticate(api_key)
        order_data["data"]['contact_id'] = contact_id
        if source is None:
            raise NotAuthenticatedException()

        size = 1000 if "size" not in order_data else order_data["size"]
        from_ = 0 if "from" not in order_data else order_data["from"]
        request_ = {"broker_type": cfg_helper.get_config("DEFAULT")["broker_type"], "source": source,
                    "method": method_type, "ip": request_flask.remote_addr, "api_key": api_key, "size": size,
                    "from": from_, "member_id": payload['member_id'], "data": order_data["data"]
                    }

        worker = getattr(dynamic_module, "ContentUpdateWorker")
        response = clear_response(worker().serve_request(request_))
        if not response['is_successful']:
            return jsonify({"status": response['error_code'], "method_type": method_type,
                            "response": response, 'error_description': response['error_description']})
        else:
            return jsonify({"status": 200, "method_type": method_type, "response": response})
    except NotAuthenticatedException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except NotAuthorizedException as e:
        return jsonify({"status": 405, "method_type": method_type, "error": str(e)})
    except PermissionDeniedException as e:
        return jsonify({"status": 403, "method_type": method_type, "error": str(e)})
    except RequiredFieldError as e:
        return jsonify({"status": e.error_code, "method_type": method_type, "error": str(e)})
    except InvalidInputException as e:
        return jsonify({"status": 401, "method_type": method_type, "error": str(e)})
    except KeyError as e:
        return jsonify({"status": 401, "method_type": method_type,
                        "error": "key %s is not passed" % str(e)})
    except:
        return jsonify({"status": 500, "method_type": None, "error": "General Error"})


#
# # Chat
# chats_blueprint = Blueprint('chats', __name__, url_prefix='/api/chats')
#
#
# @chats_blueprint.route('', methods=['POST'])
# def insert_chat():
#     return None
#
#
# @chats_blueprint.route('', methods=['GET'])
# def list_chat():
#     return None
#
#
# @chats_blueprint.route('/<int:chat_id>', methods=['GET'])
# def get_chat(chat_id):
#     return None
#
#
# @chats_blueprint.route('/<int:chat_id>', methods=['DELETE'])
# def delete_chat(chat_id):
#     return None
#
#
# @chats_blueprint.route('/<int:chat_id>/messages/<int:messages_id>', methods=['DELETE'])
# def delete_send_message(chat_id, messages_id):
#     return None
#
#
# # Groups
# groups_blueprint = Blueprint('groups', __name__, url_prefix='/api/groups')
#
#
# @groups_blueprint.route('', methods=['POST'])
# def insert_group():
#     return None
#
#
# @groups_blueprint.route('/<int:group_id>', methods=['DELETE'])
# def delete_group(group_id):
#     return None
#
#
# @groups_blueprint.route('/<int:group_id>', methods=['PATCH'])
# def insert_group(group_id):
#     return None
#
#
# @groups_blueprint.route('/<int:group_id>/<int:user_id>', methods=['DELETE'])
# def delete_send_message(group_id, user_id):
#     return None


class InvalidInputException(Exception):
    def __init__(self, param, value):
        super(InvalidInputException, self).__init__("INVALID INPUT %s: %s" % (param, value))


class PermissionDeniedException(Exception):
    def __init__(self):
        super(PermissionDeniedException, self).__init__("PERMISSION DENIED")


class NotAuthenticatedException(InvalidInputException):
    def __init__(self):
        super(NotAuthenticatedException, self).__init__("API_KEY", "Not Authenticated")


class NotAuthorizedException(InvalidInputException):
    def __init__(self):
        super(NotAuthorizedException, self).__init__("token", "Not Authorized")


class ExpireTokenException(InvalidInputException):
    def __init__(self):
        super(ExpireTokenException, self).__init__("token", "token expire")


def authenticate(api_key):
    cfg_helper = ConfigHelper()
    if not cfg_helper.has_name("DB_API", api_key + "_service"):
        return None
    service_name = cfg_helper.get_config("DB_API")[api_key + "_service"]
    return service_name


def authorize(api_key, token):
    cfg_helper = ConfigHelper()
    secret_key = cfg_helper.get_config("DEFAULT")["secret_key"]
    if api_key == token:  # CLIENT IS AN INTERNAL SERVICE
        return {'exp': 100000000000, 'member_id': '090000000'}
    if token is None:
        raise RequiredFieldError("token")

    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise ExpireTokenException()
    except jwt.InvalidTokenError:
        raise PermissionDeniedException()


def create_jwt_token(payload):
    cfg_helper = ConfigHelper()
    secret_key = cfg_helper.get_config("DEFAULT")["secret_key"]
    expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    token = jwt.encode({'exp': expiry, **payload}, secret_key, algorithm='HS256')

    return token


if __name__ == '__main__':
    # app.register_blueprint(chats_blueprint)
    app.register_blueprint(user_auth_blueprint)
    app.register_blueprint(user_blueprint)
    app.run(debug=True, host='0.0.0.0', port=9200)
