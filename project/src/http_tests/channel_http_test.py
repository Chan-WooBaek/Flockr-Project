'''
http test for the server for the channel functions
'''
import random
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import string
import requests
import pytest
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

def test_channel_invite_regular(url):
    '''
        test correct channel_invite
    '''
    # initiate data
    url_invite = f'{url}channel/invite'
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    url_details = f'{url}channel/details'
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

    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    # test correct channel_invite
    response = requests.post(url_invite, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })

    response = requests.get(url_details, params={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
    })
    result = response.json()
    assert result == {
        'name': 'COMP1531', 
        'owner_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''}], 
        'all_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland','profile_img_url': ''},
                        {'u_id': user2['u_id'], 'name_first': 'Harry', 'name_last': 'Styles','profile_img_url': ''}],
    }

def test_channel_invite_invalid_channel(url):
    '''
        test InputError, channel_id does not refer to a valid channel
    '''
    # initiate data
    url_invite = f'{url}channel/invite'
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
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

    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    # test InputError, channel_id does not refer to a valid channel
    invalid_channel_id = channel['channel_id'] + 100

    response = requests.post(url_invite, json={
        'token': user1['token'],
        'channel_id': invalid_channel_id,
        'u_id': user2['u_id'],
    })
    assert response.status_code == InputError.code

def test_channel_invite_invalid_user(url):
    '''
        test InputError, u_id does not refer to a valid user
    '''
    # initiate data
    url_invite = f'{url}channel/invite'
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
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

    response = requests.post(url_register, json={
        'email': "n.beck@gmail.com",
        'password': "12345678",
        'name_first': "Noah",
        'name_last': "Beck",
    })
    user3 = response.json()

    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    # test InputError, u_id does not refer to a valid user
    invalid_user_id = user1['u_id'] + user2['u_id'] + user3['u_id'] + 100

    response = requests.post(url_invite, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': invalid_user_id,
    })

def test_channel_invite_not_a_member(url):
    '''
        test AccessError, the authorised user is not already a member of the channel
    '''
    # initiate data
    url_invite = f'{url}channel/invite'
    url_register = f'{url}auth/register'
    url_create = f'{url}channels/create'
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user1 = response.json()

    response = requests.post(url_register, json={
        'email': "n.beck@gmail.com",
        'password': "12345678",
        'name_first': "Noah",
        'name_last': "Beck",
    })
    user3 = response.json()

    response = requests.post(url_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    # test AccessError, the authorised user is not already a member of the channel
    response = requests.post(url_invite, json={
        'token': user3['token'],
        'channel_id': channel['channel_id'],
        'u_id': user3['u_id'],
    })
    assert response.status_code == AccessError.code

def test_channel_details_regular(url):
    '''
        test correct channel_details
    '''
    # initiate data
    url_channel_invite = f'{url}channel/invite'
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_details = f'{url}channel/details'
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

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    response = requests.post(url_channel_invite, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })

    # test correct channel_details
    response = requests.get(url_channel_details, params={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
    })
    result = response.json()
    assert result == {
        'name': 'COMP1531', 
        'owner_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''}], 
        'all_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''},
                        {'u_id': user2['u_id'], 'name_first': 'Harry', 'name_last': 'Styles', 'profile_img_url': ''}],
    }

def test_channel_details_invalid_channel(url):
    '''
        test InputError, Channel ID is not a valid channel
    '''
    # initiate data
    url_channel_invite = f'{url}channel/invite'
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_details = f'{url}channel/details'
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

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    response = requests.post(url_channel_invite, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })

    # test InputError, Channel ID is not a valid channel
    invalid_channel_id = channel['channel_id'] + 100
    response = requests.get(url_channel_details, params={
        'token': user1['token'],
        'channel_id': invalid_channel_id,
    })
    assert response.status_code == InputError.code

def test_channel_details_not_a_member(url):
    '''
        test AccessError, Authorised user is not a member of channel with channel_id
    '''
    # initiate data
    url_channel_invite = f'{url}channel/invite'
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_details = f'{url}channel/details'
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

    response = requests.post(url_register, json={
        'email': "n.beck@gmail.com",
        'password': "12345678",
        'name_first': "Noah",
        'name_last': "Beck",
    })
    user3 = response.json()

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    response = requests.post(url_channel_invite, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })

    # test AccessError, Authorised user is not a member of channel with channel_id
    response = requests.get(url_channel_details, params={
        'token': user3['token'],
        'channel_id': channel['channel_id'],
    })
    assert response.status_code == AccessError.code

