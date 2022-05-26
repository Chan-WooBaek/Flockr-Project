'''
tests for all functions in other.py 
'''
import sys
sys.path.append('../')
from pytest import raises
from auth import auth_register, auth_logout
from data import data
from other import clear, users_all, admin_userpermission_change, search
from channels import channels_create
from channel import channel_invite
from message import message_send
from error import InputError, AccessError


def test_clear():
    '''
    test if clear() can correctly run 
    '''
    clear()
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
    auth_register('n.beck@gmail.com', '12345678', 'Noah', 'Beck')
    channel = channels_create(user['token'], 'COMP1531', False)
    message_send(user['token'], channel['channel_id'], 'Hello World!')
    message_send(user['token'], channel['channel_id'], 'Hello World!')
    # clear data
    clear()
    # to test if clear() clear the users in data successfully, if the user
    # are not correctly cleared, it will raise InputError because the email
    # has already been registed 
    assert data['valid_tokens'] == []
    auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
    

def test_users_all():
    '''
    test if the function users_all can return correct information
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland',)

    #test correct users all
    result = users_all(user['token'])
    assert result == {
        'users': [{
            'email': 't.holland@gmail.com',
            'handle_str': 'tomholland',
            'name_first': 'Tom',
            'name_last': 'Holland',
            'u_id': 0,
            'profile_img_url': '',
        }],
    }

def test_admin_userpermission_change():
    '''
    test if admin_userpermission_change() can correctly change user's permission
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland',)
    user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles',)
    user3 = auth_register('n.beck@gmail.com', '12345678', 'Noah', 'Beck',)
    channel = channels_create(user1['token'], 'COMP1531', False)
    channel_invite(user1['token'], channel['channel_id'], user2['u_id'])
    Owner_permission = 1
    Invild_permission = 3
    # test InputError, u_id does not refer to a valid user
    invalid_u_id = user1['u_id'] + user2['u_id'] + user3['u_id'] + 5

    admin_userpermission_change(user1['token'], user2['u_id'], 1)

    with raises(InputError):
        admin_userpermission_change(user1['token'], invalid_u_id, Owner_permission)
    # test InputError, permission_id does not refer to a value permission
    with raises(InputError):
        admin_userpermission_change(user1['token'], user2['u_id'], Invild_permission)
    
    # test AccessError, the authorised user is not an owner
    with raises(AccessError):
        admin_userpermission_change(user3['token'], user2['u_id'], Owner_permission)


def test_search():
    '''
    test if search() return correct string from all the messages
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('t.swift@gmail.com', '12345678', 'Taylor', 'Swift')
    channel1 = channels_create(user1['token'], 'COMP1531', False)
    channel2 = channels_create(user1['token'], 'COMP6080', False)
    channel3 = channels_create(user2['token'], 'COMP6771', False)
    message_send(user1['token'], channel1['channel_id'], 'Hello World!')
    message_send(user1['token'], channel2['channel_id'], '!dlroW olleH')
    message_send(user2['token'], channel3['channel_id'], 'Hello World!')

    # test correct search
    result = search(user1['token'], 'Hello')
    assert len(result['messages']) == 1
    assert result['messages'][0]['message_id'] == 0
    assert result['messages'][0]['u_id'] == 0
    assert result['messages'][0]['message'] == 'Hello World!'
    assert result['messages'][0]['time_created'] == data['messages'][0].get_time_created()



def test_users_all_invalid_token1():
    '''
    Test if a 400 error is received when the token is invalid
    '''
    # clear data
    clear()

    # initiate data
    auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')

    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        users_all("ThisIsAnInvalidToken")

def test_users_all_invalid_token2():
    '''
    Test if a 400 error is received when the token is invalid
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    auth_logout(user['token'])

    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        users_all(user['token'])

def test_admin_userpermission_change_invalid_token1():
    '''
    Test if a 400 error is received when the token is invalid
    '''
    # clear data
    clear()

    # initiate data
    auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user = auth_register('t.zhang@gmail.com', '87654321', 'Tom', 'Zhang')

    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        admin_userpermission_change("ThisIsAnInvalidToken", user['u_id'], 1)

def test_admin_userpermission_change_invalid_token2():
    '''
    Test if a 400 error is received when the token is invalid
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('t.zhang@gmail.com', '87654321', 'Tom', 'Zhang')
    auth_logout(user1['token'])
    
    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        admin_userpermission_change(user1['token'], user2['u_id'], 1)

def test_search_invalid_token1():
    '''
    Test if a 400 error is received when the token is invalid
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)
    message_send(user['token'], channel['channel_id'], 'Hello')

    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        search("ThisIsAnInvalidToken", "Hello")

def test_search_invalid_token2():
    '''
    Test if a 400 error is received when the token is invalid
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)
    message_send(user['token'], channel['channel_id'], 'Hello')
    auth_logout(user['token'])

    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        search(user['token'], "Hello")