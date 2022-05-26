import sys
sys.path.append('../')
from auth import auth_register, auth_logout
from channel import channel_invite, channel_details, channel_messages, channel_leave, channel_join, channel_addowner, channel_removeowner
from channels import channels_create
from error import InputError, AccessError
from message import message_send
from pytest import raises
from other import clear


def test_channel_invite_regular():
	'''
	test if channel_invite can correctly invite user in channel
	'''

	# clear data
	clear()

	# initiate data
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland',)
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles',)
	channel = channels_create(user1['token'], 'COMP1531', False)

	# test correct channel_invite
	channel_invite(user1['token'], channel['channel_id'] , user2['u_id'])
	result = channel_details(user1['token'], channel['channel_id'])
	assert result == {
		'name': 'COMP1531', 
		'owner_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''}], 
		'all_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''},
						{'u_id': user2['u_id'], 'name_first': 'Harry', 'name_last': 'Styles', 'profile_img_url': ''}],
	}   


def test_channel_invite_invalid_channel_id():
	'''
	test if InputError is raised if channel_id is invalid
	'''

	# clear data
	clear()

	# initiate data
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland',)
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles',)
	channel = channels_create(user1['token'], 'COMP1531', False)
	channel_invite(user1['token'], channel['channel_id'] , user2['u_id'])

	# test InputError, channel_id does not refer to a valid channel
	invalid_channel_id = channel['channel_id'] + 100
	with raises(InputError):
		channel_invite(user1['token'], invalid_channel_id , user2['u_id'])


def test_channel_invite_invalid_u_id():
	'''
	test if InputError is raised if u_id is invalid
	'''

	# clear data
	clear()

	# initiate data
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland',)
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles',)
	channel = channels_create(user1['token'], 'COMP1531', False)

	# test correct channel_invite
	channel_invite(user1['token'], channel['channel_id'] , user2['u_id'])

	# test InputError, u_id does not refer to a valid user
	invalid_user_id = user1['u_id'] + user2['u_id'] + 100
	with raises(InputError):
		channel_invite(user1['token'], channel['channel_id'], invalid_user_id)
  

def test_channel_invite_not_in_channel():
	'''
	test if InputError is raised if the authorised user is not in channel
	'''

	# clear data
	clear()

	# initiate data
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland',)
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles',)
	channel = channels_create(user1['token'], 'COMP1531', False)

	# test correct channel_invite
	with raises(AccessError):
		channel_invite(user2['token'], channel['channel_id'] , user2['u_id'])  

def test_channel_details_regular():
	'''
	test if channel_details can correctly return details of the channel
	'''

	# clear data
	clear()

	# initiate data
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
	channel = channels_create(user1['token'], 'COMP1531', False)
	channel_invite(user1['token'], channel['channel_id'] , user2['u_id'])

	# test correct channel_details
	result = channel_details(user1['token'], channel['channel_id'])
	assert result == {
		'name': 'COMP1531', 
		'owner_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''}], 
		'all_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''},
						{'u_id': user2['u_id'], 'name_first': 'Harry', 'name_last': 'Styles', 'profile_img_url': ''}],
	}

def test_channel_details_invalid_channel_id():
	'''
	test if an InputError is raised if the channel id is invalid
	'''

	# clear data
	clear()

	# initiate data
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
	channel = channels_create(user1['token'], 'COMP1531', False)
	channel_invite(user1['token'], channel['channel_id'] , user2['u_id'])

	
	# test InputError, Channel ID is not a valid channel
	invalid_channel_id = channel['channel_id'] + 100
	with raises(InputError):
		channel_details(user1['token'], invalid_channel_id)


def test_channel_details_not_in_channel():
	'''
	test if an InputError is raised if the authorised user is not a member of channel with channel_id
	'''
	# clear data
	clear()

	# initiate data
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
	user3 = auth_register('n.beck@gmail.com', '12345678', 'Noah', 'Beck')
	channel = channels_create(user1['token'], 'COMP1531', False)
	channel_invite(user1['token'], channel['channel_id'] , user2['u_id'])

	# test AccessError, Authorised user is not a member of channel with channel_id
	with raises(AccessError):
		channel_details(user3['token'], channel['channel_id'])

