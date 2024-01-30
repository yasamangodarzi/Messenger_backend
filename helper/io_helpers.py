from helper.communication_helpers import create_message, create_persian_error_message


def create_error_response(status, method_type, error, broker_type, source, member_id):
    return create_message(method=method_type, record={}, broker_type=broker_type, source=source, error_code=status,
                          is_successful=False, error_description=error, member_id=member_id)


def create_success_response(method_type, response, broker_type, source, member_id):
    return create_message(method=method_type, record=response, broker_type=broker_type, source=source, error_code=0,
                          is_successful=True, error_description="", member_id=member_id)


def create_exception_response(status, method_type, error, broker_type, source, member_id, error_persian):
    return create_persian_error_message(method=method_type, record={}, broker_type=broker_type, source=source,
                                        error_code=status,
                                        is_successful=False, error_description=error, member_id=member_id,
                                        error_persian_description=error_persian)


def check_schema(data, schema):
    invalid_field_name = None
    for field in data.keys():
        if field == "_id":
            continue
        if field not in schema.keys():
            invalid_field_name = field

    if invalid_field_name is not None:
        raise InvalidFieldName(invalid_field_name)


def preprocess_schema(data, schema):
    for field in list(data.keys()):
        if field == "_id":
            continue
        if field not in schema.keys():
            invalid_field_name = field
            del data[invalid_field_name]

    return data


def check_full_schema(data, schema):
    schema_keys = set(schema.keys())

    data_keys = set(data.keys())
    if "_id" in data_keys:
        data_keys.remove("_id")

    extra_keys = data_keys - schema_keys
    if len(extra_keys) > 0:
        for k in list(extra_keys):
            del data[k]

    if len(schema_keys - data_keys) > 0:
        for null_key in list(schema_keys - data_keys):
            data[null_key] = None

    return data


def preprocess(data, schema):
    for field in data:
        if data[field] is None and field in schema.keys() and "_null_value" in schema[field].keys():
            data[field] = schema[field]["_null_value"]
        if field in schema.keys() and "_type" in schema[field].keys():
            data[field] = schema[field]["_type"](data[field])
    return data


def field_is_empty(field, _field_name, schema):
    if field is None or field == "" or field == schema[_field_name]["_null_value"]:
        return True
    else:
        return False


class UserInputError(Exception):
    def __init__(self, message, error_code, persian_massage=''):
        super(UserInputError, self).__init__(message)
        self.error_code = error_code
        self.persian_massage = persian_massage


class MemberNotFoundError(UserInputError):
    def __init__(self):
        super(MemberNotFoundError, self).__init__("INVALID member_id", 605, "کد کاربر اشتباه است")


class RequiredFieldError(UserInputError):
    def __init__(self, field_name):
        super(RequiredFieldError, self).__init__("Field %s is required." % field_name, 602,
                                                 "متغیر %s اجباری است ." % field_name)


class InvalidFieldName(UserInputError):
    def __init__(self, field_name):
        super(InvalidFieldName, self).__init__("Field %s is invalid." % field_name, 604,
                                               "فیلد %s نامعتبر است." % field_name)


class InvalidInputField(UserInputError):
    def __init__(self, field_name):
        super(InvalidInputField, self).__init__("Invalid value for field with name '%s'" % field_name, 603,
                                                "مقدار نامعتبر برای فیلد با نام '%s'")
