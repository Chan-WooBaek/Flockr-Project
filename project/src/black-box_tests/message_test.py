'''
    test these three functions: message_send, message_remove, message_edit
'''
import sys
sys.path.append('../')
from pytest import raises
from message import message_send, message_remove, message_edit, message_react, message_unreact, message_sendlater, message_pin, message_unpin
from channels import channels_create
from auth import auth_register, auth_logout
from error import InputError, AccessError
from other import clear, search
from channel import channel_join, channel_leave, channel_invite
from datetime import datetime, timezone
import time

def test_message_send_regular1():
    '''
    test if an member who is not an owner of flockr in channel can send message
    '''

    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
    channel = channels_create(user1['token'], 'COMP1531', True)
    channel_join(user2['token'], channel['channel_id'])

    # test message_send() can correctly run if authorised user who is
    # not owner of flockr in channel sent messsage.
    message_send(user2['token'], channel['channel_id'], "I love COMP1531!")
    result = search(user2['token'], "I love COMP1531!")
    assert result['messages'][0]['message'] == "I love COMP1531!"

def test_message_send_regular2():
    '''
    test if an owner of flockr who is not in channel can send message
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
    channel = channels_create(user1['token'], 'COMP1531', True)
    channel_join(user2['token'], channel['channel_id'])

    # test message_send() can correctly run if authorised user who is
    # an owner of flockr in channel sent messsage.
    message_send(user2['token'], channel['channel_id'], "I love COMP1531!")
    result = search(user2['token'], "I love COMP1531!")
    assert result['messages'][0]['message'] == "I love COMP1531!"

def test_message_send_message_too_long():
    '''
    Test if an InputError is received when the message entered 
    has more that 1000 characters
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)

    # Test message is more than 1000 characters. Check if it will raise an AccessError
    with raises(InputError):
        message_send(user['token'], channel['channel_id'], 'Hello World!' * 100)

def test_message_send_message_no_permission():
    '''
    Test if a AcessError is received when the authorised user is
    not an owner of flockr or in channel.
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
    channel = channels_create(user1['token'], 'COMP1531', False)

    # Check if it will raise an AccessError
    with raises(AccessError):
        message_send(user2['token'], channel['channel_id'], "I love COMP1531!")

def test_message_remove_regular1():
    '''
    test if an authorised user is an owner of flockr but not an owner
    of channel or a person who sent the message can remove message
    '''

    # clear data
    clear()

    # initiate data
    auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
    user3 = auth_register('t.swift@gmail.com', '12345678', 'Taylor', 'Swift')
    channel = channels_create(user2['token'], 'COMP1531', True)
    channel_join(user3['token'], channel['channel_id'])
    message = message_send(user3['token'], channel['channel_id'], "I love COMP1531!")
    
    # check if the person who sent the message can correctly remove
    message_remove(user2['token'], message['message_id'])
    result = search(user2['token'], "I love COMP1531!")
    assert result['messages'] == []

def test_message_remove_regular2():
    '''
    test if an authorised user is an owner of channel but not an owner
    of flockr or a person who sent the message can remove message
    '''

    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
    channel = channels_create(user2['token'], 'COMP1531', True)
    channel_join(user2['token'], channel['channel_id'])
    message = message_send(user1['token'], channel['channel_id'], "I love COMP1531!")
    
    # check if the person who is owner of channel can correctly remove
    message_remove(user2['token'], message['message_id'])
    result = search(user2['token'], "I love COMP1531!")
    assert result['messages'] == []

def test_message_remove_regular3():
    '''
    test if an authorised user is a member who sent the message in channel
    but not an owner of flockr or an owner of channel can remove message
    '''

    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
    channel = channels_create(user1['token'], 'COMP1531', True)
    channel_join(user2['token'], channel['channel_id'])
    message = message_send(user2['token'], channel['channel_id'], "I love COMP1531!")
    
    # check if the person who sent the message can correctly remove
    message_remove(user2['token'], message['message_id'])
    result = search(user2['token'], "I love COMP1531!")
    assert result['messages'] == []

def test_message_remove_messageid_not_exists():
    '''
    Test if a InputError is raised when the message no longer exists
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')

    # check if the person who sent the message can correctly remove
    with raises(InputError):
        message_remove(user['token'], 1)