def test_channel_leave_ragular(url):
    '''
        test correct leave
    '''
    # initiate a channel
    url_channel_invite = f'{url}channel/invite'
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_details = f'{url}channel/details'
    url_channel_leave = f'{url}channel/leave'
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

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    response = requests.post(url_channel_invite, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })

    # test correct leave
    requests.post(url_channel_leave, json={
        'token': user2['token'],
        'channel_id': channel['channel_id'],
    })

    response = requests.get(url_channel_details, params={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
    })
    result = response.json()
    assert result == {
        'name': 'COMP1531', 
        'owner_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''}], 
        'all_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''}],
    }

def test_channel_leave_invalid_channel(url):
    '''
        test InputError, Channel ID is not a valid channel
    '''
    # initiate a channel
    url_channel_invite = f'{url}channel/invite'
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_leave = f'{url}channel/leave'
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

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    response = requests.post(url_channel_invite, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })

    # test InputError, Channel ID is not a valid channel
    invalid_channel_id = channel['channel_id'] + 100
    response = requests.post(url_channel_leave, json={
        'token': user1['token'],
        'channel_id': invalid_channel_id,
    })
    assert response.status_code == InputError.code

def test_channel_leave_not_a_member(url):
    '''
        test AccessError, Authorised user is not a member of channel with channel_id
    '''
    # initiate a channel
    url_channel_invite = f'{url}channel/invite'
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_leave = f'{url}channel/leave'
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

    response = requests.post(url_register, json={
        'email': "n.beck@gmail.com",
        'password': "12345678",
        'name_first': "Noah",
        'name_last': "Beck",
    })
    user3 = response.json()

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    response = requests.post(url_channel_invite, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })
    # test AccessError, Authorised user is not a member of channel with channel_id
    response = requests.post(url_channel_leave, json={
        'token': user3['token'],
        'channel_id': channel['channel_id'],
    })
    assert response.status_code == AccessError.code

def test_messages_regular(url):
    '''
        test correct channel message
    '''
    # initiate a channel
    url_channel_invite = f'{url}channel/invite'
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_messages = f'{url}channel/messages'
    url_message_send = f'{url}message/send'
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

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel1 = response.json()

    response = requests.post(url_channel_invite, json={
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'u_id': user2['u_id'],
    })

    response = requests.post(url_channels_create, json={
        'token': user2['token'],
        'name': "COMP6070",
        'is_public': False,
    })
    channel2 = response.json()

    response = requests.post(url_message_send, json={
        'token': user2['token'],
        'channel_id': channel2['channel_id'], 
        'message': "Hello world!"
    })

    # test correct channel message
    response = requests.post(url_message_send, json={
        'token': user1['token'],
        'channel_id': channel1['channel_id'], 
        'message': "Hello world!"
    })
    message = response.json()

    response = requests.get(url_channel_messages, params={
        'token': user1['token'],
        'channel_id': channel1['channel_id'], 
        'start': 0
    })
    result = response.json()
    assert result['messages'][0]['message_id'] == message['message_id']
    assert result['messages'][0]['message'] == 'Hello world!'
    assert result['start'] == 0
    assert result['end'] == -1

def test_messages_invalid_channel(url):
    '''
        test InputError, Channel ID is not a valid channel
    '''
    # initiate a channel
    url_channel_invite = f'{url}channel/invite'
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_messages = f'{url}channel/messages'
    url_message_send = f'{url}message/send'
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

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel1 = response.json()

    response = requests.post(url_channel_invite, json={
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'u_id': user2['u_id'],
    })

    response = requests.post(url_channels_create, json={
        'token': user2['token'],
        'name': "COMP6070",
        'is_public': False,
    })
    channel2 = response.json()

    response = requests.post(url_message_send, json={
        'token': user2['token'],
        'channel_id': channel2['channel_id'], 
        'message': "Hello world!"
    })

    # test InputError, Channel ID is not a valid channel
    invalid_channel_id = channel1['channel_id'] + 100
    response = requests.get(url_channel_messages, params={
        'token': user1['token'],
        'channel_id': invalid_channel_id, 
        'start': 0
    })
    assert response.status_code == InputError.code

