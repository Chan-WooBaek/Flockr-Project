import sys
sys.path.append('../')
from channels import channels_list, channels_listall, channels_create
from channel import channel_invite
from pytest import raises
from auth import auth_register, auth_logout
from error import InputError, AccessError
from other import clear 


def test_channels_list():
	clear()

	# initiate data
	user1 = auth_register('h.smith@gmail.com', '12345678', 'Hadise', 'Smith')
	user2 = auth_register('t.zhang@gmail.com', '87654321', 'Tom', 'Zhang')
	user3 = auth_register('l.zhao@hotmail.com', '12348765', 'Lee', 'Zhao')
	channel1 = channels_create(user1['token'], 'LOL', True)
	channel2 = channels_create(user1['token'], 'WOW', False)
	channel3 = channels_create(user2['token'], 'SC', True)

	exp_result1 = {
		'channels': [
			{'channel_id': channel1["channel_id"], 'name': 'LOL'},            
			{'channel_id': channel2["channel_id"], 'name': 'WOW'},    
		]
	}
	assert channels_list(user1['token']) == exp_result1

	exp_result2 = {
		'channels': [
			{'channel_id': channel3["channel_id"], 'name': 'SC'},            
		]
	}
	assert channels_list(user2['token']) == exp_result2

	exp_result3 = {
		'channels': [],
	}
	assert channels_list(user3['token']) == exp_result3

	channel_invite(user1['token'], channel2['channel_id'], user3['u_id'])
	exp_result4 = {
		'channels': [
			  {'channel_id': channel2["channel_id"], 'name': 'WOW'}, 
		]
	}
	assert channels_list(user3['token']) == exp_result4

def test_channels_listall():
	clear()

	# initiate data
	user1 = auth_register('h.smith@gmail.com', '12345678', 'Hadise', 'Smith')
	user2 = auth_register('t.zhang@gmail.com', '87654321', 'Tom', 'Zhang')
	user3 = auth_register('l.zhao@hotmail.com', '12348765', 'Lee', 'Zhao')
	channel1 = channels_create(user1['token'], 'LOL', True)
	channel2 = channels_create(user1['token'], 'WOW', False)
	channel3 = channels_create(user2['token'], 'SC', True)

	exp_result = {
		'channels': [
			{'channel_id': channel1["channel_id"], 'name': 'LOL'},            
			{'channel_id': channel2["channel_id"], 'name': 'WOW'},
			{'channel_id': channel3["channel_id"], 'name': 'SC'},    
		]
	}
	assert channels_listall(user1['token']) == exp_result
	assert channels_listall(user2['token']) == exp_result
	assert channels_listall(user3['token']) == exp_result


def test_channels_create():
	clear()
	# initiate data
	user = auth_register('h.smith@gmail.com', '12345678', 'Hadise', 'Smith')

	# name must be less or equal to 20 cahracters
	with raises(InputError):
		channels_create(user['token'], 'LOLOLOLOLOLOLOLOLOLOLOLOL', True)

	channel1 = channels_create(user['token'], 'WOW', False)
	channel2 = channels_create(user['token'], 'SC', True)
	assert channel1['channel_id'] != channel2['channel_id']

	exp_result1 = {
		'channels': [
			{'channel_id': channel1["channel_id"], 'name': 'WOW'},            
			{'channel_id': channel2["channel_id"], 'name': 'SC'},    
		]
	}
	assert channels_list(user['token']) == exp_result1

def test_channels_listall_invalid_token1():
	# clear data
	clear()

	# initiate data
	user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	channels_create(user['token'], 'COMP1531', False)

	# check if it will raise AccessError when token is invalid
	with raises(AccessError):
		channels_listall("ThisIsAnInvalidToken")

def test_channels_listall_invalid_token2():
	# clear data
	clear()

	# initiate data
	user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	channels_create(user['token'], 'COMP1531', False)
	auth_logout(user['token'])

	# check if it will raise AccessError when token is invalid
	with raises(AccessError):
		channels_listall(user['token'])

def test_channels_list_invalid_token1():
	# clear data
	clear()

	# initiate data
	user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	channels_create(user['token'], 'COMP1531', False)

	# check if it will raise AccessError when token is invalid
	with raises(AccessError):
		channels_list("ThisIsAnInvalidToken")

def test_channels_list_invalid_token2():
	# clear data
	clear()

	# initiate data
	user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	channels_create(user['token'], 'COMP1531', False)
	auth_logout(user['token'])

	# check if it will raise AccessError when token is invalid
	with raises(AccessError):
		channels_list(user['token'])

def test_channels_create_invalid_token1():
	# clear data
	clear()

	# initiate data
	auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')

	# check if it will raise AccessError when token is invalid
	with raises(AccessError):
		channels_create("ThisIsAnInvalidToken", 'COMP1531', False)

def test_channels_create_invalid_token2():
	# clear data
	clear()

	# initiate data
	user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
	auth_logout(user['token'])

	# check if it will raise AccessError when token is invalid
	with raises(AccessError):
		channels_create(user['token'], 'COMP1531', False)