def test_channel_message_regular():
	'''
	test if channel_message can work correctly
	'''

	# clear data
	clear()

	# initiate data
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
	channel1 = channels_create(user1['token'], 'COMP1531', False)
	channel_invite(user1['token'], channel1['channel_id'] , user2['u_id'])
	channel2 = channels_create(user2['token'], 'COMP6070', False)
	message_send(user2['token'], channel2['channel_id'], "Hello world!")

	# test correct channel message
	message = message_send(user1['token'], channel1['channel_id'], "Hello world!")
	result = channel_messages(user1['token'], channel1['channel_id'], 0)
	assert result['messages'][0]['message_id'] == message['message_id']
	assert result['messages'][0]['message'] == 'Hello world!'
	assert result['start'] == 0
	assert result['end'] == -1


def test_channel_message_invalid_channel_id():
	'''
	test if InputError if channel ID is not a valid channel
	'''

	# clear data
	clear()

	# initiate data
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
	channel1 = channels_create(user1['token'], 'COMP1531', False)
	channel_invite(user1['token'], channel1['channel_id'] , user2['u_id'])
	channel2 = channels_create(user2['token'], 'COMP6070', False)
	message_send(user2['token'], channel2['channel_id'], "Hello world!")

	invalid_channel_id = channel1['channel_id'] + 100
	
	# test InputError, Channel ID is not a valid channel
	with raises(InputError):
		channel_messages(user1['token'], invalid_channel_id, 0)

def test_channel_message_start_greatet_than_nummessages():
	'''
	test if an InputError is raised if start is greater than the total number of messages in the channel
	'''

	# clear data
	clear()

	# initiate data
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
	channel1 = channels_create(user1['token'], 'COMP1531', False)
	channel_invite(user1['token'], channel1['channel_id'] , user2['u_id'])
	channel2 = channels_create(user2['token'], 'COMP6070', False)
	message_send(user2['token'], channel2['channel_id'], "Hello world!")
	
	# test InputError, start is greater than the total number of messages in the channel
	invalid_start = 100
	with raises(InputError):
		channel_messages(user1['token'], channel1['channel_id'], invalid_start)   

def test_channel_message_not_in_channel():
	'''
	test if an AccessError if authorised user is not a member of channel with channel_id
	'''

	# clear data
	clear()

	# initiate data
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
	user3 = auth_register('n.beck@gmail.com', '12345678', 'Noah', 'Beck')
	channel1 = channels_create(user1['token'], 'COMP1531', False)
	channel_invite(user1['token'], channel1['channel_id'] , user2['u_id'])
	channel2 = channels_create(user2['token'], 'COMP6070', False)
	message_send(user2['token'], channel2['channel_id'], "Hello world!")
	
	# test AccessError, Authorised user is not a member of channel with channel_id
	with raises(AccessError):
		channel_messages(user3['token'], channel1['channel_id'] , 0)     

def test_channel_message_end_not_equal_to_minus1():
	''' 
	test if the key 'end' of the return value of channel_message is -1
	'''
	# clear data
	clear()
	
	# initiate data
	user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	channel = channels_create(user['token'], 'COMP6080', False)
	for i in range(0,100):
		message_send(user['token'], channel['channel_id'], "Hello world!" + str(i))
	
	result = channel_messages(user['token'], channel['channel_id'], 0)
	# check result
	assert len(result['messages']) == 50
	assert result['start'] == 0
	assert result['end'] == 50

def test_channel_leave():
	'''
	test if channel_leave can correctly work
	'''
	# clear data
	clear()

	# initiate a channel
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
	channel = channels_create(user1['token'], 'COMP1531', False)
	channel_invite(user1['token'], channel['channel_id'] , user2['u_id'])

	#test correct leave
	channel_leave(user2['token'],  channel['channel_id'])
	result = channel_details(user1['token'], channel['channel_id'])
	assert result == {
		'name': 'COMP1531', 
		'owner_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''}], 
		'all_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''}],
	}


def test_channel_leave_invalid_channel_id():
	'''
	test if an InputError is raised if channel id is invalid
	'''
	# clear data
	clear()

	# initiate a channel
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
	channel = channels_create(user1['token'], 'COMP1531', False)
	channel_invite(user1['token'], channel['channel_id'] , user2['u_id'])

	# test InputError, Channel ID is not a valid channel
	invalid_channel_id = channel['channel_id'] + 100
	with raises(InputError):
		channel_leave(user1['token'], invalid_channel_id)

def test_channel_leave_not_in_channel():
	'''
	test if an InputError is raised if authorised user is not a member of channel with channel_id
	'''
	# clear data
	clear()

	# initiate a channel
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
	user3 = auth_register('n.beck@gmail.com', '12345678', 'Noah', 'Beck')
	channel = channels_create(user1['token'], 'COMP1531', False)
	channel_invite(user1['token'], channel['channel_id'] , user2['u_id'])

	# test AccessError, Authorised user is not a member of channel with channel_id
	with raises(AccessError):
		channel_leave(user3['token'], channel['channel_id'])