def test_message_remove_message_was_removed():
    '''
    Test if an InputError is raisedwhen the message no longer exists
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)
    message = message_send(user['token'], channel['channel_id'], "I love COMP1531!")
    message_remove(user['token'], message['message_id'])    

    # check if it will raises InputError
    with raises(InputError):
        message_remove(user['token'], message['message_id'])

def test_message_remove_message_no_permission():
    '''
    Test if an AccessError is raised when the aurothised user has no permission
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
    channel = channels_create(user1['token'], 'COMP1531', True)
    channel_join(user2['token'], channel['channel_id'])

    message = message_send(user1['token'], channel['channel_id'], "I love COMP1531!")
    # check if it will raises InputError
    with raises(AccessError):
        message_remove(user2['token'], message['message_id'])

def test_message_edit_regular1():
    '''
    test if an authorised user is a member who sent the message in channel
    but not an owner of flockr or an owner of channel can edit message
    '''

    # clear data
    clear()

    # initiate data
    auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
    user3 = auth_register('t.swift@gmail.com', '12345678', 'Taylor', 'Swift')
    channel = channels_create(user2['token'], 'COMP1531', True)
    channel_join(user3['token'], channel['channel_id'])
    message = message_send(user3['token'], channel['channel_id'], "I love COMP1531!")
    
    # check if the person who sent the message can correctly remove
    message_edit(user3['token'], message['message_id'], "COMP1531 is cool!")
    result = search(user2['token'], "COMP1531 is cool!")
    assert result['messages'][0]['message'] == "COMP1531 is cool!"
   

def test_message_edit_regular2():
    '''
    test if an authorised user is an owner of channel but not an owner
    of flockr or a person who sent the message can edit message
    '''

    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
    channel = channels_create(user2['token'], 'COMP1531', True)
    channel_join(user2['token'], channel['channel_id'])
    message = message_send(user1['token'], channel['channel_id'], "I love COMP1531!")
    
    # check if the person who is owner of channel can correctly remove
    message_edit(user2['token'], message['message_id'], "COMP1531 is cool!")
    result = search(user2['token'], "COMP1531 is cool!")
    assert result['messages'][0]['message'] == "COMP1531 is cool!"
   

def test_message_edit_regular3():
    '''
    test if an authorised user is an owner of flockr but not an owner
    of channel or a person who sent the message can edit message
    '''

    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
    channel = channels_create(user2['token'], 'COMP1531', True)
    channel_join(user2['token'], channel['channel_id'])
    message = message_send(user2['token'], channel['channel_id'], "I love COMP1531!")
    
    # check if the person who is owner of flockr can correctly edit
    message_edit(user1['token'], message['message_id'], "COMP1531 is cool!")
    result = search(user2['token'], "COMP1531 is cool!")
    assert result['messages'][0]['message'] == "COMP1531 is cool!"

def test_message_edit_message_no_permission():
    '''
    Test if an AccessError is raised when the aurothised user has no permission
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
    channel = channels_create(user1['token'], 'COMP1531', True)
    channel_join(user2['token'], channel['channel_id'])

    message = message_send(user1['token'], channel['channel_id'], "I love COMP1531!")
    # check if the person who sent the message can correctly remove
    with raises(AccessError):
        message_edit(user2['token'], message['message_id'], "Hello!")

def test_message_send_invalid_token1():
    '''
    Test if an AccessError error is received when the token is invalid
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)

    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        message_send("ThisIsAnInvalidToken",  channel['channel_id'], 'Hello')

def test_message_send_invalid_token2():
    '''
    Test if an AccessError error is received when the token is invalid
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)
    auth_logout(user['token'])

    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        message_send(user['token'], channel['channel_id'], 'Hello')

def test_message_remove_invalid_token1():
    '''
    Test if an AccessError error is received when the token is invalid
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        message_remove("ThisIsAnInvalidToken", message['message_id'])

def test_message_remove_invalid_token2():
    '''
    Test if an AccessError error is received when the token is invalid
    '''	
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)
    message = message_send(user['token'], channel['channel_id'], 'Hello')
    auth_logout(user['token'])

    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        message_remove(user['token'], message['message_id'])

def test_message_edit_invalid_token1():
    '''
    Test if an AccessError error is received when the token is invalid
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        message_edit("ThisIsAnInvalidToken", message['message_id'], "GOOD")

def test_message_edit_invalid_token2():
    '''
    Test if an AccessError error is received when the token is invalid
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)
    message = message_send(user['token'], channel['channel_id'], 'Hello')
    auth_logout(user['token'])

    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        message_edit(user['token'], message['message_id'], "GOOD")

