from helper.config_helper import ConfigHelper

cfg_helper = ConfigHelper()
service_name = "CONTACT"

from contact.zero.workers import *
from contact.zero.business_flow.admin.admins_bf import *
from contact.zero.business_flow.user.users_bf import *
from contact.zero.business_flow.internal.internal import *
from contact.zero.utils.utils import *
from contact.zero.utils.definitions import *