def test_messages_start_too_big(url):
    '''
        test InputError, start is greater than the total number of messages in the channel
    '''
    # initiate a channel
    url_channel_invite = f'{url}channel/invite'
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_messages = f'{url}channel/messages'
    url_message_send = f'{url}message/send'
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

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel1 = response.json()

    response = requests.post(url_channel_invite, json={
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'u_id': user2['u_id'],
    })

    response = requests.post(url_channels_create, json={
        'token': user2['token'],
        'name': "COMP6070",
        'is_public': False,
    })
    channel2 = response.json()

    response = requests.post(url_message_send, json={
        'token': user2['token'],
        'channel_id': channel2['channel_id'], 
        'message': "Hello world!"
    })
    # test InputError, start is greater than the total number of messages in the channel
    
    invalid_start = 100
    response = requests.get(url_channel_messages, params={
        'token': user1['token'],
        'channel_id': channel1['channel_id'], 
        'start': invalid_start
    })
    assert response.status_code == InputError.code

def test_messages_not_a_member(url):
    '''
        test AccessError, Authorised user is not a member of channel with channel_id
    '''
    # initiate a channel
    url_channel_invite = f'{url}channel/invite'
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_messages = f'{url}channel/messages'
    url_message_send = f'{url}message/send'
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

    response = requests.post(url_register, json={
        'email': "n.beck@gmail.com",
        'password': "12345678",
        'name_first': "Noah",
        'name_last': "Beck",
    })
    user3 = response.json()

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel1 = response.json()

    response = requests.post(url_channel_invite, json={
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
        'u_id': user2['u_id'],
    })

    response = requests.post(url_channels_create, json={
        'token': user2['token'],
        'name': "COMP6070",
        'is_public': False,
    })
    channel2 = response.json()

    response = requests.post(url_message_send, json={
        'token': user2['token'],
        'channel_id': channel2['channel_id'], 
        'message': "Hello world!"
    })
    # test InputError, start is greater than the total number of messages in the channel
    response = requests.get(url_channel_messages, params={
        'token': user3['token'],
        'channel_id': channel1['channel_id'], 
        'start': 0
    })
    assert response.status_code == InputError.code

def test_channel_message_end_not_equal_to_minus1(url):
    '''
        test channel message end not equal to minus
    '''
    # initiate data
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_messages = f'{url}channel/messages'
    url_message_send = f'{url}message/send'

    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    response = requests.post(url_channels_create, json={
        'token': user['token'],
        'name': "COMP6080",
        'is_public': False,
    })
    channel = response.json()

    for i in range(0,100):
        response = requests.post(url_message_send, json={
            'token': user['token'],
            'channel_id': channel['channel_id'], 
            'message': "Hello world!" + str(i)
        })

    response = requests.get(url_channel_messages, params={
        'token': user['token'],
        'channel_id': channel['channel_id'], 
        'start': 0
    })
    result = response.json()
    # check result
    assert len(result['messages']) == 50
    assert result['start'] == 0
    assert result['end'] == 50

def test_channel_join_regular(url):
    '''
        test correct join
    '''
    # initiate a channel
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_details = f'{url}channel/details'
    url_channel_join = f'{url}channel/join'
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

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': True,
    })
    channel1 = response.json()

    #test correct join
    response = requests.post(url_channel_join, json={
        'token': user2['token'],
        'channel_id': channel1['channel_id'],
    })
    print(response)
    print(response.ok)
    response = requests.get(url_channel_details, params={
        'token': user1['token'],
        'channel_id': channel1['channel_id'],
    })
    result = response.json()
    assert result == {
        'name': 'COMP1531', 
        'owner_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''}], 
        'all_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''},
                        {'u_id': user2['u_id'], 'name_first': 'Harry', 'name_last': 'Styles', 'profile_img_url': ''}],
    }

