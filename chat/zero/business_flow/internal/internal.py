import chat as service
from helper.business_flow_helpers import BusinessFlow
from chat.zero.utils.utils import *


class FreeBusinessFlowManager(BusinessFlow):
    def __init__(self, ):
        super(FreeBusinessFlowManager, self).__init__(service.service_name)

        self.cfg_helper = ConfigHelper()

        self.index = self.mongo.create_index(self.cfg_helper.get_config(service.service_name)["index_name"])

    def select_business_flow(self, data, request, member, params=None):
        raise PermissionError()

    def insert_business_flow(self, data, request, member, params=None):
        raise PermissionError()

    def delete_business_flow(self, data, request, member, params=None):
        raise PermissionError()

    def update_business_flow(self, data, request, member, params=None):
        raise PermissionError()
