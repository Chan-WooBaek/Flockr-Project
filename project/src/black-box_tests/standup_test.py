import sys
sys.path.append('../')
from standup import standup_start, standup_active, standup_send
from auth import auth_register, auth_logout
from other import clear, search
from channels import channels_create
from channel import channel_invite
import time
from pytest import raises
from error import InputError, AccessError
import string
from data import data
import random

def standup_regular_single():
    '''
    Test when a single user creates a standup and send messages
    '''
    clear()

    # create a new user
    user = auth_register("email01@gmail.com", "123456", "Alex", "Abdel")

    # create a new channel
    channel = channels_create(user['token'], 'LOL', True)

    ret = standup_start(user['token'], channel['channel_id'], 5)
    time_finish = ret['time_finish']

    # testing if the standup_active returns the correct result
    ret = standup_active(user['token'], channel['channel_id'])
    assert ret == {
        'is_active': True,
        'time_finish': time_finish,
    }

    standup_send(user['token'], channel['channel_id'], "teststandup01")
    standup_send(user['token'], channel['channel_id'], "teststandup02")
    standup_send(user['token'], channel['channel_id'], "teststandup03")

    # searching the existing messages before the time_finish
    messages = search(user['token'], "teststandup")['messages']
    assert len(messages) == 0

    time.sleep(6)   # Delays for 6 seconds.

    # searching the existing messages after the time_finish
    messages = search(user['token'], "teststandup")['messages']
    assert len(messages) == 1
    expected_message = (
        'alexabdel: teststandup01\n'
        'alexabdel: teststandup02\n'
        'alexabdel: teststandup03\n'
    )
    assert messages[0]['message'] == expected_message

def standup_regular_multiple():
    '''
    Test when a single user creates a standup and multiple users send messages
    '''
    clear()

    # create a new user
    user1 = auth_register("email01@gmail.com", "123456", "Alex", "Abdel")
    user2 = auth_register("email02@gmail.com", "123456", "Amy", "Liu")

    # user1 creates a new channel
    channel = channels_create(user1['token'], 'LOL', True)

    # user1 invites user2 to the channel
    channel_invite(user1['token'], channel['channel_id'], user2['u_id'])

    ret = standup_start(user1['token'], channel['channel_id'], 5)
    time_finish = ret['time_finish']

    # testing if the standup_active returns the correct result
    ret = standup_active(user1['token'], channel['channel_id'])
    assert ret == {
        'is_active': True,
        'time_finish': time_finish,
    }

    standup_send(user1['token'], channel['channel_id'], "teststandup01")
    standup_send(user1['token'], channel['channel_id'], "teststandup02")
    standup_send(user2['token'], channel['channel_id'], "teststandup03")

    # searching the existing messages before the time_finish
    messages = search(user1['token'], "teststandup")['messages']
    assert len(messages) == 0

    time.sleep(6)   # Delays for 6 seconds.

    # searching the existing messages after the time_finish
    messages = search(user1['token'], "teststandup")['messages']
    assert len(messages) == 1
    expected_message = (
        'alexabdel: teststandup01\n'
        'alexabdel: teststandup02\n'
        'amyliu: teststandup03\n'
    )
    assert messages[0]['message'] == expected_message



def test_standup_start_invalid_channel_id():
    '''
    Test if an InputError is raised when an invalid channel_id is passed in to 
    the function standup_start
    '''    
    clear()
    # create a new user
    user = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")

    # create a new channel
    channel = channels_create(user['token'], 'LOL', True)

    invalid_channel_id = channel['channel_id'] + 100

    with raises(InputError):
        standup_start(user['token'], invalid_channel_id, 5)

def test_standup_active_invalid_channel_id():
    '''
    Test if an InputError is raised when an invalid channel_id is passed in to 
    the function standup_active
    '''    
    clear()
    # create a new user
    user = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")

    # create a new channel
    channel = channels_create(user['token'], 'LOL', True)

    standup_start(user['token'], channel['channel_id'], 5)

    # passing in invalid_channel id to standup_active
    invalid_channel_id = channel['channel_id'] + 100
    with raises(InputError):
        standup_active(user['token'], invalid_channel_id)
    

def test_standup_send_invalid_channel_id():
    '''
    Test if an InputError is raised when an invalid channel_id is passed in to 
    the function standup_send
    '''    
    clear()

    # create a new user
    user = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")

    # create a new channel
    channel = channels_create(user['token'], 'LOL', True)

    standup_start(user['token'], channel['channel_id'], 5)

    # passing in invalid_channel id to standup_send
    invalid_channel_id = channel['channel_id'] + 100
    with raises(InputError):
        standup_send(user['token'], invalid_channel_id, "teststandup01")


