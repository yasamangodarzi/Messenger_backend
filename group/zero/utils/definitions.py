group_schema = {
    "broker_type": {"_type": str, "_null_value": "null", "_check_in_insert": False},
    "admin_ids": {"_type": str, "_null_value": "null", "_check_in_insert": False},
    "group_user_name": {"_type": str, "_null_value": "null", "_check_in_insert": True},
    "user_ids": {"_type": str, "_null_value": "null", "_check_in_insert": False},
    "group_photo": {"_type": str, "_null_value": "null", "_check_in_insert": False},
    "group_name": {"_type": str, "_null_value": "TRUE", "_check_in_insert": False},
    "last_update_date": {"_type": str, "format": "8yyyy/MM/dd HH:mm:ss.SSSSSS",
                         "_null_value": "1970/01/01 00:00:00.000000",
                         "_check_in_insert": False},
    "DC_CREATE_TIME": {"_type": str, "format": "8yyyy/MM/dd HH:mm:ss.SSSSSS",
                       "_null_value": "1970/01/01 00:00:00.000000",
                       "_check_in_insert": False},

}