def test_channel_join_correct():
	'''
	test if channel_join can work properly
	'''
	# clear data
	clear()

	# initiate a channel
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
	channel1 = channels_create(user1['token'], 'COMP1531', True)

	#test correct join
	channel_join(user2['token'], channel1['channel_id'])
	result = channel_details(user1['token'], channel1['channel_id'])
	assert result == {
		'name': 'COMP1531', 
		'owner_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''}], 
		'all_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''},
						{'u_id': user2['u_id'], 'name_first': 'Harry', 'name_last': 'Styles', 'profile_img_url': ''}],
	}

def test_channel_join_invalid_phannel_id():
	'''
	test if InputError is raised when Channel ID is not a valid channel
	'''
	# clear data
	clear()

	# initiate a channel
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	user3 = auth_register('n.beck@gmail.com', '12345678', 'Noah', 'Beck')
	channel1 = channels_create(user1['token'], 'COMP1531', True)
	channel2 = channels_create(user3['token'], 'COMP1531', False)

	# test InputError, Channel ID is not a valid channel
	invalid_channel_id = channel1['channel_id'] + channel2['channel_id'] + 100
	with raises(InputError):
		channel_join(user3['token'], invalid_channel_id)

def test_channel_join_private_channel():
	'''
	test if AccessError is raised when channel_id refers to a channel that is private
	'''
	# clear data
	clear()

	# initiate a channel
	user1 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
	user2 = auth_register('n.beck@gmail.com', '12345678', 'Noah', 'Beck')
	channel = channels_create(user1['token'], 'COMP1531', False)

	# test AccessError, channel_id refers to a channel that is private
	with raises(AccessError):
		channel_join(user2['token'], channel['channel_id'])

def test_channel_addowner_correct():
	'''
	test if channel_addowner can work properly
	'''
	# clear data
	clear()

	# initiate a channel
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
	channel = channels_create(user1['token'], 'COMP1531', False)

	#test correct addowner
	channel_addowner(user1['token'], channel['channel_id'], user2['u_id'])
	result = channel_details(user1['token'], channel['channel_id'])
	assert result == {
		'name': 'COMP1531', 
		'owner_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''},
						  {'u_id': user2['u_id'], 'name_first': 'Harry', 'name_last': 'Styles', 'profile_img_url': ''}], 
		'all_members': [{'u_id': user1['u_id'], 'name_first': 'Tom', 'name_last': 'Holland', 'profile_img_url': ''},
						{'u_id': user2['u_id'], 'name_first': 'Harry', 'name_last': 'Styles', 'profile_img_url': ''}],
	}


def test_channel_addowner_invalid_channels_id():
	'''
	test when InputErroris raised when Channel ID is not a valid channel
	'''
	# clear data
	clear()

	# initiate a channel
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	user3 = auth_register('n.beck@gmail.com', '12345678', 'Noah', 'Beck')
	channel = channels_create(user1['token'], 'COMP1531', False)

	invalid_channel_id = channel['channel_id'] + 100

	# test InputError, Channel ID is not a valid channel
	with raises(InputError):
		channel_addowner(user1['token'], invalid_channel_id, user3['u_id'])

def test_channel_addowner_already_in_channel():
	'''
	test if InputError is raised when user with user id u_id is already an owner of the channel
	'''
	# clear data
	clear()

	# initiate a channel
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
	channel = channels_create(user1['token'], 'COMP1531', False)
	channel_addowner(user1['token'], channel['channel_id'], user2['u_id'])

	# test InputError, user with user id u_id is already an owner of the channel
	with raises(InputError):    
		channel_addowner(user1['token'], channel['channel_id'], user2['u_id'])

def test_channel_addowner_not_an_owner():
	'''
	test if AccessError is raised when the authorised user is not an owner of the flockr, or an owner of this channel
	'''
	# clear data
	clear()

	# initiate a channel
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	user3 = auth_register('n.beck@gmail.com', '12345678', 'Noah', 'Beck')
	user4 = auth_register('x.ji@gmail.com', '12345678', 'Xiaohan', 'Ji')
	channel = channels_create(user1['token'], 'COMP1531', False)

	# test AccessError, the authorised user is not an owner of the flockr, or an owner of this channel
	with raises(AccessError):
		channel_addowner(user3['token'], channel['channel_id'], user4['u_id'])
	