def test_standup_start_invalid_token():
    '''
    Test if an AccessError is raised when an invalid token is passed in
    to the function standup_start
    '''
    clear()

    # create a new user
    user = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")

    # create a new channel
    channel = channels_create(user['token'], 'LOL', True)

    # invalid format of the token
    invalid_token = f"{user['token']}invalidtoken"
    with raises(AccessError):
        standup_start(invalid_token, channel['channel_id'], 5)

    # invalidated token
    auth_logout(user['token'])
    with raises(AccessError):
        standup_start(user['token'], channel['channel_id'], 5)


def test_standup_active_invalid_token():
    '''
    Test if an AccessError is raised when an invalid token is passed in
    to the function standup_active
    '''
    clear()

    # create a new user
    user = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")

    # create a new channel
    channel = channels_create(user['token'], 'LOL', True)

    # invalid format of the token
    invalid_token = f"{user['token']}invalidtoken"
    with raises(AccessError):
        standup_active(invalid_token, channel['channel_id'])

    # invalidated token
    auth_logout(user['token'])
    with raises(AccessError):
        standup_active(user['token'], channel['channel_id'])


def test_standup_send_invalid_token():
    '''
    Test if an AccessError is raised when an invalid token is passed in
    to the function standup_send
    '''
    clear()

    # create a new user
    user = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")

    # create a new channel
    channel = channels_create(user['token'], 'LOL', True)

    standup_start(user['token'], channel['channel_id'], 5)
    
    # invalid format of the token
    invalid_token = f"{user['token']}invalidtoken"
    with raises(AccessError):
        standup_send(invalid_token, channel['channel_id'], "testing_invalid_token")

    # invalidated token
    auth_logout(user['token'])
    with raises(AccessError):
        standup_send(user['token'], channel['channel_id'], "testing_invalid_token")

def test_standup_start_twice():
    '''
    Test if an InputError is raised when an active standup is currently running 
    in this channel
    '''
    clear()

    # create a new user
    user = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")

    # create a new channel
    channel = channels_create(user['token'], 'LOL', True)

    standup_start(user['token'], channel['channel_id'], 5)

    # standup_start again when there is an active standup currently running 
    # in this channel
    with raises(InputError):
        standup_start(user['token'], channel['channel_id'], 3)



def test_standup_send_long_message():
    '''
    Test if an AccessError is raised when an invalid token is passed in
    to the function standup_send
    '''
    clear()

    # create a new user
    user = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")

    # create a new channel
    channel = channels_create(user['token'], 'LOL', True)

    standup_start(user['token'], channel['channel_id'], 5)

    length = 1001
    letters_and_digits = string.ascii_letters + string.digits
    long_message = ''.join((random.choice(letters_and_digits) for i in range(length)))

    with raises(InputError):
         standup_send(user['token'], channel['channel_id'], long_message)
    
def test_standup_send_not_active():
    '''
    Test if an InputError is raised when an active standup is not currently 
    running in this channel
    '''
    clear()

    # create a new user
    user = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")

    # create a new channel
    channel = channels_create(user['token'], 'LOL', True)

    # An active standup is not currently running in this channel
    with raises(InputError):
        standup_send(user['token'], channel['channel_id'], "test_not_active")
     
def test_standup_send_not_member():
    '''
    Test if an AccessError is raised when an user not belonged to a particular
    channel is sending a message
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
    channel = channels_create(user1['token'], 'COMP1531', False)

    standup_start(user1['token'], channel['channel_id'], 5)

    # user2 is not a member of the channel
    with raises(AccessError):
        standup_send(user2['token'], channel['channel_id'], "test_not_member")

def test_standup_start_not_member():
    '''
    Test if an AccessError is raised when an user not belonged to a particular
    channel is willing to start a new standup in this channel
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
    channel = channels_create(user1['token'], 'COMP1531', False)

    # user2 is not a member of the channel
    with raises(AccessError):
        standup_start(user2['token'], channel['channel_id'], 5)

def test_standup_active_not_member():
    '''
    Test if an AccessError is raised when an user not belonged to a particular
    channel is checking if a channel has a standup
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
    channel = channels_create(user1['token'], 'COMP1531', False)

    standup_start(user1['token'], channel['channel_id'], 5)

    # user2 is not a member of the channel
    with raises(AccessError):
        standup_active(user2['token'], channel['channel_id'])
