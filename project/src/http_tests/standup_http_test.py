'''
http test for the server for the standup functions
'''
import sys
sys.path.append('../')
import random
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import string
import requests
import pytest
import time
import string
import random
from error import InputError, AccessError


# Use this fixture to get the URL of the server. It starts the server for you,
# so you don't need to.
@pytest.fixture
def url():
    '''Generate the url'''
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")

def standup_regular(url):
    '''
    test correct standup for three functions
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_start = f'{url}standup/start'
    url_active = f'{url}standup/active'
    url_standup_send = f'{url}standup/send'
    url_search = f'{url}search'

    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "email01@gmail.com",
        'password': "123456",
        'name_first': "Alexander",
        'name_last': "Abdelrahman",
    })
    user = response.json()

    # create channels
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # standup start
    response = requests.post(url_start, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'length': 5,
    })
    ret = response.json()
    time_finish = ret['time_finish']

    # testing if the standup_active returns the correct result
    response = requests.get(url_active, params={
        'token': user['token'],
        'channel_id':channel['channel_id'],
    })
    result = response.json()
    assert result == {
        'is_active': True,
        'time_finish': time_finish,
    }

    # standup send
    response = requests.post(url_standup_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': "teststandup01",
    })

    response = requests.post(url_standup_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': "teststandup02",
    })

    response = requests.post(url_standup_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': "teststandup03",
    })
    # searching the existing messages before the time_finish
    response = requests.get(url_search, params={
        'token': user['token'],
        'query_str': "teststandup",
    })
    messages = response.json()
    assert len(messages) == 0

    # Delays for 6 seconds.
    time.sleep(6)

    # searching the existing messages after the time_finish
    response = requests.get(url_search, params={
        'token': user['token'],
        'query_str': "teststandup",
    })
    messages = response.json()
    assert len(messages) == 3

def test_standup_start_invalid_channel_id(url):
    '''
    Test if an InputError is raised when an invalid channel_id is passed in to 
    the function standup_start
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_start = f'{url}standup/start'

    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "email01@gmail.com",
        'password': "123456",
        'name_first': "Alexander",
        'name_last': "Abdelrahman",
    })
    user = response.json()

    # create channels
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()
    # test if channel_id is not invalid
    invalid_channel_id = channel['channel_id'] + 100
    response = requests.post(url_start, json={
        'token': user['token'],
        'channel_id': invalid_channel_id,
        'length': 5,
    })
    assert response.status_code == InputError.code

def test_standup_active_invalid_channel_id(url):
    '''
    Test if an InputError is raised when an invalid channel_id is passed in to 
    the function standup_start
    '''    
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_start = f'{url}standup/start'
    url_active = f'{url}standup/active'

    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "email01@gmail.com",
        'password': "123456",
        'name_first': "Alexander",
        'name_last': "Abdelrahman",
    })
    user = response.json()

    # create channels
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # standup start
    response = requests.post(url_start, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'length': 5,
    })

    # passing in invalid_channel id to standup_active
    invalid_channel_id = channel['channel_id'] + 100
    response = requests.get(url_active, params={
        'token': user['token'],
        'channel_id':invalid_channel_id,
    })
    assert response.status_code == InputError.code

def test_standup_send_invalid_channel_id(url):
    '''
    Test if an InputError is raised when an invalid channel_id is passed in to 
    the function standup_send
    '''    
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_start = f'{url}standup/start'
    url_standup_send = f'{url}standup/send'

    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "email01@gmail.com",
        'password': "123456",
        'name_first': "Alexander",
        'name_last': "Abdelrahman",
    })
    user = response.json()

    # create channels
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # standup start
    response = requests.post(url_start, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'length': 5,
    })

    # passing in invalid_channel id to standup_active
    invalid_channel_id = channel['channel_id'] + 100
    response = requests.post(url_standup_send, json={
        'token': user['token'],
        'channel_id': invalid_channel_id,
        'message': "teststandup01",
    })
    assert response.status_code == InputError.code

def test_standup_start_invalid_token(url):
    '''
    Test if an AccessError is raised when an invalid token is passed in
    to the function standup_start
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_start = f'{url}standup/start'
    url_logout = f'{url}auth/logout'
    
    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "email01@gmail.com",
        'password': "123456",
        'name_first': "Alexander",
        'name_last': "Abdelrahman",
    })
    user = response.json()

    # create channels
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # invalid format of the token
    invalid_token = f"{user['token']}invalidtoken"
    response = requests.post(url_start, json={
        'token': invalid_token,
        'channel_id': channel['channel_id'],
        'length': 5,
    })
    assert response.status_code == AccessError.code

    
    # user logout
    requests.post(url_logout, json={
        'token': user['token'],
    })

    # invalidated token
    response = requests.post(url_start, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'length': 5,
    })
    assert response.status_code == AccessError.code

def test_standup_active_invalid_token(url):
    '''
    Test if an AccessError is raised when an invalid token is passed in
    to the function standup_active
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_active = f'{url}standup/active'
    url_logout = f'{url}auth/logout'

    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "email01@gmail.com",
        'password': "123456",
        'name_first': "Alexander",
        'name_last': "Abdelrahman",
    })
    user = response.json()

    # create channels
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # invalid format of the token
    invalid_token = f"{user['token']}invalidtoken"
    response = requests.get(url_active, params={
        'token': invalid_token,
        'channel_id':channel['channel_id'],
    })
    assert response.status_code == AccessError.code

    # user logout
    requests.post(url_logout, json={
        'token': user['token'],
    })

    # invalidated token
    response = requests.get(url_active, params={
        'token': user['token'],
        'channel_id':channel['channel_id'],
    })
    assert response.status_code == AccessError.code

