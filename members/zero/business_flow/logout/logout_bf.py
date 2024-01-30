from helper.io_helpers import *
from helper.config_helper import ConfigHelper
from helper.business_flow_helpers import BusinessFlow

import members as service


# noinspection PyMethodMayBeStatic
class LogoutBusinessFlowManager(BusinessFlow):
    def __init__(self, ):
        super(LogoutBusinessFlowManager, self).__init__(service.service_name)

        self.cfg_helper = ConfigHelper()

    def logout_business_flow(self, member, data, request):
        self.mongo.get_mongo_connection()

        if 'method' not in request.keys():
            raise RequiredFieldError("method")

        method = request["method"]
        if method == "logout":
            pass
        else:
            raise PermissionError()

        return 0
