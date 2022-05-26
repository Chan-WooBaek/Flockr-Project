import sys
sys.path.append('../')
from pytest import raises
from message import message_send, message_remove, message_edit
from channels import channels_create
from auth import auth_register
from error import InputError
from other import clear

def test_message_send_empty_string():
    '''
    Test assumption which is if an InputError is raised when send a message which
    is empty string
    '''
    # clear data
    clear()

    #initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)
    # check if it will raise InputError
    with raises(InputError):
        message_send(user['token'], channel['channel_id'], "")

def test_message_edit_messageid_not_exists():
    '''
    Test assumption which is if an InputError is raised when the message no longer exists
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')

    # check if it will raise InputError
    with raises(InputError):
        message_edit(user['token'], 1, "Hello")

def test_message_edit_message_was_removed():
    '''
     Test assumption which is if an InputError is raise dwhen the message no longer exists
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)
    message = message_send(user['token'], channel['channel_id'], "I love COMP1531!")
    message_remove(user['token'], message['message_id'])
        
    # check if it will raise InputError
    with raises(InputError):
        message_edit(user['token'], message['message_id'], "Hello")
    
def test_message_edit_message_to_long():
    '''
     Test assumption which is if an InputError is raise dwhen the message is too long
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)
    message = message_send(user['token'], channel['channel_id'], "I love COMP1531!")
        
    # check if it will raise InputError
    with raises(InputError):
        message_edit(user['token'], message['message_id'], "I love COMP1531!!!"*2333)    