def test_message_react_regular1():
    '''
    Test if message_react can correct work
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    # react message
    message_react(user['token'], message['message_id'], 1)

    # check if the message is reacted by user and the key 'is_this_user_reacted' is correct
    result = search(user['token'], "Hello")
    assert result['messages'][0]['reacts'][0]['u_ids'] == [user['u_id']]
    assert result['messages'][0]['reacts'][0]['is_this_user_reacted'] == True


def test_message_react_regular2():
    '''
    Test if message_react can correct work
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('t.swift@gmail.com', '12345678', 'Taylor', 'Swift')
    channel = channels_create(user1['token'], 'COMP1531', True)
    channel_join(user2['token'], channel['channel_id'])
    message = message_send(user1['token'], channel['channel_id'], 'Hello')

    # react message
    message_react(user1['token'], message['message_id'], 1)

    # check if the key 'is_this_user_reacted' is correct
    result = search(user2['token'], "Hello")
    assert result['messages'][0]['reacts'][0]['is_this_user_reacted'] == False

def test_message_react_invalid_message_id():
    '''
    Test if an InputError is raised if message_id is not a valid message 
    within a channel that the authorised user has joined
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    # check if an InputError is raised if message_id is invalid
    invalid_message_id = message['message_id'] + 100
    with raises(InputError):
        message_react(user['token'], invalid_message_id, 1)

def test_message_react_invalid_not_in_channel():
    '''
    Test if an InputError is raised if message_id is not a valid message 
    within a channel that the authorised user has joined
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('s.abcd@gmail.com', '12345678', 'Taylor', 'Swift')
    channel = channels_create(user1['token'], 'COMP1531', True)
    message = message_send(user1['token'], channel['channel_id'], 'Hello')

    # check if an InputError is raised if token is invalid
    with raises(InputError):
        message_react(user2['token'], message['message_id'], 1)

def test_message_react_invalid_react_id():
    '''
    Test if an InputError is raised if react_id is not a valid React ID. 
    The only valid react ID the frontend has is 1
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    # check if an InputError is raised if react_id is invalid
    invalid_react_id = 2
    with raises(InputError):
        message_react(user['token'], message['message_id'], invalid_react_id)

def test_message_react_already_reacted():
    '''
    Test if an InputError is raised if Message with ID message_id already 
    contains an active React with ID react_id from the authorised user
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    # check if an InputError is raised if the message is already reacted by authorised user
    message_react(user['token'], message['message_id'], 1)
    with raises(InputError):
        message_react(user['token'], message['message_id'], 1)

def test_message_react_invalid_token1():
    '''
    Test if an AccessError error is received when the token is invalid
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        message_react("ThisIsAnInvalidToken", message['message_id'], 1)

def test_message_react_invalid_token2():
    '''
    Test if an AccessError error is received when the token is invalid
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)
    message = message_send(user['token'], channel['channel_id'], 'Hello')
    auth_logout(user['token'])

    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        message_react(user['token'], message['message_id'], 1)


def test_message_unreact_regular1():
    '''
    Test if message_react can correct work
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)
    message = message_send(user['token'], channel['channel_id'], 'Hello')
    message_react(user['token'], message['message_id'], 1)

    # unreact message
    message_unreact(user['token'], message['message_id'], 1)

    # check if the message is unreacted by user and the key 'is_this_user_reacted' is correct
    result = search(user['token'], "Hello")
    assert result['messages'][0]['reacts'][0]['u_ids'] == []
    assert result['messages'][0]['reacts'][0]['is_this_user_reacted'] == False

def test_message_unreact_regular2():
    '''
    Test if message_react can correct work
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('t.swift@gmail.com', '12345678', 'Taylor', 'Swift')
    channel = channels_create(user1['token'], 'COMP1531', True)
    channel_join(user2['token'], channel['channel_id'])
    message = message_send(user1['token'], channel['channel_id'], 'Hello')
    message_react(user1['token'], message['message_id'], 1)
    message_react(user2['token'], message['message_id'], 1)
    # unreact message
    message_unreact(user1['token'], message['message_id'], 1)

    # check if the key 'is_this_user_reacted' is correct
    result = search(user2['token'], "Hello")
    assert result['messages'][0]['reacts'][0]['is_this_user_reacted'] == True