def test_channel_join_invalid_channel(url):
    '''
        test InputError, Channel ID is not a valid channel
    '''
    # initiate a channel
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_join = f'{url}channel/join'
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user1 = response.json()

    response = requests.post(url_register, json={
        'email': "n.beck@gmail.com",
        'password': "12345678",
        'name_first': "Noah",
        'name_last': "Beck",
    })
    user3 = response.json()

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': True,
    })
    channel1 = response.json()

    response = requests.post(url_channels_create, json={
        'token': user3['token'],
        'name': "COMP6080",
        'is_public': False,
    })
    channel2 = response.json()

    # test InputError, Channel ID is not a valid channel
    invalid_channel_id = channel1['channel_id'] + channel2['channel_id'] + 100
    response = requests.post(url_channel_join, json={
        'token': user3['token'],
        'channel_id': invalid_channel_id,
    })
    assert response.status_code == InputError.code

def test_channel_join_private(url):
    '''
        test AccessError, channel_id refers to a channel that is private
    '''
    # initiate a channel
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_join = f'{url}channel/join'
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

    response = requests.post(url_register, json={
        'email': "n.beck@gmail.com",
        'password': "12345678",
        'name_first': "Noah",
        'name_last': "Beck",
    })
    user3 = response.json()

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': True,
    })

    response = requests.post(url_channels_create, json={
        'token': user3['token'],
        'name': "COMP6080",
        'is_public': False,
    })
    channel2 = response.json()

    # test AccessError, channel_id refers to a channel that is private  
    response = requests.post(url_channel_join, json={
        'token': user2['token'],
        'channel_id': channel2['channel_id'],
    })
    assert response.status_code == AccessError.code

def test_channel_addowner_regular(url):
    '''
        test correct addowner
    '''
    # initiate a channel
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_details = f'{url}channel/details'
    url_channel_addowner = f'{url}channel/addowner'
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

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    #test correct addowner
    response = requests.post(url_channel_addowner, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })

    response = requests.get(url_channel_details, params={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
    })
    result = response.json()
    assert result == {
        'name': 'COMP1531', 
        'owner_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''},
                          {'u_id': user2['u_id'], 'name_first': 'Harry', 'name_last': 'Styles', 'profile_img_url': ''}], 
        'all_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''},
                        {'u_id': user2['u_id'], 'name_first': 'Harry', 'name_last': 'Styles', 'profile_img_url': ''}],
    }

def test_channel_addowner_invalid_channel(url):
    '''
        test InputError, Channel ID is not a valid channel
    '''
    # initiate a channel
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_addowner = f'{url}channel/addowner'
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user1 = response.json()

    response = requests.post(url_register, json={
        'email': "n.beck@gmail.com",
        'password': "12345678",
        'name_first': "Noah",
        'name_last': "Beck",
    })
    user3 = response.json()

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    # test InputError, Channel ID is not a valid channel
    invalid_channel_id = channel['channel_id'] + 100
    response = requests.post(url_channel_addowner, json={
        'token': user1['token'],
        'channel_id': invalid_channel_id,
        'u_id': user3['u_id'],
    })
    assert response.status_code == InputError.code

def test_channel_addowner_already_owner(url):
    '''
        test InputError, user with user id u_id is already an owner of the channel
    '''
    # initiate a channel
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_addowner = f'{url}channel/addowner'
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user1 = response.json()

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    # test InputError, user with user id u_id is already an owner of the channel
    response = requests.post(url_channel_addowner, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user1['u_id'],
    })
    assert response.status_code == InputError.code

def test_channel_addowner_not_owner_flock(url):
    '''
        test AccessError,  the authorised user is not an owner of the flockr, 
        or an owner of this channel
    '''
    # initiate a channel
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_addowner = f'{url}channel/addowner'
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user1 = response.json()

    response = requests.post(url_register, json={
        'email': "n.beck@gmail.com",
        'password': "12345678",
        'name_first': "Noah",
        'name_last': "Beck",
    })
    user3 = response.json()

    response = requests.post(url_register, json={
        'email': "x.ji@gmail.com",
        'password': "12345678",
        'name_first': "Xiaohan",
        'name_last': "Ji",
    })
    user4 = response.json()

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    # test AccessError,  the authorised user is not an owner of the flockr, or an owner of this channel
    response = requests.post(url_channel_addowner, json={
        'token': user3['token'],
        'channel_id': channel['channel_id'],
        'u_id': user4['u_id'],
    })
    assert response.status_code == AccessError.code