def test_channel_removeowner_correct(): 
	'''
	test if channel_removeowner can work properly
	'''
	# clear data
	clear()

	# initiate a channel
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
	user3 = auth_register('n.beck@gmail.com', '12345678', 'Noah', 'Beck')
	channel = channels_create(user2['token'], 'COMP1531', False)
	channel_addowner(user2['token'], channel['channel_id'], user3['u_id'])

	#test correct removeowner
	channel_removeowner(user2['token'], channel['channel_id'], user3['u_id'])
	result = channel_details(user2['token'], channel['channel_id'])
	assert result == {
		'name': 'COMP1531', 
		'owner_members': [{'u_id': user2['u_id'], 'name_first': 'Harry', 'name_last': 'Styles', 'profile_img_url': ''}], 
		'all_members': [{'u_id': user2['u_id'], 'name_first': 'Harry', 'name_last': 'Styles', 'profile_img_url': ''},
						{'u_id': user3['u_id'], 'name_first': 'Noah', 'name_last': 'Beck', 'profile_img_url': ''},]
	}

def test_channel_removeowner_invalid_channel(): 
	'''
	test if InputError is raised when Channel ID is not a valid channel
	'''
	# clear data
	clear()

	# initiate a channel
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
	user3 = auth_register('n.beck@gmail.com', '12345678', 'Noah', 'Beck')
	channel = channels_create(user2['token'], 'COMP1531', False)
	channel_addowner(user2['token'], channel['channel_id'], user3['u_id'])

	# test InputError, Channel ID is not a valid channel
	invalid_channel_id = channel['channel_id'] + 100
	with raises(InputError):
		channel_removeowner(user2['token'], invalid_channel_id, user2['u_id'])

def test_channel_removeowner_user_with_u_id_not_owner(): 
	'''
	test if InputError is raised when user with user id u_id is not an owner of the channel
	'''
	# clear data
	clear()

	# initiate a channel
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
	user3 = auth_register('n.beck@gmail.com', '12345678', 'Noah', 'Beck')
	channel = channels_create(user2['token'], 'COMP1531', False)
	channel_addowner(user2['token'], channel['channel_id'], user3['u_id'])

	# test InputError, user with user id u_id is not an owner of the channel
	with raises(InputError):
		channel_removeowner(user2['token'], channel['channel_id'], user1['u_id'])
	
def test_channel_removeowner_authorised_user_not_owner(): 
	'''
	test if AccessError is raised when the authorised user is not an owner of 
	the flockr, or an owner of this channel
	'''
	# clear data
	clear()

	# initiate a channel
	user2 = auth_register('h.styles@gmail.com', '12345678', 'Harry', 'Styles')
	user3 = auth_register('n.beck@gmail.com', '12345678', 'Noah', 'Beck')
	user4 = auth_register('x.ji@gmail.com', '12345678', 'Xiaohan', 'Ji')
	channel = channels_create(user2['token'], 'COMP1531', False)
	channel_addowner(user2['token'], channel['channel_id'], user3['u_id'])

	# test AccessError, when the authorised user is not an owner of the flockr, or an owner of this channel
	with raises(AccessError):
		channel_removeowner(user4['token'], channel['channel_id'], user3['u_id'])


def test_channel_invite_invalid_token1():
	# clear data
	clear()

	# initiate data
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	channel = channels_create(user1['token'], 'COMP1531', False)
	user2 = auth_register('t.zhang@gmail.com', '87654321', 'Tom', 'Zhang')

	# check if will raise AccessError when token is invalid
	with raises(AccessError):
		channel_invite("ThisIsAnInvalidToken", channel['channel_id'], user2['u_id'])

def test_channel_invite_invalid_token2():
	# clear data
	clear()

	# initiate data
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	channel = channels_create(user1['token'], 'COMP1531', False)
	user2 = auth_register('t.zhang@gmail.com', '87654321', 'Tom', 'Zhang')
	auth_logout(user1['token'])

	# check if will raise AccessError when token is invalid
	with raises(AccessError):
		channel_invite(user1['token'], channel['channel_id'], user2['u_id'])

def test_channel_details_invalid_token1():
	# clear data
	clear()

	# initiate data
	user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	channel = channels_create(user['token'], 'COMP1531', False)

	# check if it will raise AccessError when token is invalid
	with raises(AccessError):
		channel_details("ThisIsAnInvalidToken", channel['channel_id'])

