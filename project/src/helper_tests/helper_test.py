'''
Testing helper.py
created on 11/10/2020 by Chan Baek and Xinran Zhu
'''
import sys
sys.path.append('../')
import string
import random
from pytest import raises


from error import InputError
from auth import auth_register, auth_login
from helper import check_name_first, check_name_last, check_email_format, \
check_email_repeated, check_password, check_handle, find_channel, find_user, \
is_user_in_channel, is_user_owner, find_message, encrypt_password, \
generate_token, get_uid_from_token, invalidate_token, is_message_reacted_by_user
from channel import channel_invite
from channels import channels_create
from message import message_send
from other import clear
from data import data


def test_check_name_first_long():
    '''
    check_name_first() should raise InputError when a firstname with length
    greater than 50 is passed in.
    '''
    clear()
    # create a 51-character string
    length = 51
    letters_and_digits = string.ascii_letters + string.digits
    long_name = ''.join((random.choice(letters_and_digits) for i in range(length)))
    with raises(InputError, match='Invalid first name: more than 50 characters'):
        check_name_first(long_name)

def test_check_name_first_short():
    '''
    check_name_first() should raise InputError when an empty first name
    is passed in.
    '''
    clear()
    with raises(InputError, match='Invalid first name: less than 1 character'):
        check_name_first("")

def test_check_name_last_long():
    '''
    check_name_last() should raise InputError when a lastname with length
    greater than 50 is passed in.
    '''
    clear()
    # create a 51-character string
    length = 51
    letters_and_digits = string.ascii_letters + string.digits
    long_name = ''.join((random.choice(letters_and_digits) for i in range(length)))
    with raises(InputError, match='Invalid last name: more than 50 characters'):
        check_name_last(long_name)

def test_check_name_last_short():
    '''
    check_name_last() should raise InputError when an empty last name
    is passed in.
    '''
    clear()
    with raises(InputError, match='Invalid last name: less than 1 character'):
        check_name_last("")

def test_check_email_format():
    '''
    An InputError is expected to be raised when the input email has an invalid format.
    '''
    clear()
    with raises(InputError, match='Invalid Email Format'):
        check_email_format("invalidemail")

    check_email_format("good@gmail.com")

def test_check_email_repeated():
    '''
    An InputError is expected to be raised when the input email has an invalid email.
    '''
    clear()
    auth_register('h.smith@gmail.com', '12345678', 'Hadise', 'Smith')
    with raises(InputError):
        check_email_repeated('h.smith@gmail.com')

def test_check_handle_invalid():
    '''
    An Input error is expected to be raised when the input handle is invalid
    '''
    clear()
    with raises(InputError):
        check_handle('s')

def test_check_handle_taken():
    '''
    An Input error is expected to be raised when the input handle is taken
    '''
    clear()
    auth_register('h.smith@gmail.com', '12345678', 'Hadise', 'Smith')
    with raises(InputError):
        check_handle('hadisesmith')

def test_password_invalid():
    '''
    An Input error is expected to be raised when the input password is invalid
    '''
    with raises(InputError):
        check_password('123')

def test_find_channel():
    '''
    Testing if find_channel() returns the correct index of where the passed in
    channel is located in data['channels'].
    '''
    clear()
    user1 = auth_register('h.smith@gmail.com', '12345678', 'Hadise', 'Smith')
    user2 = auth_register('t.zhang@gmail.com', '87654321', 'Tom', 'Zhang')
    channels_create(user1['token'], 'LOL', True)
    channels_create(user1['token'], 'WOW', False)
    channel3 = channels_create(user2['token'], 'SC', True)

    assert find_channel(channel3['channel_id']) == 2

def test_find_channel_invalid_channel_id():
    '''
    None should be returned when an invalid channel_id is passed in.
    '''
    clear()
    user1 = auth_register('h.smith@gmail.com', '12345678', 'Hadise', 'Smith')
    user2 = auth_register('t.zhang@gmail.com', '87654321', 'Tom', 'Zhang')
    channels_create(user1['token'], 'LOL', True)
    channels_create(user1['token'], 'WOW', False)
    channel3 = channels_create(user2['token'], 'SC', True)

    assert find_channel(channel3['channel_id'] + 3) is None

def test_find_user():
    '''
    Testing if find_user() returns the correct index of where the passed in
    u_id is located in data['channels'].
    '''
    clear()
    auth_register('h.smith@gmail.com', '12345678', 'Hadise', 'Smith')
    auth_register('t.zhang@gmail.com', '87654321', 'Tom', 'Zhang')
    user3 = auth_register('l.zhao@hotmail.com', '12348765', 'Lee', 'Zhao')

    assert find_user(user3['u_id']) == 2