def test_channel_removeowner_regular(url): 
    '''
        test correct removeowner
    '''
    # initiate a channel
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_details = f'{url}channel/details'
    url_channel_addowner = f'{url}channel/addowner'
    url_channel_removeowner = f'{url}channel/removeowner'
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

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    response = requests.post(url_channel_addowner, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })
    #test correct removeowner
    response = requests.post(url_channel_removeowner, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })

    response = requests.get(url_channel_details, params={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
    })
    result = response.json()
    assert result == {
        'name': 'COMP1531', 
        'owner_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''}], 
        'all_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''},
                        {'u_id': user2['u_id'], 'name_first': 'Harry', 'name_last': 'Styles', 'profile_img_url': ''}],
    }

def test_channel_removeowner_invalid_channel(url): 
    '''
        test InputError, Channel ID is not a valid channel
    '''
    # initiate a channel
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_addowner = f'{url}channel/addowner'
    url_channel_removeowner = f'{url}channel/removeowner'
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

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    response = requests.post(url_channel_addowner, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })

    # test InputError, Channel ID is not a valid channel
    invalid_channel_id = channel['channel_id'] + 100
    response = requests.post(url_channel_removeowner, json={
        'token': user1['token'],
        'channel_id': invalid_channel_id,
        'u_id': user2['u_id'],
    })
    assert response.status_code == InputError.code

def test_channel_removeowner_not_a_owner(url): 
    '''
        test InputError, user with user id u_id is not an owner of the channel
    '''
    # initiate a channel
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_addowner = f'{url}channel/addowner'
    url_channel_removeowner = f'{url}channel/removeowner'
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

    response = requests.post(url_register, json={
        'email': "n.beck@gmail.com",
        'password': "12345678",
        'name_first': "Noah",
        'name_last': "Beck",
    })
    user3 = response.json()

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    response = requests.post(url_channel_addowner, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })

    # test InputError, user with user id u_id is not an owner of the channel
    response = requests.post(url_channel_removeowner, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user3['u_id'],
    })
    assert response.status_code == InputError.code

def test_channel_removeowner_not_a_owner2(url): 
    '''
        test AccessError, when the authorised user is not an owner of the flockr, 
        or an owner of this channel
    '''
    # initiate a channel
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_addowner = f'{url}channel/addowner'
    url_channel_removeowner = f'{url}channel/removeowner'
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

    response = requests.post(url_register, json={
        'email': "x.ji@gmail.com",
        'password': "12345678",
        'name_first': "Xiaohan",
        'name_last': "Ji",
    })
    user4 = response.json()

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    response = requests.post(url_channel_addowner, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })
   
    # test AccessError, when the authorised user is not an owner of the flockr, or an owner of this channel
    response = requests.post(url_channel_removeowner, json={
        'token': user4['token'],
        'channel_id': channel['channel_id'],
        'u_id': user1['u_id'],
    })
    assert response.status_code == AccessError.code

def test_channel_invite_invalid_token1(url):
    '''
        test channel_invite invalid token1
    '''
	# initiate data
    url_invite = f'{url}channel/invite'
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user1 = response.json()

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()
	
    response = requests.post(url_register, json={
        'email': "t.zhang@gmail.com",
        'password': "87654321",
        'name_first': "Tom",
        'name_last': "Zhang",
    })
    user2 = response.json()

	# check if will raise AccessError when token is invalid
    response = requests.post(url_invite, json={
        'token': "ThisIsAnInvalidToken",
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })
    assert response.status_code == AccessError.code

def test_channel_invite_invalid_token2(url):
    '''
        test channel_invite invalid token1
    '''
	# initiate data
    url_invite = f'{url}channel/invite'
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_auth_logout = f'{url}auth/logout'
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user1 = response.json()

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()
	
    response = requests.post(url_register, json={
        'email': "t.zhang@gmail.com",
        'password': "87654321",
        'name_first': "Tom",
        'name_last': "Zhang",
    })
    user2 = response.json()

    response = requests.post(url_auth_logout, json={
        'token': user1['token'],
    })

	# check if will raise AccessError when token is invalid
    response = requests.post(url_invite, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })
    assert response.status_code == AccessError.code

