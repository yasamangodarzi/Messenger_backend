import traceback
import pymongo
from helper.config_helper import ConfigHelper
from helper.io_helpers import *
from helper.multiplexer import Multiplexer

import chat as service
from members import get_member


class ChatWorker:
    def __init__(self, ):
        super(ChatWorker, self).__init__()
        self.cfg_helper = ConfigHelper()
        self.mongo = pymongo.MongoClient("mongodb://localhost:27017/").myclient[service.service_name]
        self.user_bf = service.UserBusinessFlowManager()
        self.admin_bf = service.AdminBusinessFlowManager()
        self.free_bf = service.FreeBusinessFlowManager()

        self.multiplexer = Multiplexer()


# noinspection PyShadowingBuiltins,PyBroadException,DuplicatedCode
class ChatSelectWorker(ChatWorker):
    def __init__(self, ):
        super(ChatSelectWorker, self).__init__()

    def serve_request(self, request_body):
        request = request_body
        broker_type = request["broker_type"]
        data = request["data"]
        try:
            if data is None:
                data = {}

            data["broker_type"] = broker_type

            results = self.business_flow(data, request)

            response = create_success_response(method_type=request["method"],
                                               response=results,
                                               broker_type=request["broker_type"],
                                               source=request["source"],
                                               member_id=request["member_id"])
        except PermissionError:
            response = create_error_response(status=701,
                                             method_type=request["method"], error="PERMISSION DENIED",
                                             broker_type=request["broker_type"],
                                             source=request["source"],
                                             member_id=request["member_id"])
        except UserInputError as e:
            response = create_exception_response(status=e.error_code,
                                                 method_type=request["method"], error=str(e),
                                                 broker_type=request["broker_type"],
                                                 source=request["source"],
                                                 member_id=request["member_id"],
                                                 error_persian=e.persian_massage)
        except Exception:
            # tb.print_exc()
            error = f"Exception\n{traceback.format_exc()}"
            response = create_error_response(status=401,
                                             method_type=request["method"], error=error,
                                             broker_type=request["broker_type"],
                                             source=request["source"],
                                             member_id=request["member_id"])

        return response

    def business_flow(self, data, request):
        request_sender_id = request["member_id"]
        request_sender_member = get_member(request_sender_id=request_sender_id)

        source = request["source"]

        if self.multiplexer.is_admin(source=source, member_category=request_sender_member["category"]):
            return self.admin_bf.select_business_flow(data=data, request=request, member=request_sender_member)
        elif self.multiplexer.is_member(source=source, member_category=request_sender_member["category"]):
            return self.user_bf.select_business_flow(data=data, request=request, member=request_sender_member)
        elif self.multiplexer.is_free(source=source, member_category=request_sender_member["category"]):
            return self.free_bf.select_business_flow(data=data, request=request, member=request_sender_member)

        else:
            raise PermissionError()


# noinspection PyShadowingBuiltins,PyBroadException,DuplicatedCode
class ChatInsertWorker(ChatWorker):
    def __init__(self, ):
        super(ChatInsertWorker, self).__init__()

    def serve_request(self, request_body):
        request = request_body
        broker_type = request["broker_type"]
        data = request["data"]

        try:
            if data is None:
                raise RequiredFieldError("data")

            data["broker_type"] = broker_type

            result = self.business_flow(data, request)

            response = create_success_response(
                method_type=request["method"],
                response=result,
                broker_type=request["broker_type"],
                source=request["source"],
                member_id=request["member_id"])

        except PermissionError:
            response = create_error_response(status=701,
                                             method_type=request["method"], error="PERMISSION DENIED",
                                             broker_type=request["broker_type"],
                                             source=request["source"],
                                             member_id=request["member_id"])

        except UserInputError as e:

            response = create_exception_response(status=e.error_code,

                                                 method_type=request["method"], error=str(e),

                                                 broker_type=request["broker_type"],

                                                 source=request["source"],

                                                 member_id=request["member_id"],

                                                 error_persian=e.persian_massage)

        except Exception:
            error = f"Exception\n{traceback.format_exc()}"
            response = create_error_response(status=401,
                                             method_type=request["method"], error=error,
                                             broker_type=request["broker_type"],
                                             source=request["source"],
                                             member_id=request["member_id"])

        return response

    def business_flow(self, data, request):
        request_sender_id = request["member_id"]
        request_sender_member = get_member(request_sender_id=request_sender_id)
        source = request["source"]

        if self.multiplexer.is_admin(source=source, member_category=request_sender_member["category"]):
            return self.admin_bf.insert_business_flow(data=data, request=request, member=request_sender_member)
        elif self.multiplexer.is_member(source=source, member_category=request_sender_member["category"]):
            return self.user_bf.insert_business_flow(data=data, request=request, member=request_sender_member)
        elif self.multiplexer.is_free(source=source, member_category=request_sender_member["category"]):
            return self.free_bf.insert_business_flow(data=data, request=request, member=request_sender_member)

        else:
            raise PermissionError()


