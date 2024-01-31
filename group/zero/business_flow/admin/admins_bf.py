from helper.business_flow_helpers import BusinessFlow
from members.zero.utils.utils import *
import group as service


# noinspection PyMethodMayBeStatic

class AdminBusinessFlowManager(BusinessFlow):
    def __init__(self, ):
        super(AdminBusinessFlowManager, self).__init__(service.service_name)

        self.cfg_helper = ConfigHelper()

    # noinspection PyUnusedLocal
    def select_business_flow(self, data, request, member, params=None):
        raise PermissionError()

    def insert_business_flow(self, data, request, member, params=None):
        raise PermissionError()

    def delete_business_flow(self, data, request, member, params=None):
        raise PermissionError()

    def update_business_flow(self, data, request, member, params=None):
        raise PermissionError()