def test_standup_send_invalid_token(url):
    '''
    Test if an AccessError is raised when an invalid token is passed in
    to the function standup_send
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_start = f'{url}standup/start'
    url_standup_send = f'{url}standup/send'
    url_logout = f'{url}auth/logout'

    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "email01@gmail.com",
        'password': "123456",
        'name_first': "Alexander",
        'name_last': "Abdelrahman",
    })
    user = response.json()

    # create channels
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # standup start
    response = requests.post(url_start, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'length': 5,
    })

    # invalid format of the token
    invalid_token = f"{user['token']}invalidtoken"
    response = requests.post(url_standup_send, json={
        'token': invalid_token,
        'channel_id': channel['channel_id'],
        'message': "teststandup01",
    })
    assert response.status_code == AccessError.code

    # user logout
    requests.post(url_logout, json={
        'token': user['token'],
    })

    # invalidated token
    response = requests.post(url_standup_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': "teststandup01",
    })
    assert response.status_code == AccessError.code

def test_standup_start_twice(url):
    '''
    Test if an InputError is raised when an active standup is currently running 
    in this channel
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_start = f'{url}standup/start'
    
    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "email01@gmail.com",
        'password': "123456",
        'name_first': "Alexander",
        'name_last': "Abdelrahman",
    })
    user = response.json()

    # create channels
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # standup start
    response = requests.post(url_start, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'length': 5,
    })

    # standup_start again when there is an active standup currently running 
    # in this channel
    response = requests.post(url_start, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'length': 3,
    })
    assert response.status_code == InputError.code

def test_standup_send_long_message(url):
    '''
    Test if an AccessError is raised when an invalid token is passed in
    to the function standup_send
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_start = f'{url}standup/start'
    url_standup_send = f'{url}standup/send'
    
    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "email01@gmail.com",
        'password': "123456",
        'name_first': "Alexander",
        'name_last': "Abdelrahman",
    })
    user = response.json()

    # create channels
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # standup start
    response = requests.post(url_start, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'length': 5,
    })
    # test long message
    length = 1001
    letters_and_digits = string.ascii_letters + string.digits
    long_message = ''.join((random.choice(letters_and_digits) for i in range(length)))
    url_standup_send = f'{url}standup/send'
    response = requests.post(url_standup_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': long_message,
    })
    assert response.status_code == InputError.code

def test_standup_send_not_active(url):
    '''
    Test if an InputError is raised when an active standup is not currently 
    running in this channel
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_standup_send = f'{url}standup/send'

    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "email01@gmail.com",
        'password': "123456",
        'name_first': "Alexander",
        'name_last': "Abdelrahman",
    })
    user = response.json()

    # create channels
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # An active standup is not currently running in this channel
    response = requests.post(url_standup_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': "test_not_active",
    })
    assert response.status_code == InputError.code

def test_standup_send_not_member(url):
    '''
    Test if an AccessError is raised when an user not belonged to a particular
    channel is sending a message
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_start = f'{url}standup/start'
    url_standup_send = f'{url}standup/send'
    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user1 = response.json()

    response = requests.post(url_register, json={
        'email': "h.styles@gmail.com",
        'password': "12345678",
        'name_first': "Harry",
        'name_last': "Styles",
    })
    user2 = response.json()

    # create channels
    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': 'COMP1531',
        'is_public': False,
    })
    channel = response.json()

    # standup start
    response = requests.post(url_start, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'length': 5,
    })

    # user2 is not a member of the channel
    response = requests.post(url_standup_send, json={
        'token': user2['token'],
        'channel_id': channel['channel_id'],
        'message': "test_not_member",
    })
    assert response.status_code == AccessError.code

def test_standup_start_not_member(url):
    '''
    Test if an AccessError is raised when an user not belonged to a particular
    channel is willing to start a new standup in this channel
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_start = f'{url}standup/start'
    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user1 = response.json()

    response = requests.post(url_register, json={
        'email': "h.styles@gmail.com",
        'password': "12345678",
        'name_first': "Harry",
        'name_last': "Styles",
    })
    user2 = response.json()

    # create channels
    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': 'COMP1531',
        'is_public': False,
    })
    channel = response.json()

    # user2 is not a member of the channel
    response = requests.post(url_start, json={
        'token': user2['token'],
        'channel_id': channel['channel_id'],
        'length': 5,
    })
    assert response.status_code == AccessError.code

def test_standup_active_not_member(url):
    '''
    Test if an AccessError is raised when an user not belonged to a particular
    channel is checking if a channel has a standup
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_start = f'{url}standup/start'
    url_active = f'{url}standup/active'
    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user1 = response.json()

    response = requests.post(url_register, json={
        'email': "h.styles@gmail.com",
        'password': "12345678",
        'name_first': "Harry",
        'name_last': "Styles",
    })
    user2 = response.json()

    # create channels
    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': 'COMP1531',
        'is_public': False,
    })
    channel = response.json()

    # stand up
    response = requests.post(url_start, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'length': 5,
    })

    # user2 is not a member of the channel
    response = requests.get(url_active, params={
        'token': user2['token'],
        'channel_id':channel['channel_id'],
    })
    assert response.status_code == AccessError.code