def test_channel_details_invalid_token2():
	# clear data
	clear()

	# initiate data
	user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	channel = channels_create(user['token'], 'COMP1531', False)
	auth_logout(user['token'])

	# check if it will raise AccessError when token is invalid
	with raises(AccessError):
		channel_details(user['token'], channel['channel_id'])

def test_channel_messages_invalid_token1():
	# clear data
	clear()

	# initiate data
	user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	channel = channels_create(user['token'], 'COMP1531', False)
	message_send(user['token'], channel['channel_id'], 'Hello')

	# check if it will raise AccessError when token is invalid
	with raises(AccessError):
		channel_messages("ThisIsAnInvalidToken", channel['channel_id'], 0)

def test_channel_messages_invalid_token2():
	# clear data
	clear()

	# initiate data
	user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	channel = channels_create(user['token'], 'COMP1531', False)
	message_send(user['token'], channel['channel_id'], 'Hello')
	auth_logout(user['token'])

	# check if it will raise AccessError when token is invalid
	with raises(AccessError):
		channel_messages(user['token'], channel['channel_id'], 0)

def test_channel_leave_invalid_token1():
	# clear data
	clear()

	# initiate data
	user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	channel = channels_create(user['token'], 'COMP1531', False)

	# check if it will raise AccessError when token is invalid
	with raises(AccessError):
		channel_leave("ThisIsAnInvalidToken", channel['channel_id'])

def test_channel_leave_invalid_token2():
	# clear data
	clear()

	# initiate data
	user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	channel = channels_create(user['token'], 'COMP1531', False)
	auth_logout(user['token'])

	# check if it will raise AccessError when token is invalid
	with raises(AccessError):
		channel_leave(user['token'], channel['channel_id'])

def test_channel_join_invalid_token1():
	# clear data
	clear()

	# initiate data
	user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	channel = channels_create(user['token'], 'COMP1531', False)
	auth_register('t.zhang@gmail.com', '87654321', 'Tom', 'Zhang')

	# check if it will raise AccessError when token is invalid
	with raises(AccessError):
		channel_join("ThisIsAnInvalidToken", channel['channel_id'])

def test_channel_join_invalid_token2():
	# clear data
	clear()

	# initiate data
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	channel = channels_create(user1['token'], 'COMP1531', False)
	user2 = auth_register('t.zhang@gmail.com', '87654321', 'Tom', 'Zhang')
	auth_logout(user2['token'])

	# check if it will raise AccessError when token is invalid
	with raises(AccessError):
		channel_join(user2['token'], channel['channel_id'])

def test_channel_addowner_invalid_token1():
	# clear data
	clear()

	# initiate data
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	channel = channels_create(user1['token'], 'COMP1531', False)
	user2 = auth_register('t.zhang@gmail.com', '87654321', 'Tom', 'Zhang')

	# check if it will raise AccessError when token is invalid
	with raises(AccessError):
		channel_addowner("ThisIsAnInvalidToken", channel['channel_id'], user2['u_id'])

def test_channel_addowner_invalid_token2():
	# clear data
	clear()

	# initiate data
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	channel = channels_create(user1['token'], 'COMP1531', False)
	user2 = auth_register('t.zhang@gmail.com', '87654321', 'Tom', 'Zhang')
	auth_logout(user1['token'])

	# check if it will raise AccessError when token is invalid
	with raises(AccessError):
		channel_addowner(user1['token'], channel['channel_id'], user2['u_id'])


def test_channel_removeowner_invalid_token1():
	# clear data
	clear()

	# initiate data
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	channel = channels_create(user1['token'], 'COMP1531', False)
	user2 = auth_register('t.zhang@gmail.com', '87654321', 'Tom', 'Zhang')
	channel_addowner(user1['token'], channel['channel_id'], user2['u_id'])

	# check if it will raise AccessError when token is invalid
	with raises(AccessError):
		channel_removeowner("ThisIsAnInvalidToken", channel['channel_id'], user2['u_id'])

def test_channel_removeowner_invalid_token2():
	# clear data
	clear()

	# initiate data
	user1 = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	channel = channels_create(user1['token'], 'COMP1531', False)
	user2 = auth_register('t.zhang@gmail.com', '87654321', 'Tom', 'Zhang')
	channel_addowner(user1['token'], channel['channel_id'], user2['u_id'])
	auth_logout(user1['token'])

	# check if it will raise AccessError when token is invalid
	with raises(AccessError):
		channel_removeowner(user1['token'], channel['channel_id'], user2['u_id'])	