# noinspection PyBroadException,PyShadowingBuiltins,DuplicatedCode
class ChatDeleteWorker(ChatWorker):
    def __init__(self, ):
        super(ChatDeleteWorker, self).__init__()

    def serve_request(self, request_body):
        request = request_body
        data = request["data"]
        broker_type = request["broker_type"]

        try:
            if data is None:
                raise RequiredFieldError(data)


            data["broker_type"] = broker_type

            result = self.business_flow(data=data, request=request)

            response = create_success_response(
                method_type=request["method"],
                response=result,
                broker_type=request["broker_type"],
                source=request["source"],
                member_id=request["member_id"])

        except PermissionError:
            response = create_error_response(status=701,
                                             method_type=request["method"], error="PERMISSION DENIED",
                                             broker_type=request["broker_type"],
                                             source=request["source"],
                                             member_id=request["member_id"])

        except UserInputError as e:
            response = create_error_response(status=e.error_code,
                                             method_type=request["method"], error=str(e),
                                             broker_type=request["broker_type"],
                                             source=request["source"],
                                             member_id=request["member_id"])


        except Exception:
            # tb.print_exc()
            error = f"Exception\n{traceback.format_exc()}"
            response = create_error_response(status=401,
                                             method_type=request["method"], error=error,
                                             broker_type=request["broker_type"],
                                             source=request["source"],
                                             member_id=request["member_id"])

        return response

    def business_flow(self, data, request):
        request_sender_id = request["member_id"]
        request_sender_member = get_member(request_sender_id=request_sender_id)

        source = request["source"]

        if self.multiplexer.is_admin(source=source, member_category=request_sender_member["category"]):
            return self.admin_bf.delete_business_flow(data=data, request=request, member=request_sender_member)
        elif self.multiplexer.is_member(source=source, member_category=request_sender_member["category"]):
            return self.user_bf.delete_business_flow(data=data, request=request, member=request_sender_member)
        elif self.multiplexer.is_free(source=source, member_category=request_sender_member["category"]):
            return self.free_bf.delete_business_flow(data=data, request=request, member=request_sender_member)

        else:
            raise PermissionError()


# noinspection PyBroadException,PyShadowingBuiltins,DuplicatedCode
class ChatUpdateWorker(ChatWorker):
    def __init__(self, ):
        super(ChatUpdateWorker, self).__init__()

    def serve_request(self, request_body):
        request = request_body
        broker_type = request["broker_type"]
        data = request["data"]

        try:
            if data is None:
                raise RequiredFieldError("data")

            data["broker_type"] = broker_type

            result = self.business_flow(data, request)

            response = create_success_response(
                method_type=request["method"],
                response=result,
                broker_type=request["broker_type"],
                source=request["source"],
                member_id=request["member_id"])

        except PermissionError:
            response = create_error_response(status=701,
                                             method_type=request["method"], error="PERMISSION DENIED",
                                             broker_type=request["broker_type"],
                                             source=request["source"],
                                             member_id=request["member_id"])

        except UserInputError as e:
            response = create_error_response(status=e.error_code,
                                             method_type=request["method"], error=str(e),
                                             broker_type=request["broker_type"],
                                             source=request["source"],
                                             member_id=request["member_id"])

        except Exception:
            # tb.print_exc()
            error = f"Exception\n{traceback.format_exc()}"
            response = create_error_response(status=401,
                                             method_type=request["method"], error=error,
                                             broker_type=request["broker_type"],
                                             source=request["source"],
                                             member_id=request["member_id"])

        return response

    def business_flow(self, data, request):
        request_sender_id = request["member_id"]
        request_sender_member = get_member(request_sender_id=request_sender_id)

        source = request["source"]

        if self.multiplexer.is_admin(source=source, member_category=request_sender_member["category"]):
            return self.admin_bf.update_business_flow(data=data, request=request, member=request_sender_member)
        elif self.multiplexer.is_member(source=source, member_category=request_sender_member["category"]):
            return self.user_bf.update_business_flow(data=data, request=request, member=request_sender_member)
        elif self.multiplexer.is_free(source=source, member_category=request_sender_member["category"]):
            return self.free_bf.update_business_flow(data=data, request=request, member=request_sender_member)

        else:
            raise PermissionError()