def test_channel_details_invalid_token1(url):
    '''
        check if it will raise AccessError when token is invalid
    '''
	# initiate data
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_details = f'{url}channel/details'
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    response = requests.post(url_channels_create, json={
        'token': user['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

	# check if it will raise AccessError when token is invalid
    response = requests.get(url_channel_details, params={
        'token': "ThisIsAnInvalidToken",
        'channel_id': channel['channel_id'],
    })
    assert response.status_code == AccessError.code

def test_channel_details_invalid_token2(url):
    '''
        check if it will raise AccessError when token is invalid
    '''
	# initiate data
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_auth_logout = f'{url}auth/logout'
    url_channel_details = f'{url}channel/details'
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    response = requests.post(url_channels_create, json={
        'token': user['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()
	
    response = requests.post(url_auth_logout, json={
        'token': user['token'],
    })

	# check if it will raise AccessError when token is invalid
    response = requests.get(url_channel_details, params={
        'token': user['token'],
        'channel_id': channel['channel_id'],
    })
    assert response.status_code == AccessError.code

def test_channel_messages_invalid_token1(url):
    '''
        check if it will raise AccessError when token is invalid
    '''
	# initiate data
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_message_send = f'{url}message/send'
    url_channel_messages = f'{url}channel/messages'

    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    response = requests.post(url_channels_create, json={
        'token': user['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()
	
    response = requests.post(url_message_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'], 
        'message': "Hello"
    })

	# check if it will raise AccessError when token is invalid
    response = requests.get(url_channel_messages, params={
        'token': "ThisIsAnInvalidToken",
        'channel_id': channel['channel_id'], 
        'start': 0
    })
    assert response.status_code == AccessError.code

def test_channel_messages_invalid_token2(url):
    '''
        check if it will raise AccessError when token is invalid
    '''
	# initiate data
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_message_send = f'{url}message/send'
    url_channel_messages = f'{url}channel/messages'
    url_auth_logout = f'{url}auth/logout'

    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    response = requests.post(url_channels_create, json={
        'token': user['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()
	
    response = requests.post(url_message_send, json={
        'token': user['token'],
        'channel_id': channel['channel_id'], 
        'message': "Hello"
    })
	
    response = requests.post(url_auth_logout, json={
        'token': user['token'],
    })

	# check if it will raise AccessError when token is invalid
    response = requests.get(url_channel_messages, params={
        'token': user['token'],
        'channel_id': channel['channel_id'], 
        'start': 0
    })
    assert response.status_code == AccessError.code

def test_channel_leave_invalid_token1(url):
    '''
        check if it will raise AccessError when token is invalid
    '''
	# initiate data
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_leave = f'{url}channel/leave'

    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    response = requests.post(url_channels_create, json={
        'token': user['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()
	
	# check if it will raise AccessError when token is invalid
    response = requests.post(url_channel_leave, json={
        'token': "ThisIsAnInvalidToken",
        'channel_id': channel['channel_id'],
    })
    assert response.status_code == AccessError.code

def test_channel_leave_invalid_token2(url):
    '''
        check if it will raise AccessError when token is invalid
    '''
	# initiate data
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_leave = f'{url}channel/leave'
    url_auth_logout = f'{url}auth/logout'

    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    response = requests.post(url_channels_create, json={
        'token': user['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    response = requests.post(url_auth_logout, json={
        'token': user['token'],
    })

	# check if it will raise AccessError when token is invalid
    response = requests.post(url_channel_leave, json={
        'token': user['token'],
        'channel_id': channel['channel_id'],
    })
    assert response.status_code == AccessError.code

def test_channel_join_invalid_token1(url):
    '''
        check if it will raise AccessError when token is invalid
    '''
	# initiate data
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_join = f'{url}channel/join'

    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user = response.json()

    response = requests.post(url_channels_create, json={
        'token': user['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()
	
	# check if it will raise AccessError when token is invalid
    response = requests.post(url_channel_join, json={
        'token': "ThisIsAnInvalidToken",
        'channel_id': channel['channel_id'],
    })
    assert response.status_code == AccessError.code

def test_channel_join_invalid_token2(url):
    '''
        check if it will raise AccessError when token is invalid
    '''
	# initiate data
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_join = f'{url}channel/join'
    url_auth_logout = f'{url}auth/logout'

    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user1 = response.json()

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    response = requests.post(url_register, json={
        'email': "t.zhang@gmail.com",
        'password': "87654321",
        'name_first': "Tom",
        'name_last': "Zhang",
    })
    user2 = response.json()

    response = requests.post(url_auth_logout, json={
        'token': user2['token'],
    })

	# check if it will raise AccessError when token is invalid
    response = requests.post(url_channel_join, json={
        'token': user2['token'],
        'channel_id': channel['channel_id'],
    })
    assert response.status_code == AccessError.code

def test_channel_addowner_invalid_token1(url):
    '''
        check if it will raise AccessError when token is invalid
    '''
	# initiate data
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_addowner = f'{url}channel/addowner'

    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user1 = response.json()

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    response = requests.post(url_register, json={
        'email': "t.zhang@gmail.com",
        'password': "87654321",
        'name_first': "Tom",
        'name_last': "Zhang",
    })
    user2 = response.json()
	
	# check if it will raise AccessError when token is invalid
    response = requests.post(url_channel_addowner, json={
        'token': "ThisIsAnInvalidToken",
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })
    assert response.status_code == AccessError.code

def test_channel_addowner_invalid_token2(url):
    '''
        check if it will raise AccessError when token is invalid
    '''
	# initiate data
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_addowner = f'{url}channel/addowner'
    url_auth_logout = f'{url}auth/logout'

    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user1 = response.json()

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    response = requests.post(url_register, json={
        'email': "t.zhang@gmail.com",
        'password': "87654321",
        'name_first': "Tom",
        'name_last': "Zhang",
    })
    user2 = response.json()

    response = requests.post(url_auth_logout, json={
        'token': user1['token'],
    })

	# check if it will raise AccessError when token is invalid
    response = requests.post(url_channel_addowner, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })
    assert response.status_code == AccessError.code


def test_channel_removeowner_invalid_token1(url):
    '''
        check if it will raise AccessError when token is invalid
    '''
	# initiate data
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_addowner = f'{url}channel/addowner'
    url_channel_removeowner = f'{url}channel/removeowner'
    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user1 = response.json()

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    response = requests.post(url_register, json={
        'email': "t.zhang@gmail.com",
        'password': "87654321",
        'name_first': "Tom",
        'name_last': "Zhang",
    })
    user2 = response.json()
	
    response = requests.post(url_channel_addowner, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })

	# check if it will raise AccessError when token is invalid
    response = requests.post(url_channel_removeowner, json={
        'token': "ThisIsAnInvalidToken",
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })
    assert response.status_code == AccessError.code

def test_channel_removeowner_invalid_token2(url):
    '''
        check if it will raise AccessError when token is invalid
    '''
	# initiate data
    url_register = f'{url}auth/register'
    url_channels_create = f'{url}channels/create'
    url_channel_addowner = f'{url}channel/addowner'
    url_channel_removeowner = f'{url}channel/removeowner'
    url_auth_logout = f'{url}auth/logout'

    response = requests.post(url_register, json={
        'email': "t.holland@gmail.com",
        'password': "12345678",
        'name_first': "Tom",
        'name_last': "Holland",
    })
    user1 = response.json()

    response = requests.post(url_channels_create, json={
        'token': user1['token'],
        'name': "COMP1531",
        'is_public': False,
    })
    channel = response.json()

    response = requests.post(url_register, json={
        'email': "t.zhang@gmail.com",
        'password': "87654321",
        'name_first': "Tom",
        'name_last': "Zhang",
    })
    user2 = response.json()

    response = requests.post(url_auth_logout, json={
        'token': user1['token'],
    })

    response = requests.post(url_channel_addowner, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })

	# check if it will raise AccessError when token is invalid
    response = requests.post(url_channel_removeowner, json={
        'token': user1['token'],
        'channel_id': channel['channel_id'],
        'u_id': user2['u_id'],
    })
    assert response.status_code == AccessError.code
