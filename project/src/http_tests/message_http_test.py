'''
http test for the server for the message functions
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
from data import data
from other import clear
import time
from datetime import datetime, timezone
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

def test_message_send_regular1(url):
    '''
    test if an member who is not an owner of flockr in channel can send message
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_search = f'{url}search'

    # initiate data
    # register users
    requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })

    response = requests.post(url_register, json={
        'email': "s.taylor@gmail.com",
        'password': "12345678",
        'name_first': "Swift",
        'name_last': "Taylor",
    })
    user2 = response.json() 

    # create channels
    response = requests.post(url_create, json={
        'token': user2['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # test message_send() can correctly run if authorised user who is
    # not owner of flockr in channel sent messsage.
    requests.post(url_send, json={
        'token': user2['token'],
        'channel_id': channel['channel_id'],
        'message': "I love COMP1531!",
    })
    

    response = requests.get(url_search, params={
        'token': user2['token'],
        'query_str': "I love COMP1531!",
    })
    result = response.json()
    assert result['messages'][0]['message'] == "I love COMP1531!"

def test_message_send_regular2(url):
    '''
    test if an owner of flockr who is not in channel can send message
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_search = f'{url}search'

    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })
    user1 = response.json() 

    response = requests.post(url_register, json={
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json() 

    # create channels
    response = requests.post(url_create, json={
        'token': user2['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # test if an owner of flockr but not in channel can send message
    requests.post(url_send, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'message': "COMP1531 is fun!"
    })

    response = requests.get(url_search, params={
        'token': user2['token'],
        'query_str': "COMP1531 is fun!",
    })
    result = response.json()
    assert result['messages'][0]['message'] == "COMP1531 is fun!"
    

def test_message_send_message_too_long(url):
    '''
    Test if a InputError error is received when the message entered 
    has more that 1000 characters
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    
    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })
    user = response.json() 

    # create channels
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # check if it will recieve InputError error
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': "I love COMP1531!" * 100
    })
    assert response.status_code == InputError.code

