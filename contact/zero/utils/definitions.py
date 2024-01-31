contact_schema = {
    "broker_type": {"_type": str, "_null_value": "null", "_check_in_insert": False},
    "user_id": {"_type": str, "_null_value": "null", "_check_in_insert": True},
    "contact_id": {"_type": str, "_null_value": "null", "_check_in_insert": True},
    "contact_name": {"_type": str, "_null_value": "null", "_check_in_insert": False},
    "access_phone": {"_type": str, "_null_value": "TRUE", "_check_in_insert": False},
    "access_photo": {"_type": str, "_null_value": "TRUE", "_check_in_insert": False},
    "pin": {"_type": str, "_null_value": "null", "_check_in_insert": False},
    "category": {"_type": str, "_null_value": "null", "_check_in_insert": False},
    "access_status": {"_type": str, "_null_value": "FALSE", "_check_in_insert": False},
    "status": {"_type": str, "_null_value": "last_seen_ago", "_check_in_insert": False},
    "last_update_date": {"_type": str, "format": "8yyyy/MM/dd HH:mm:ss.SSSSSS",
                         "_null_value": "1970/01/01 00:00:00.000000",
                         "_check_in_insert": False},
    "DC_CREATE_TIME": {"_type": str, "format": "8yyyy/MM/dd HH:mm:ss.SSSSSS",
                       "_null_value": "1970/01/01 00:00:00.000000",
                       "_check_in_insert": False},

}