def test_find_user_invalid_u_id():
    '''
    None should be returned when an invalid u_id is passed in.
    '''
    clear()
    auth_register('h.smith@gmail.com', '12345678', 'Hadise', 'Smith')
    auth_register('t.zhang@gmail.com', '87654321', 'Tom', 'Zhang')
    user3 = auth_register('l.zhao@hotmail.com', '12348765', 'Lee', 'Zhao')

    assert find_user(user3['u_id'] + 3) is None

def test_is_user_in_channel():
    '''
    Testing if is_user_in_channel() returns the correct boolean value
    to indicate whether a user is in a channel
    '''
    clear()
    user1 = auth_register('h.smith@gmail.com', '12345678', 'Hadise', 'Smith')
    user2 = auth_register('t.zhang@gmail.com', '87654321', 'Tom', 'Zhang')
    channel1 = channels_create(user1['token'], 'LOL', True)
    channel2 = channels_create(user1['token'], 'WOW', False)
    channel3 = channels_create(user2['token'], 'SC', True)

    assert is_user_in_channel(user1['u_id'], channel1['channel_id'])
    assert not is_user_in_channel(user2['u_id'], channel2['channel_id'])
    assert is_user_in_channel(user2['u_id'], channel3['channel_id'])

def test_is_user_owner():
    '''
    Testing if is_user_owner() returns the correct boolean value
    to indicate whether a user is an owner of a channel
    '''
    clear()
    user1 = auth_register('h.smith@gmail.com', '12345678', 'Hadise', 'Smith')
    user2 = auth_register('t.zhang@gmail.com', '87654321', 'Tom', 'Zhang')
    channel = channels_create(user1['token'], 'LOL', True)
    channel_invite(user1['token'], channel['channel_id'], user1['u_id'])

    assert is_user_owner(user1['u_id'], channel['channel_id'])
    assert not is_user_owner(user2['u_id'], channel['channel_id'])

def test_find_message():
    '''
    Testing if find_message() returns the correct index of where the passed in
    message_id is located in data['message'].
    '''
    clear()
    user = auth_register('h.smith@gmail.com', '12345678', 'Hadise', 'Smith')
    channel = channels_create(user['token'], 'LOL', True)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    assert find_user(message['message_id']) == 0

def test_find_message_invalid_message_id():
    '''
    None should be returned when an invalid message_id is passed in.
    '''
    clear()
    user = auth_register('h.smith@gmail.com', '12345678', 'Hadise', 'Smith')
    channel = channels_create(user['token'], 'LOL', True)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    assert find_message(message['message_id'] + 100) == None

def test_encrypt_password():
    '''
    Test if the ecrypting system is working.
    '''
    clear()
    password_list = []
    password_list.append(encrypt_password("password1"))
    password_list.append(encrypt_password("ILoveCOMP1531"))
    password_list.append(encrypt_password("target_str"))
    password_list.append(encrypt_password("pythonIsNice"))
    password_list.append(encrypt_password("ILoveCats"))
    password_list.append(encrypt_password("SpicyThingy"))

    assert encrypt_password("target_str") in password_list
    assert encrypt_password("invalid") not in password_list

def test_capture_invalid_token():
    '''
    Test if get_uid_from_token() captures the invalid token
    '''
    clear()
    user = auth_register('h.smith@gmail.com', '12345678', 'Hadise', 'Smith')
    invalid_uid = user['u_id'] + 10
    invalid_token = generate_token(invalid_uid)
    assert get_uid_from_token(invalid_token) is None
    
def test_valid_token():
    '''
    Test if generate_token() in auth_register 
    and get_uid_from_token() work correctly as a whole
    '''
    clear()
    user1 = auth_register('h.smith@gmail.com', '12345678', 'Hadise', 'Smith')
    assert get_uid_from_token(user1['token']) == user1['u_id']

    user2 = auth_register('t.zhang@gmail.com', '87654321', 'Tom', 'Zhang')
    assert get_uid_from_token(user2['token']) == user2['u_id']

def test_repeated_token():
    '''
    Make sure nothing is added to the valid_tokens list if the new token
    generated is already in the list
    '''
    clear()
    auth_register('h.smith@gmail.com', '12345678', 'Hadise', 'Smith')
    auth_login('h.smith@gmail.com', '12345678')
    assert len(data['valid_tokens']) == 1


def test_invalidate_token():
    '''
    Test if invalidate_token() and get_uid_from_token() is working correctly
    together
    '''
    clear()
    user1 = auth_register('h.smith@gmail.com', '12345678', 'Hadise', 'Smith')
    invalidate_token(user1['token'])
    print(data['valid_tokens'])
    assert get_uid_from_token(user1['token']) is None

def test_is_message_reacted_by_user():
    '''
    Test if is_message_reacted_by_user() is working correctly
    ''' 
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    react_id = 1
    assert is_message_reacted_by_user(user['token'], message['message_id'], react_id) == False
    