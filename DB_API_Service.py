from flask import Flask, Blueprint

app = Flask(__name__)

user_blueprint = Blueprint('api', __name__, url_prefix='/api')


@user_blueprint.route('/register', methods=['POST'])
def user_register():
    return None


@user_blueprint.route('/login', methods=['POST'])
def user_login():
    return None


# User
user_auth_blueprint = Blueprint('user', __name__, url_prefix='/api/user')


@user_auth_blueprint.route('/<int:user_id>', methods=['GET'])
def user_info(user_id):
    return None


@user_auth_blueprint.route('/<int:user_id>', methods=['PATCH'])
def change_user_info(user_id):
    return None


@user_auth_blueprint.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    return None


@user_auth_blueprint.route('?keyword=<str:key>', methods=['GET'])
def search(key):
    return None


@user_auth_blueprint.route('/<int:user_id>/contacts', methods=['GET'])
def get_contacts(user_id):
    return None


@user_auth_blueprint.route('/<int:user_id>/contacts', methods=['POST'])
def insert_contact(user_id):
    return None


@user_auth_blueprint.route('/<int:user_id>/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(user_id, contact_id):
    return None


# Chat
chats_blueprint = Blueprint('chats', __name__, url_prefix='/api/chats')


@chats_blueprint.route('', methods=['POST'])
def insert_chat():
    return None


@chats_blueprint.route('', methods=['GET'])
def list_chat():
    return None


@chats_blueprint.route('/<int:chat_id>', methods=['GET'])
def get_chat(chat_id):
    return None


@chats_blueprint.route('/<int:chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    return None


@chats_blueprint.route('/<int:chat_id>/messages/<int:messages_id>', methods=['DELETE'])
def delete_send_message(chat_id, messages_id):
    return None


# Groups
groups_blueprint = Blueprint('groups', __name__, url_prefix='/api/groups')


@groups_blueprint.route('', methods=['POST'])
def insert_group():
    return None


@groups_blueprint.route('/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    return None


@groups_blueprint.route('/<int:group_id>', methods=['PATCH'])
def insert_group(group_id):
    return None


@groups_blueprint.route('/<int:group_id>/<int:user_id>', methods=['DELETE'])
def delete_send_message(group_id, user_id):
    return None


if __name__ == '__main__':
    app.run(debug=True)