def test_message_unreact_invalid_message_id():
    '''
    Test if an InputError is raised if message_id is not a valid message 
    within a channel that the authorised user has joined
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)
    message = message_send(user['token'], channel['channel_id'], 'Hello')
    message_react(user['token'], message['message_id'], 1)

    # check if an InputError is raised if message_id is invalid
    invalid_message_id = message['message_id'] + 100
    with raises(InputError):
        message_react(user['token'], invalid_message_id, 1)

def test_message_unreact_invalid_not_in_channel():
    '''
    Test if an InputError is raised if message_id is not a valid message 
    within a channel that the authorised user has joined
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('s.abcd@gmail.com', '12345678', 'Taylor', 'Swift')
    channel = channels_create(user1['token'], 'COMP1531', True)
    message = message_send(user1['token'], channel['channel_id'], 'Hello')
    channel_join(user2['token'], channel['channel_id'])
    message_react(user2['token'], message['message_id'], 1)
    channel_leave(user2['token'], channel['channel_id'])    

    # check if an InputError is raised if message_id is invalid
    with raises(InputError):
        message_unreact(user2['token'], message['message_id'], 1)

def test_message_unreact_invalid_react_id():
    '''
    Test if an InputError is raised if react_id is not a valid React ID. 
    The only valid react ID the frontend has is 1
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)
    message = message_send(user['token'], channel['channel_id'], 'Hello')
    message_react(user['token'], message['message_id'], 1) 

    # check if an InputError is raised if react_id is invalid
    invalid_react_id = 2
    with raises(InputError):
        message_unreact(user['token'], message['message_id'], invalid_react_id)

def test_message_unreact_not_reacted():
    '''
    Test if an InputError is raised if Message with ID message_id 
    does not contain an active React with ID react_id
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    # check if an InputError is raised if the message is already reacted by authorised user
    with raises(InputError):
        message_unreact(user['token'], message['message_id'], 1)

def test_message_unreact_invalid_token1():
    '''
    Test if an AccessError error is received when the token is invalid
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)
    message = message_send(user['token'], channel['channel_id'], 'Hello')
    message_react(user['token'], message['message_id'], 1) 

    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        message_unreact("ThisIsAnInvalidToken", message['message_id'], 1)

def test_message_unreact_invalid_token2():
    '''
    Test if an AccessError error is received when the token is invalid
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)
    message = message_send(user['token'], channel['channel_id'], 'Hello')
    message_react(user['token'], message['message_id'], 1) 
    auth_logout(user['token'])

    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        message_unreact(user['token'], message['message_id'], 1)

def test_message_sendlater_regular():
    '''
    test if an message_sendlater can corretly run
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)

    dt_now = datetime.utcnow()
    time_now = int(dt_now.replace(tzinfo=timezone.utc).timestamp())
    time_sent = time_now + 2

    # test message_sendlater() can correctly run
    message_sendlater(user['token'], channel['channel_id'], "I love COMP1531!", time_sent)
    result = search(user['token'], "I love COMP1531!")
    assert result['messages'] == []

    time.sleep(4)
    result = search(user['token'], "I love COMP1531!")
    assert result['messages'][0]['message'] == "I love COMP1531!"

def test_message_sendlater_invalid_channel_id():
    '''
    test if an InputError is raised if channel_id is not valid
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)

    dt_now = datetime.utcnow()
    time_now = int(dt_now.replace(tzinfo=timezone.utc).timestamp())
    time_sent = time_now + 2

    invalid_channel_id = channel['channel_id'] + 100
    # test if InputError is raised
    with raises(InputError):
        message_sendlater(user['token'], invalid_channel_id, "I love COMP1531!", time_sent)

def test_message_sendlater_message_too_long():
    '''
    test if an InputError is raised if message is too long
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)

    dt_now = datetime.utcnow()
    time_now = int(dt_now.replace(tzinfo=timezone.utc).timestamp())
    time_sent = time_now + 2

    # test if InputError is raised
    with raises(InputError):
        message_sendlater(user['token'], channel['channel_id'], "I love COMP1531!" * 300, time_sent)


def test_message_sendlater_time_sent_in_past():
    '''
    test if an InputError is raised if Time sent is a time in the past
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)

    dt_now = datetime.utcnow()
    time_now = int(dt_now.replace(tzinfo=timezone.utc).timestamp())
    time_past = time_now - 100

    # test if InputError is raised
    with raises(InputError):
        message_sendlater(user['token'], channel['channel_id'], "I love COMP1531!", time_past)