def test_message_send_message_no_permission(url):
    '''
    Test if a AccessError error is received when the authorised user is
    not an owner of flockr or in channel.
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    
    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })
    user1 = response.json() 

    response = requests.post(url_register, json={
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json() 

    # create channels
    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # test if will recieve AccessError error
    response = requests.post(url_send, json={
        'token': user2['token'],
        'channel_id': channel['channel_id'],
        'message': "I love COMP1531!"
    })
    assert response.status_code == AccessError.code

def test_message_remove_regular1(url):
    '''
    test if an authorised user is a member who sent the message in channel
    but not an owner of flockr or an owner of channel can remove message
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_remove = f'{url}message/remove'
    url_join = f'{url}channel/join'
    url_search = f'{url}search'

    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })
    user1 = response.json() 

    response = requests.post(url_register, json={
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json() 

    # create a channel
    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # user2 join the channel
    response = requests.post(url_join, json={
        'token': user2['token'],
        'channel_id': channel['channel_id'],
    })

    # user2 sends an message
    response = requests.post(url_send, json={
        'token': user2['token'],
        'channel_id': channel['channel_id'],
        'message': "I love COMP1531!",
    })
    message = response.json()

    # check if the person who sent the message can correctly remove
    response = requests.delete(url_remove, json={
        'token': user2['token'],
        'message_id': message['message_id'],
    })

    response = requests.get(url_search, params={
        'token': user2['token'],
        'query_str': "I love COMP1531!",
    })
    result = response.json()
    assert result['messages'] == []
    
def test_message_remove_regular_regular2(url):
    '''
    test if an authorised user is an owner of channel but not an owner
    of flockr or a person who sent the message can remove message
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_remove = f'{url}message/remove'
    url_join = f'{url}channel/join'
    url_search = f'{url}search'

    # initiate data
    # register users
    requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })

    response = requests.post(url_register, json={
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json() 

    response = requests.post(url_register, json={
        'email': "email_01@gmail.com",
        'password': "12345678",
        'name_first': "ABC",
        'name_last': "DEFG",
    })
    user3 = response.json() 


    # create a channel
    response = requests.post(url_create, json={
        'token': user2['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # user2, 3 join the channel
    requests.post(url_join, json={
        'token': user3['token'],
        'channel_id': channel['channel_id'],
    })

    # user3 sends an message
    response = requests.post(url_send, json={
        'token': user3['token'],
        'channel_id': channel['channel_id'],
        'message': "I love COMP1531!",
    })
    message = response.json()

    # check if the owner of the channel can correctly remove
    response = requests.delete(url_remove, json={
        'token': user2['token'],
        'message_id': message['message_id'],
    })

    response = requests.get(url_search, params={
        'token': user2['token'],
        'query_str': "I love COMP1531!",
    })
    result = response.json()
    assert result['messages'] == []

def test_message_remove_regular_regular3(url):
    '''
    test if an authorised user is an owner of flockr but not an owner
    of channel or a person who sent the message can remove message
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_remove = f'{url}message/remove'
    url_join = f'{url}channel/join'
    url_search = f'{url}search'

    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })
    user1 = response.json() 

    response = requests.post(url_register, json={
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json() 

    response = requests.post(url_register, json={
        'email': "email_01@gmail.com",
        'password': "12345678",
        'name_first': "ABC",
        'name_last': "DEFG",
    })
    user3 = response.json() 


    # create a channel
    response = requests.post(url_create, json={
        'token': user2['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # user3 join the channel
    requests.post(url_join, json={
        'token': user3['token'],
        'channel_id': channel['channel_id'],
    })


    # user3 sends an message
    response = requests.post(url_send, json={
        'token': user3['token'],
        'channel_id': channel['channel_id'],
        'message': "I love COMP1531!",
    })
    message = response.json()

    # check if the owner of flockr can correctly remove by
    response = requests.delete(url_remove, json={
        'token': user1['token'],
        'message_id': message['message_id'],
    })

    response = requests.get(url_search, params={
        'token': user2['token'],
        'query_str': "I love COMP1531!",
    })
    result = response.json()
    assert result['messages'] == []


def test_message_remove_messageid_not_exists(url):
    '''
    Test if a InputError error is received when the message no longer exists
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_remove = f'{url}message/remove'
    
    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })
    user = response.json() 

    # create channels
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # send an message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': "I love COMP1531!"
    })
    message = response.json()

    # check if there is a InputError error
    invalid_message_id = message['message_id'] + 1000
    response = requests.delete(url_remove, json={
        'token': user['token'],
        'message_id': invalid_message_id,
    })
    assert response.status_code == InputError.code

def test_message_remove_message_was_removed(url):
    '''
    Test if a InputError error is received when the message no longer exists
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_remove = f'{url}message/remove'
    
    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })
    user = response.json() 

    # create channels
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # send an message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': "I love COMP1531!"
    })
    message = response.json()

    # remove the message
    requests.delete(url_remove, json={
        'token': user['token'],
        'message_id': message['message_id'],
    })

    # check if there is a InputError error
    response = requests.delete(url_remove, json={
        'token': user['token'],
        'message_id': message['message_id'],
    })
    assert response.status_code == InputError.code

def test_message_remove_message_no_permission(url):
    '''
    Test if a AccessError error is received when the aurothised user has no permission
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_remove = f'{url}message/remove'
    
    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })
    user1 = response.json() 

    # join the channel
    response = requests.post(url_register, json={
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json() 

    # create channels
    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # send an message
    response = requests.post(url_send, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'message': "I love COMP1531!"
    })
    message = response.json()

    # check if there is a AccessError error
    response = requests.delete(url_remove, json={
        'token': user2['token'],
        'message_id': message['message_id'],
    })
    assert response.status_code == AccessError.code

def test_message_edit_regular1(url):
    '''
    test if an authorised user is a member who sent the message in channel
    but not an owner of flockr or an owner of channel can edit the message
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_edit = f'{url}message/edit'
    url_join = f'{url}channel/join'
    url_search = f'{url}search'

    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })
    user1 = response.json() 

    response = requests.post(url_register, json={
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json() 

    # create a channel
    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # user2 join the channel
    response = requests.post(url_join, json={
        'token': user2['token'],
        'channel_id': channel['channel_id'],
    })

    # user2 sends an message
    response = requests.post(url_send, json={
        'token': user2['token'],
        'channel_id': channel['channel_id'],
        'message': "I love COMP1531!",
    })
    message = response.json()

    # check if the person who sent the message can correctly edit
    response = requests.put(url_edit, json={
        'token': user2['token'],
        'message_id': message['message_id'],
        'message': "COMP1531 is cool!"
    })

    # search if the modified message match the correct string
    response = requests.get(url_search, params={
        'token': user2['token'],
        'query_str': "COMP1531 is cool!",
    })
    result = response.json()
    assert result['messages'][0]['message'] == "COMP1531 is cool!"
    
def test_message_edit_regular_regular2(url):
    '''
    test if an authorised user is an owner of channel but not an owner
    of flockr or a person who sent the message can remove message
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_edit = f'{url}message/edit'
    url_join = f'{url}channel/join'
    url_search = f'{url}search'

    # initiate data
    # register users
    requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })

    response = requests.post(url_register, json={
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json() 

    response = requests.post(url_register, json={
        'email': "email_01@gmail.com",
        'password': "12345678",
        'name_first': "ABC",
        'name_last': "DEFG",
    })
    user3 = response.json() 


    # create a channel
    response = requests.post(url_create, json={
        'token': user2['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # user2, 3 join the channel
    requests.post(url_join, json={
        'token': user3['token'],
        'channel_id': channel['channel_id'],
    })

    # user3 sends an message
    response = requests.post(url_send, json={
        'token': user3['token'],
        'channel_id': channel['channel_id'],
        'message': "I love COMP1531!",
    })
    message = response.json()

    # check if the owner of the channel can correctly edit
    response = requests.put(url_edit, json={
        'token': user2['token'],
        'message_id': message['message_id'],
        'message': "COMP1531 is cool!",
    })

    response = requests.get(url_search, params={
        'token': user2['token'],
        'query_str': "COMP1531 is cool!",
    })
    result = response.json()
    assert result['messages'][0]['message'] == "COMP1531 is cool!"

def test_message_edit_regular_regular3(url):
    '''
    test if an authorised user is an owner of flockr but not an owner
    of channel or a person who sent the message can remove message
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_edit = f'{url}message/edit'
    url_join = f'{url}channel/join'
    url_search = f'{url}search'

    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })
    user1 = response.json() 

    response = requests.post(url_register, json={
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json() 

    response = requests.post(url_register, json={
        'email': "email_01@gmail.com",
        'password': "12345678",
        'name_first': "ABC",
        'name_last': "DEFG",
    })
    user3 = response.json() 


    # create a channel
    response = requests.post(url_create, json={
        'token': user2['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # user3 join the channel
    requests.post(url_join, json={
        'token': user3['token'],
        'channel_id': channel['channel_id'],
    })


    # user3 sends an message
    response = requests.post(url_send, json={
        'token': user3['token'],
        'channel_id': channel['channel_id'],
        'message': "I love COMP1531!",
    })
    message = response.json()

    # check if the owner of flockr can correctly edit
    response = requests.put(url_edit, json={
        'token': user1['token'],
        'message_id': message['message_id'],
        'message': "COMP1531 is cool!",
    })

    response = requests.get(url_search, params={
        'token': user2['token'],
        'query_str': "COMP1531 is cool!",
    })
    result = response.json()
    assert result['messages'][0]['message'] == "COMP1531 is cool!"

def test_message_edit_message_no_permission(url):
    '''
    Test if a AccessError error is received when the message no longer exists
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_edit = f'{url}message/edit'
    
    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })
    user1 = response.json() 

    # join the channel
    response = requests.post(url_register, json={
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json() 

    # create channels
    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # send an message
    response = requests.post(url_send, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'message': "I love COMP1531!"
    })
    message = response.json()

    # check if there is a AccessError error
    response = requests.put(url_edit, json={
        'token': user2['token'],
        'message_id': message['message_id'],
        'message': "COMP1531 is cool!"
    })
    assert response.status_code == AccessError.code

def test_message_send_invalid_token1(url):
    '''
    Test if a AccessError error is received when the token is invalid
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'

    # initiate data
    response = requests.post(url_register, json={
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user = response.json()

    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # check if receive AccessError error
    response = requests.post(url_send, json={
        'token': "ThisIsAnInvalidToken",
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    assert response.status_code == AccessError.code

def test_message_send_invalid_token2(url):
    '''
    Test if a AccessError error is received when the token is invalid
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_logout = f'{url}auth/logout'

    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # user logout
    requests.post(url_logout, json={
        'token': user['token'],
    })

    # check if receive AccessError error
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    assert response.status_code == AccessError.code

def test_message_remove_invalid_token1(url):
    '''
    Test if a AccessError error is received when the token is invalid
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_remove = f'{url}message/remove'

    # initiate data
    # register user
    response = requests.post(url_register, json={
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user = response.json()

    # create channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # send message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # check if receive AccessError error
    response = requests.delete(url_remove, json={
        'token': "ThisIsAnInvalidToken",
        'message_id': message['message_id'],
    })
    assert response.status_code == AccessError.code

def test_message_remove_invalid_token2(url):
    '''
    Test if a AccessError error is received when the token is invalid
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_logout = f'{url}auth/logout'
    url_remove = f'{url}message/remove'

    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # user logout
    requests.post(url_logout, json={
        'token': user['token'],
    })

    # check if receive AccessError error
    response = requests.delete(url_remove, json={
        'token': user['token'],
        'message_id': message['message_id'],
    })
    assert response.status_code == AccessError.code


def test_message_edit_invalid_token1(url):
    '''
    Test if a AccessError error is received when the token is invalid
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_edit = f'{url}message/edit'
    url_send = f'{url}message/send'

    # initiate data
    # register user
    response = requests.post(url_register, json={
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user = response.json()

    # create channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # send message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()


    # check if receive AccessError error
    response = requests.put(url_edit, json={
        'token': "ThisIsAnInvalidToken",
        'message_id': message['message_id'],
        'message': 'Hello Hello',
    })
    assert response.status_code == AccessError.code

def test_message_edit_invalid_token2(url):
    '''
    Test if a AccessError error is received when the token is invalid
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_logout = f'{url}auth/logout'
    url_edit = f'{url}message/edit'

    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # user logout
    requests.post(url_logout, json={
        'token': user['token'],
    })

    # check if receive AccessError error
    response = requests.put(url_edit, json={
        'token': user['token'],
        'message_id': message['message_id'],
        'message': "Good!"
    })
    assert response.status_code == AccessError.code

def test_message_sendlater_regular(url):
    '''
    test if an message_sendlater can corretly run
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_sendlater = f'{url}message/sendlater'
    url_search = f'{url}search'

    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })
    user = response.json() 

    # create channels
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    dt_now = datetime.utcnow()
    time_now = int(dt_now.replace(tzinfo=timezone.utc).timestamp())
    time_sent = time_now + 2
    # test if a AccessError error is raised
    response = requests.post(url_sendlater, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': "I love COMP1531!",
        'time_sent': time_sent,
    })
    response = requests.get(url_search, params={
        'token': user['token'],
        'query_str': "I love COMP1531!",
    })
    result = response.json()
    assert result['messages'] == []

    time.sleep(4)
    response = requests.get(url_search, params={
        'token': user['token'],
        'query_str': "I love COMP1531!",
    })
    result = response.json()
    assert result['messages'][0]['message'] == "I love COMP1531!"

def test_message_sendlater_invalid_channel_id(url):
    '''
    test if an InputError is raised if channel_id is not valid
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_sendlater = f'{url}message/sendlater'

    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })
    user = response.json() 

    # create channels
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    dt_now = datetime.utcnow()
    time_now = int(dt_now.replace(tzinfo=timezone.utc).timestamp())
    time_sent = time_now + 2
    invalid_channel_id = channel['channel_id'] + 100
    # test if a InputError error is raised
    response = requests.post(url_sendlater, json={
        'token': user['token'],
        'channel_id': invalid_channel_id,
        'message': "I love COMP1531",
        'time_sent': time_sent,
    })
    assert response.status_code == InputError.code

def test_message_sendlater_message_too_long(url):
    '''
    test if an InputError is raised if message is too long
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_sendlater = f'{url}message/sendlater'

    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })
    user = response.json() 

    # create channels
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    dt_now = datetime.utcnow()
    time_now = int(dt_now.replace(tzinfo=timezone.utc).timestamp())
    time_sent = time_now + 2
    # test if a InputError error is raised
    response = requests.post(url_sendlater, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': "I love COMP1531" * 300,
        'time_sent': time_sent,
    })
    assert response.status_code == InputError.code

def test_message_sendlater_time_sent_in_past(url):
    '''
    test if an InputError is raised if Time sent is a time in the past
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_sendlater = f'{url}message/sendlater'

    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })
    user = response.json() 

    # create channels
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    dt_now = datetime.utcnow()
    time_now = int(dt_now.replace(tzinfo=timezone.utc).timestamp())
    time_past = time_now - 10
    # test if a InputError error is raised
    response = requests.post(url_sendlater, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': "I love COMP1531",
        'time_sent': time_past,
    })
    assert response.status_code == InputError.code

def test_message_sendlater_user_not_in_channel(url):
    '''
    test if an InputError is raised if channel_id is not valid
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_sendlater = f'{url}message/sendlater'

    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })
    user1 = response.json() 

    response = requests.post(url_register, json={
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Smith",
    })
    user2 = response.json() 

    # create channels
    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    dt_now = datetime.utcnow()
    time_now = int(dt_now.replace(tzinfo=timezone.utc).timestamp())
    time_sent = time_now + 2
    # test if a AccessError error is raised
    response = requests.post(url_sendlater, json={
        'token': user2['token'],
        'channel_id': channel['channel_id'],
        'message': "I love COMP1531",
        'time_sent': time_sent,
    })
    assert response.status_code == AccessError.code

def test_message_sendlater_invalid_token1(url):
    '''
    test if an AccessError is raised if token passed in is invalid
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_sendlater = f'{url}message/sendlater'

    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })
    user = response.json() 

    # create channels
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    dt_now = datetime.utcnow()
    time_now = int(dt_now.replace(tzinfo=timezone.utc).timestamp())
    time_sent = time_now + 2
    # test if a InputError error is raised
    response = requests.post(url_sendlater, json={
        'token': 'ThisIsAnInvalidToken',
        'channel_id': channel['channel_id'],
        'message': "I love COMP1531",
        'time_sent': time_sent,
    })
    assert response.status_code == AccessError.code

def test_message_sendlater_invalid_token2(url):
    '''
    test if an AccessError is raised if token passed in is invalid
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_sendlater = f'{url}message/sendlater'
    url_logout = f'{url}auth/logout'

    # initiate data
    # register users
    response = requests.post(url_register, json={
        'email': "h.smith@gmail.com",
        'password': "12345678",
        'name_first': "Hadise",
        'name_last': "Smith",
    })
    user = response.json() 

    # create channels
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'LOL',
        'is_public': True,
    })
    channel = response.json()

    requests.post(url_logout, json={
        'token': user['token'],
    })

    dt_now = datetime.utcnow()
    time_now = int(dt_now.replace(tzinfo=timezone.utc).timestamp())
    time_sent = time_now + 2
    # test if a AccessError error is raised
    response = requests.post(url_sendlater, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': "I love COMP1531",
        'time_sent': time_sent,
    })
    assert response.status_code == AccessError.code
    
def test_message_react_regular1(url):
    '''
    Test if message_react can correct work
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_react = f'{url}message/react'
    url_search = f'{url}search'
    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # react message
    response = requests.post(url_react, json={
        'token': user['token'],
        'message_id': message['message_id'],
        'react_id': 1,
    })

    # check if the message is reacted by user and the key 'is_this_user_reacted' is correct
    response = requests.get(url_search, params={
        'token': user['token'],
        'query_str': "Hello",
    })
    result = response.json()
    assert result['messages'][0]['reacts'][0]['u_ids'] == [user['u_id']]
    assert result['messages'][0]['reacts'][0]['is_this_user_reacted'] == True

def test_message_react_regular2(url):
    '''
    Test if message_react can correct work
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_join = f'{url}channel/join'
    url_send = f'{url}message/send'
    url_react = f'{url}message/react'
    url_search = f'{url}search'
    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user1 = response.json()

    response = requests.post(url_register, json={
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # join a channel
    response = requests.post(url_join, json={
        'token': user2['token'],
        'channel_id': channel['channel_id'],
    })

    # send a message
    response = requests.post(url_send, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()
    # react message
    response = requests.post(url_react, json={
        'token': user1['token'],
        'message_id': message['message_id'],
        'react_id': 1,
    })
    # check if the key 'is_this_user_reacted' is correct
    response = requests.get(url_search, params={
        'token': user2['token'],
        'query_str': "Hello",
    })
    result = response.json()
    assert result['messages'][0]['reacts'][0]['is_this_user_reacted'] == False

def test_message_react_invalid_message_id(url):
    '''
    Test if an InputError is raised if message_id is not a valid message 
    within a channel that the authorised user has joined
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_react = f'{url}message/react'

    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()
    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # check if an InputError is raised if message_id is invalid
    invalid_message_id = message['message_id'] + 100
    response = requests.post(url_react, json={
        'token': user['token'],
        'message_id': invalid_message_id,
        'react_id': 1,
    })
    assert response.status_code == InputError.code

def test_message_react_invalid_not_in_channel(url):
    '''
    Test if an InputError is raised if message_id is not a valid message 
    within a channel that the authorised user has joined
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_react = f'{url}message/react'
    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user1 = response.json()

    response = requests.post(url_register, json={
        'email': "s.abcd@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()
    # check if an InputError is raised if token is invalid
    response = requests.post(url_react, json={
        'token': user2['token'],
        'message_id': message['message_id'],
        'react_id': 1,
    })
    assert response.status_code == InputError.code

def test_message_react_invalid_react_id(url):
    '''
    Test if an InputError is raised if react_id is not a valid React ID. 
    The only valid react ID the frontend has is 1
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_react = f'{url}message/react'

    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()
    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # check if an InputError is raised if react_id is invalid
    invalid_react_id = 2
    response = requests.post(url_react, json={
        'token': user['token'],
        'message_id':  message['message_id'],
        'react_id': invalid_react_id,
    })
    assert response.status_code == InputError.code

def test_message_react_already_reacted(url):   
    '''
    Test if an InputError is raised if Message with ID message_id already 
    contains an active React with ID react_id from the authorised user
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_react = f'{url}message/react'

    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()
    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()
    response = requests.post(url_react, json={
        'token': user['token'],
        'message_id':  message['message_id'],
        'react_id': 1,
    })
    # check if an InputError is raised if the message is already reacted by authorised user
    response = requests.post(url_react, json={
        'token': user['token'],
        'message_id':  message['message_id'],
        'react_id': 1,
    })
    assert response.status_code == InputError.code

def test_message_react_invalid_token1(url):
    '''
    Test if an AccessError error is received when the token is invalid
    '''
    '''
    Test if an InputError is raised if Message with ID message_id already 
    contains an active React with ID react_id from the authorised user
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_react = f'{url}message/react'

    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()
    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # check if it will raise AccessError when token is invalid
    response = requests.post(url_react, json={
        'token': "ThisIsAnInvalidToken",
        'message_id':  message['message_id'],
        'react_id': 1,
    })
    assert response.status_code == AccessError.code

def test_message_react_invalid_token2(url):
    '''
    Test if an AccessError error is received when the token is invalid
    '''

    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_react = f'{url}message/react'
    url_logout = f'{url}auth/logout'

    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()
    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()
    # user logout
    requests.post(url_logout, json={
        'token': user['token'],
    })
    # check if it will raise AccessError when token is invalid
    response = requests.post(url_react, json={
        'token': user['token'],
        'message_id':  message['message_id'],
        'react_id': 1,
    })
    assert response.status_code == AccessError.code

def test_message_unreact_regular1(url):
    '''
    Test if message_react can correct work
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_react = f'{url}message/react'
    url_unreact = f'{url}message/unreact'
    url_search = f'{url}search'
    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # react message
    response = requests.post(url_react, json={
        'token': user['token'],
        'message_id': message['message_id'],
        'react_id': 1,
    })

    # unreact message
    response = requests.post(url_unreact, json={
        'token': user['token'],
        'message_id': message['message_id'],
        'react_id': 1,
    })
    
    # check if the message is unreacted by user and the key 'is_this_user_reacted' is correct
    response = requests.get(url_search, params={
        'token': user['token'],
        'query_str': "Hello",
    })
    result = response.json()
    assert result['messages'][0]['reacts'][0]['u_ids'] == []
    assert result['messages'][0]['reacts'][0]['is_this_user_reacted'] == False

def test_message_unreact_regular2(url):
    '''
    Test if message_react can correct work
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_join = f'{url}channel/join'
    url_send = f'{url}message/send'
    url_react = f'{url}message/react'
    url_unreact = f'{url}message/unreact'
    url_search = f'{url}search'
    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user1 = response.json()

    response = requests.post(url_register, json={
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # join a channel
    response = requests.post(url_join, json={
        'token': user2['token'],
        'channel_id': channel['channel_id'],
    })

    # send a message
    response = requests.post(url_send, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()
    # react message
    response = requests.post(url_react, json={
        'token': user1['token'],
        'message_id': message['message_id'],
        'react_id': 1,
    })

    response = requests.post(url_react, json={
        'token': user2['token'],
        'message_id': message['message_id'],
        'react_id': 1,
    })
    # unreact message
    response = requests.post(url_unreact, json={
        'token': user1['token'],
        'message_id': message['message_id'],
        'react_id': 1,
    })
    # check if the key 'is_this_user_reacted' is correct
    response = requests.get(url_search, params={
        'token': user2['token'],
        'query_str': "Hello",
    })
    result = response.json()
    assert result['messages'][0]['reacts'][0]['is_this_user_reacted'] == True

def test_message_unreact_invalid_message_id(url):
    '''
    Test if an InputError is raised if message_id is not a valid message 
    within a channel that the authorised user has joined
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_react = f'{url}message/react'
    url_unreact = f'{url}message/unreact'
    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # react message
    response = requests.post(url_react, json={
        'token': user['token'],
        'message_id': message['message_id'],
        'react_id': 1,
    })

    # check if an InputError is raised if message_id is invalid
    invalid_message_id = message['message_id'] + 100
    response = requests.post(url_unreact, json={
        'token': user['token'],
        'message_id': invalid_message_id,
        'react_id': 1,
    })
    assert response.status_code == InputError.code

def test_message_unreact_invalid_not_in_channel(url):
    '''
    Test if an InputError is raised if message_id is not a valid message 
    within a channel that the authorised user has joined
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_join = f'{url}channel/join'
    url_send = f'{url}message/send'
    url_react = f'{url}message/react'
    url_unreact = f'{url}message/unreact'
    url_channel_leave = f'{url}channel/leave'
    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user1 = response.json()

    response = requests.post(url_register, json={
        'email': "s.abcd@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # join a channel
    response = requests.post(url_join, json={
        'token': user2['token'],
        'channel_id': channel['channel_id'],
    })

    # react message
    response = requests.post(url_react, json={
        'token': user2['token'],
        'message_id': message['message_id'],
        'react_id': 1,
    })

    # leave a channel
    requests.post(url_channel_leave, json={
        'token': user2['token'],
        'channel_id': channel['channel_id'],
    })

    # check if an InputError is raised if message_id is invalid
    response = requests.post(url_unreact, json={
        'token': user2['token'],
        'message_id': message['message_id'],
        'react_id': 1,
    })
    assert response.status_code == InputError.code

def test_message_unreact_invalid_react_id(url):
    '''
    Test if an InputError is raised if react_id is not a valid React ID. 
    The only valid react ID the frontend has is 1
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_react = f'{url}message/react'
    url_unreact = f'{url}message/unreact'

    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()
    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # react message
    response = requests.post(url_react, json={
        'token': user['token'],
        'message_id':  message['message_id'],
        'react_id': 1,
    })
    # check if an InputError is raised if react_id is invalid
    invalid_react_id = 2
    response = requests.post(url_unreact, json={
        'token': user['token'],
        'message_id': message['message_id'],
        'react_id': invalid_react_id,
    })
    assert response.status_code == InputError.code

def test_message_unreact_not_reacted(url):
    '''
    Test if an InputError is raised if Message with ID message_id 
    does not contain an active React with ID react_id
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_unreact = f'{url}message/unreact'

    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()
    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # check if an InputError is raised if the message is already reacted by authorised user
    response = requests.post(url_unreact, json={
        'token': user['token'],
        'message_id': message['message_id'],
        'react_id': 1,
    })
    assert response.status_code == InputError.code

def test_message_unreact_invalid_token1(url):
    '''
    Test if an AccessError error is received when the token is invalid
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_react = f'{url}message/react'
    url_unreact = f'{url}message/unreact'

    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()
    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # react message
    response = requests.post(url_react, json={
        'token': user['token'],
        'message_id':  message['message_id'],
        'react_id': 1,
    })
    # check if an InputError is raised if react_id is invalid
    response = requests.post(url_unreact, json={
        'token': "ThisIsAnInvalidToken",
        'message_id': message['message_id'],
        'react_id': 1,
    })
    assert response.status_code == InputError.code

def test_message_unreact_invalid_token2(url):
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_react = f'{url}message/react'
    url_unreact = f'{url}message/unreact'
    url_logout = f'{url}auth/logout'

    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()
    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # react message
    response = requests.post(url_react, json={
        'token': user['token'],
        'message_id':  message['message_id'],
        'react_id': 1,
    })

    # user logout
    requests.post(url_logout, json={
        'token': user['token'],
    })

    # check if an InputError is raised if react_id is invalid
    response = requests.post(url_unreact, json={
        'token': user['token'],
        'message_id': message['message_id'],
        'react_id': 1
    })
    assert response.status_code == InputError.code
    
def test_message_pin_regular1(url):
    '''
    Test if message_pin can correct work
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_pin = f'{url}message/pin'
    url_search = f'{url}search'
    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # pin message
    response = requests.post(url_pin, json={
        'token': user['token'],
        'message_id': message['message_id'],
    })

    # check if the message is reacted by user and the key 'is_this_user_reacted' is correct
    response = requests.get(url_search, params={
        'token': user['token'],
        'query_str': "Hello",
    })
    result = response.json()
    assert result['messages'][0]['is_pinned'] == True

def test_message_pin_regular2(url):
    '''
    Test if message_pin can correct work
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_join = f'{url}channel/join'
    url_send = f'{url}message/send'
    url_pin = f'{url}message/pin'
    url_search = f'{url}search'
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
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # join a channel
    response = requests.post(url_join, json={
        'token': user2['token'],
        'channel_id': channel['channel_id'],
    })

    # send a message
    response = requests.post(url_send, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # pin message
    response = requests.post(url_pin, json={
        'token': user1['token'],
        'message_id': message['message_id'],
    })

    # check if the message is reacted by user and the key 'is_this_user_reacted' is correct
    response = requests.get(url_search, params={
        'token': user2['token'],
        'query_str': "Hello",
    })
    result = response.json()
    assert result['messages'][0]['is_pinned'] == True

# tests for InputError
def test_message_pin_invalid_message_id(url):
    '''
    Test if an InputError is raised if message_id is not a valid message 
    within a channel that the authorised user has joined
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_pin = f'{url}message/pin'

    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # check if an InputError is raised if message_id is invalid
    invalid_message_id = message['message_id'] + 100
    response = requests.post(url_pin, json={
        'token': user['token'],
        'message_id': invalid_message_id,
    })
    assert response.status_code == InputError.code

def test_message_pin_already_pinned(url):
    '''
    Test if an InputError is raised if Message with ID message_id already 
    pinned
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_pin = f'{url}message/pin'
    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # pin message
    response = requests.post(url_pin, json={
        'token': user['token'],
        'message_id': message['message_id'],
    })

    # check if an InputError is raised if the message is 
    # already pined by authorised user
    response = requests.post(url_pin, json={
        'token': user['token'],
        'message_id': message['message_id'],
    })
    assert response.status_code == InputError.code

# tests for AccessError
def test_message_pin_not_a_member(url):
    '''
    Test if message_pin can correct work
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_pin = f'{url}message/pin'
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
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()
    # check if an AccessError is raised if the authorised user is not a member of the channel that 
    # the message is within
    response = requests.post(url_pin, json={
        'token': user2['token'],
        'message_id': message['message_id'],
    })
    assert response.status_code == AccessError.code

def test_message_pin_authorised_user_not_an_owner(url):
    '''
    Test if an authorised user is not an owner
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_invite = f'{url}channel/invite'
    url_send = f'{url}message/send'
    url_pin = f'{url}message/pin'
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
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # invite to a channel
    response = requests.post(url_invite, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })

    # send a message
    response = requests.post(url_send, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # check if an AccessError is raised if the authorised user is not an owner
    response = requests.post(url_pin, json={
        'token': user2['token'],
        'message_id': message['message_id'],
    })
    assert response.status_code == AccessError.code

# tests for invalid token
def test_message_pin_invalid_token1(url):
    '''
    Test if an AccessError error is received when the token is invalid
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_pin = f'{url}message/pin'
    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # check if it will raise AccessError when token is invalid
    response = requests.post(url_pin, json={
        'token': "ThisIsAnInvalidToken",
        'message_id': message['message_id'],
    })
    assert response.status_code == AccessError.code

def test_message_pin_invalid_token2(url):
    '''
    Test if an AccessError error is received when the token is invalid
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_logout = f'{url}auth/logout'
    url_pin = f'{url}message/pin'
    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # user logout
    requests.post(url_logout, json={
        'token': user['token'],
    })

    # check if it will raise AccessError when token is invalid
    response = requests.post(url_pin, json={
        'token': user['token'],
        'message_id': message['message_id'],
    })
    assert response.status_code == AccessError.code

def test_message_unpin_regular1(url):
    '''
    Test if message_unpin can correct work
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_pin = f'{url}message/pin'
    url_unpin = f'{url}message/unpin'
    url_search = f'{url}search'
    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # pin message
    response = requests.post(url_pin, json={
        'token': user['token'],
        'message_id': message['message_id'],
    })

    # unpin message
    response = requests.post(url_unpin, json={
        'token': user['token'],
        'message_id': message['message_id'],
    })


    # check if the message is unpined by user and the key 'is_this_user_pined' is correct
    response = requests.get(url_search, params={
        'token': user['token'],
        'query_str': "Hello",
    })
    result = response.json()
    assert result['messages'][0]['is_pinned'] == False

def test_message_unpin_regular2(url):
    '''
    Test if message_unpin can correct work
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_join = f'{url}channel/join'
    url_send = f'{url}message/send'
    url_pin = f'{url}message/pin'
    url_unpin = f'{url}message/unpin'
    url_search = f'{url}search'
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
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # join a channel
    response = requests.post(url_join, json={
        'token': user2['token'],
        'channel_id': channel['channel_id'],
    })

    # send a message
    response = requests.post(url_send, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # pin message
    response = requests.post(url_pin, json={
        'token': user1['token'],
        'message_id': message['message_id'],
    })

    # unpin message
    response = requests.post(url_unpin, json={
        'token': user1['token'],
        'message_id': message['message_id'],
    })

    # check if the key 'is_pined' is correct
    response = requests.get(url_search, params={
        'token': user2['token'],
        'query_str': "Hello",
    })
    result = response.json()
    assert result['messages'][0]['is_pinned'] == False

# tests for InputError
def test_message_unpin_invalid_message_id(url):
    '''
    Test if an InputError is raised if message_id is not a valid message 
    within a channel that the authorised user has joined
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_pin = f'{url}message/pin'
    url_unpin = f'{url}message/unpin'
    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # pin a message properly
    response = requests.post(url_pin, json={
        'token': user['token'],
        'message_id': message['message_id'],
    })

    # check if an InputError is raised if message_id is invalid
    invalid_message_id = message['message_id'] + 100
    response = requests.post(url_unpin, json={
        'token': user['token'],
        'message_id': invalid_message_id,
    })
    assert response.status_code == InputError.code

def test_message_unpin_already_pinned(url):
    '''
    Test if an InputError is raised if Message with ID message_id already 
    unpinned
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_pin = f'{url}message/pin'
    url_unpin = f'{url}message/unpin'
    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # pin message
    response = requests.post(url_pin, json={
        'token': user['token'],
        'message_id': message['message_id'],
    })

    # unpin a messsage
    response = requests.post(url_unpin, json={
        'token': user['token'],
        'message_id': message['message_id'],
    })

    # check if an InputError is raised if the message is already pined by authorised user
    response = requests.post(url_unpin, json={
        'token': user['token'],
        'message_id': message['message_id'],
    })
    assert response.status_code == InputError.code

# tests for AccessError
def test_message_unpin_not_a_member(url):
    '''
    Test if an authorised user is not a member of the channel that 
    the message is within
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_pin = f'{url}message/pin'
    url_unpin = f'{url}message/unpin'
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
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # pin a message
    response = requests.post(url_pin, json={
        'token': user1['token'],
        'message_id': message['message_id'],
    })

    # check if an AccessError is raised if the authorised user is not a member of the channel that 
    # the message is within
    response = requests.post(url_unpin, json={
        'token': user2['token'],
        'message_id': message['message_id'],
    })
    assert response.status_code == AccessError.code

def test_message_unpin_authorised_user_not_an_owner(url):
    '''
    Test if an authorised user is not an owner
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_invite = f'{url}channel/invite'
    url_send = f'{url}message/send'
    url_pin = f'{url}message/pin'
    url_unpin = f'{url}message/unpin'
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
        'email': "t.swift@gmail.com",
        'password': "12345678",
        'name_first': "Taylor",
        'name_last': "Swift",
    })
    user2 = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # invite to a channel
    response = requests.post(url_invite, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })

    # send a message
    response = requests.post(url_send, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # pin a message
    response = requests.post(url_pin, json={
        'token': user1['token'],
        'message_id': message['message_id'],
    })

    # check if an AccessError is raised if the authorised user is not an owner
    response = requests.post(url_unpin, json={
        'token': user2['token'],
        'message_id': message['message_id'],
    })
    assert response.status_code == AccessError.code

# tests for invalid token
def test_message_unpin_invalid_token1(url):
    '''
    Test if an AccessError error is received when the token is invalid
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_pin = f'{url}message/pin'
    url_unpin = f'{url}message/unpin'
    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # pin a message
    response = requests.post(url_pin, json={
        'token': user['token'],
        'message_id': message['message_id'],
    })

    # check if it will raise AccessError when token is invalid
    response = requests.post(url_unpin, json={
        'token': "ThisIsAnInvalidToken",
        'message_id': message['message_id'],
    })
    assert response.status_code == AccessError.code

def test_message_unpin_invalid_token2(url):
    '''
    Test if an AccessError error is received when the token is invalid
    '''
    # set url
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_send = f'{url}message/send'
    url_logout = f'{url}auth/logout'
    url_pin = f'{url}message/pin'
    url_unpin = f'{url}message/unpin'
    # initiate data
    # register an user
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    # create a channel
    response = requests.post(url_create, json={
        'token': user['token'],
        'name': 'COMP1531',
        'is_public': True,
    })
    channel = response.json()

    # send a message
    response = requests.post(url_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': 'Hello',
    })
    message = response.json()

    # pin a message
    response = requests.post(url_pin, json={
        'token': user['token'],
        'message_id': message['message_id'],
    })

    # user logout
    requests.post(url_logout, json={
        'token': user['token'],
    })

    # check if it will raise AccessError when token is invalid
    response = requests.post(url_unpin, json={
        'token': user['token'],
        'message_id': message['message_id'],
    })
    assert response.status_code == AccessError.code