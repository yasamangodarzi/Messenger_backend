chat_schema = {
    "broker_type": {"_type": str, "_null_value": "null", "_check_in_insert": False},
    "member_ids": {"_type": list, "_null_value": [], "_check_in_insert": False},
    "chat_id": {"_type": str, "_null_value": "", "_check_in_insert": True},
    "last_update_date": {"_type": str, "format": "8yyyy/MM/dd HH:mm:ss.SSSSSS",
                         "_null_value": "1970/01/01 00:00:00.000000",
                         "_check_in_insert": False},
    "DC_CREATE_TIME": {"_type": str, "format": "8yyyy/MM/dd HH:mm:ss.SSSSSS",
                       "_null_value": "1970/01/01 00:00:00.000000",
                       "_check_in_insert": False},

}
message_schema = {
    "message_id": {"_type": str, "_null_value": "null", "_check_in_insert": False},
    "chat_id": {"_type": str, "_null_value": "null", "_check_in_insert": False},
    "sender": {"_type": str, "_null_value": "null", "_check_in_insert": False},
    "receiver": {"_type": list, "_null_value": [], "_check_in_insert": False},
    "content": {"_type": str, "_null_value": 'null', "_check_in_insert": False},
    "type": {"_type": str, "_null_value": "", "_check_in_insert": False},
    "last_update_date": {"_type": str, "format": "8yyyy/MM/dd HH:mm:ss.SSSSSS",
                         "_null_value": "1970/01/01 00:00:00.000000",
                         "_check_in_insert": False},
    "DC_CREATE_TIME": {"_type": str, "format": "8yyyy/MM/dd HH:mm:ss.SSSSSS",
                       "_null_value": "1970/01/01 00:00:00.000000",
                       "_check_in_insert": False},

}