def test_message_sendlater_user_not_in_channel():
    '''
    test if an AccessError is raised if user is not in channel
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user1['token'], 'COMP1531', True)
    user2 = auth_register('a.asd@gmail.com', '12345678', 'Taylor', 'Swift')

    dt_now = datetime.utcnow()
    time_now = int(dt_now.replace(tzinfo=timezone.utc).timestamp())
    time_sent = time_now + 2

    # test if InputError is raised
    with raises(AccessError):
        message_sendlater(user2['token'], channel['channel_id'], "I love COMP1531!", time_sent)

def test_message_sendlater_invalid_token1():
    '''
    test if an InputError is raised if token passed in is invalid
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)

    dt_now = datetime.utcnow()
    time_now = int(dt_now.replace(tzinfo=timezone.utc).timestamp())
    time_sent = time_now + 2

    # test if InputError is raised
    with raises(AccessError):
        message_sendlater("ThisIsAnInvalidToken", channel['channel_id'], "I love COMP1531!", time_sent)

def test_message_sendlater_invalid_token2():
    '''
    test if an InputError is raised if token passed in is invalid
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)
    auth_logout(user['token'])

    dt_now = datetime.utcnow()
    time_now = int(dt_now.replace(tzinfo=timezone.utc).timestamp())
    time_sent = time_now + 2

    # test if InputError is raised
    with raises(AccessError):
        message_sendlater(user['token'], channel['channel_id'], "I love COMP1531!", time_sent)

def test_message_pin_regular1():
    '''
    Test if message_pin can correct work
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    # pin message
    message_pin(user['token'], message['message_id'])

    # check if the message is pined by user and the key 'is_this_user_pined' is correct
    result = search(user['token'], "Hello")
    assert result['messages'][0]['is_pinned'] == True

def test_message_pin_regular2():
    '''
    Test if message_pin can correct work
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('t.swift@gmail.com', '12345678', 'Taylor', 'Swift')
    channel = channels_create(user1['token'], 'COMP1531', True)
    channel_join(user2['token'], channel['channel_id'])
    message = message_send(user1['token'], channel['channel_id'], 'Hello')

    # pin message
    message_pin(user1['token'], message['message_id'])

    # check if the key 'is_this_user_pined' is correct
    result = search(user2['token'], "Hello")
    assert result['messages'][0]['is_pinned'] == True

# tests for InputError
def test_message_pin_invalid_message_id():
    '''
    Test if an InputError is raised if message_id is not a valid message 
    within a channel that the authorised user has joined
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    # check if an InputError is raised if message_id is invalid
    invalid_message_id = message['message_id'] + 100
    with raises(InputError):
        message_pin(user['token'], invalid_message_id)

def test_message_pin_already_pinned():
    '''
    Test if an InputError is raised if Message with ID message_id already 
    pinned
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    # check if an InputError is raised if the message is already pined by authorised user
    message_pin(user['token'], message['message_id'])
    with raises(InputError):
        message_pin(user['token'], message['message_id'])

# tests for AccessError
def test_message_pin_not_a_member():
    '''
    Test if an authorised user is not a member of the channel that 
    the message is within
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('t.swift@gmail.com', '12345678', 'Taylor', 'Swift')
    channel = channels_create(user1['token'], 'COMP1531', True)
    message = message_send(user1['token'], channel['channel_id'], 'Hello')

    # check if an AccessError is raised if the authorised user is not a member of the channel that 
    # the message is within
    with raises(AccessError):
        message_pin(user2['token'], message['message_id'])

def test_message_pin_authorised_user_not_an_owner():
    '''
    Test if an authorised user is not an owner
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('t.swift@gmail.com', '12345678', 'Taylor', 'Swift')
    channel = channels_create(user1['token'], 'COMP1531', True)
    channel_invite(user1['token'], channel['channel_id'], user2['u_id'])
    message = message_send(user1['token'], channel['channel_id'], 'Hello')

    # check if an AccessError is raised if the authorised user is not an owner
    with raises(AccessError):
        message_pin(user2['token'], message['message_id'])

# tests for invalid token
def test_message_pin_invalid_token1():
    '''
    Test if an AccessError error is received when the token is invalid
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        message_pin("ThisIsAnInvalidToken", message['message_id'])

