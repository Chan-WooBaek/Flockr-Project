'''
The helper_test.py only calls the static methods from different classes
so that the helper_test.py is left unchanged
'''

from data import User, Channel, Message
from error import AccessError

def authorise(function):
    '''
    Use decorator to remove repetition with the checks for token
    '''
    def wrapper(*args, **kwargs):
        token = args[0]
        if get_uid_from_token(token) is None:
            raise AccessError(description="Invalid token!")
        return function(*args)
    return wrapper

def check_name_first(name):
    '''
    check if the name is between 1 and 50 characters.
    '''
    User.check_name_first(name)

def check_name_last(name):
    '''
    check if the name is between 1 and 50 characters.
    '''
    User.check_name_last(name)

def check_email_format(email):
    '''
    An InputError will be raised if the passed in email has an invalid format.
    '''
    User.check_email_format(email)

def check_email_repeated(email):
    '''
    An input error will be raised if the passed in email is already existing
    '''
    User.check_email_repeated(email)

def check_password(password):
    '''
    An InputError will be raised if the passed password is invalid
    '''
    User.check_password(password)

def check_handle(handle_str):
    '''
    An InputError will be raised if the password handle is invalid
    '''
    User.check_handle(handle_str)

def find_channel(channel_id):
    '''
    Return the index of the channel whose channel_id matches the passed in
    channel_id. None will be returned if it is not found.
    '''
    return Channel.find_channel(channel_id)

def find_user(u_id):
    '''
    Return the index of the user whose u_id matches the passed in
    u_id. None will be returned if it is not found.
    '''

    return User.find_user(u_id)

def is_user_in_channel(u_id, channel_id):
    '''
    Check if the user with the passed in u_id is a member of the channel
    with the passed in channel_id.
    '''
    return Channel.is_user_in_channel(u_id, channel_id)

def is_user_owner(u_id, channel_id):
    '''
    Check if the user with the passed in u_id is an owner of the channel
    with the passed in channel_id.
    '''
    return Channel.is_user_owner(u_id, channel_id)

def find_message(message_id):
    '''
    Return the index of the message whose message_id matches the passed in
    u_id. None will be returned if it is not found.
    '''
    return Message.find_message(message_id)

def encrypt_password(password):
    '''
    Return the hashsed password string.
    '''
    return User.encrypt_password(password)


def generate_token(u_id):
    '''
    Return the token generated based on the passed in u_id.
    If the token does not exist, add it to the valid_tokens list
    The payload:
    {
        "u_id": integer,
    }
    '''
    return User.generate_token(u_id)

def get_uid_from_token(token):
    '''
    Return the u_id decoded from the passed in token.
    If the token is not in the valid_tokens list, return None.
    If the u_id does not exist, return None.
    '''
    return User.get_uid_from_token(token)

def invalidate_token(token):
    '''
    Assumes the token passed in is valid
    Remove the token from the valid_tokens list
    '''
    User.invalidate_token(token)

def is_message_reacted_by_user(u_id, message_id, react_id):
    '''
    Check if the message is already reacted by the authorised user
    '''
    return Message.is_message_reacted_by_user(u_id, message_id, react_id)