def test_message_pin_invalid_token2():
    '''
    Test if an AccessError error is received when the token is invalid
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)
    message = message_send(user['token'], channel['channel_id'], 'Hello')
    auth_logout(user['token'])

    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        message_pin(user['token'], message['message_id'])

def test_message_unpin_regular1():
    '''
    Test if message_unpin can correct work
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    # pin message
    message_pin(user['token'], message['message_id'])

    #unpin message
    message_unpin(user['token'], message['message_id'])

    # check if the message is unpined by user and the key 'is_this_user_pined' is correct
    result = search(user['token'], "Hello")
    assert result['messages'][0]['is_pinned'] == False

def test_message_unpin_regular2():
    '''
    Test if message_unpin can correct work
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('t.swift@gmail.com', '12345678', 'Taylor', 'Swift')
    channel = channels_create(user1['token'], 'COMP1531', True)
    channel_join(user2['token'], channel['channel_id'])
    message = message_send(user1['token'], channel['channel_id'], 'Hello')

    # pin message
    message_pin(user1['token'], message['message_id'])

    #unpin message
    message_unpin(user1['token'], message['message_id'])

    # check if the key 'is_this_user_pined' is correct
    result = search(user2['token'], "Hello")
    assert result['messages'][0]['is_pinned'] == False

# tests for InputError
def test_message_unpin_invalid_message_id():
    '''
    Test if an InputError is raised if message_id is not a valid message 
    within a channel that the authorised user has joined
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    # pin message
    message_pin(user['token'], message['message_id'])

    # check if an InputError is raised if message_id is invalid
    invalid_message_id = message['message_id'] + 100
    with raises(InputError):
        message_unpin(user['token'], invalid_message_id)

def test_message_unpin_already_unpinned():
    '''
    Test if an InputError is raised if Message with ID message_id already 
    unpinned
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', True)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    # pin and unpin a message
    message_pin(user['token'], message['message_id'])
    message_unpin(user['token'], message['message_id'])

    # check if an InputError is raised if the message is already pined by authorised user
    with raises(InputError):
        message_unpin(user['token'], message['message_id'])

# tests for AccessError
def test_message_unpin_not_a_member():
    '''
    Test if an authorised user is not a member of the channel that 
    the message is within
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('t.swift@gmail.com', '12345678', 'Taylor', 'Swift')
    channel = channels_create(user1['token'], 'COMP1531', True)
    message = message_send(user1['token'], channel['channel_id'], 'Hello')

    # pin message
    message_pin(user1['token'], message['message_id'])  

    # check if an AccessError is raised if the authorised user is not a member of the channel that 
    # the message is within
    with raises(AccessError):
        message_unpin(user2['token'], message['message_id'])

def test_message_unpin_authorised_user_not_an_owner():
    '''
    Test if an authorised user is not an owner
    '''
    # clear data
    clear()

    # initiate data
    user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    user2 = auth_register('t.swift@gmail.com', '12345678', 'Taylor', 'Swift')
    channel = channels_create(user1['token'], 'COMP1531', True)
    channel_invite(user1['token'], channel['channel_id'], user2['u_id'])
    message = message_send(user1['token'], channel['channel_id'], 'Hello')

    # pin message
    message_pin(user1['token'], message['message_id']) 

    # check if an AccessError is raised if the authorised user is not an owner
    with raises(AccessError):
        message_unpin(user2['token'], message['message_id'])

# tests for invalid token
def test_message_unpin_invalid_token1():
    '''
    Test if an AccessError error is received when the token is invalid
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    # pin message
    message_pin(user['token'], message['message_id'])

    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        message_unpin("ThisIsAnInvalidToken", message['message_id'])

def test_message_unpin_invalid_token2():
    '''
    Test if an AccessError error is received when the token is invalid
    '''
    # clear data
    clear()

    # initiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)
    message = message_send(user['token'], channel['channel_id'], 'Hello')

    # pin a message
    message_pin(user['token'], message['message_id'])

    auth_logout(user['token'])

    # check if it will raise AccessError when token is invalid
    with raises(AccessError):
        message_unpin(user['token'], message['message_id'])
