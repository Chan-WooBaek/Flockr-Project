'''
http test for the server for the other functions
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

def test_clear(url):
	'''
	test correct clear
	'''
	# set url
	url_register = f'{url}auth/register'
	url_create = f'{url}channels/create'
	url_send = f'{url}message/send'
	url_clear = f'{url}clear'

	# register a new user
	url_register = f'{url}auth/register'
	response = requests.post(url_register, json={
		'email': "t.holland@gmail.com",
		'password': "12345678",
		'name_first': "Tom",
		'name_last': "Holland",
	})
	user = response.json() 

	# register a new user
	response = requests.post(url_register, json={
		'email': "h.styles@gmail.com",
		'password': "12345678",
		'name_first': "Harry",
		'name_last': "Styles",
	})
	user1 = response.json()

	# register a new user'
	requests.post(url_register, json={
		'email': "n.beck@gmail.com",
		'password': "12345678",
		'name_first': "Noah",
		'name_last': "Beck",
	})

	# create a new channel
	response = requests.post(url_create, json={
		'token': user1['token'],
		'name': 'COMP1531',
		'is_public': False,
	})
	channel = response.json()

	# send a message
	response = requests.post(url_send, json={
		'token': user['token'],
		'channel_id': channel['channel_id'],
		'message': 'Hello World!',
	})

	# send a message
	response = requests.post(url_send, json={
		'token': user['token'],
		'channel_id': channel['channel_id'],
		'message': 'Hello World!',
	})
	
	# clear the data
	requests.delete(url_clear, json={})

	# register a new user, if the the clear function works correctly, 
	# the register functions will work properly, or the register function 
	# will raise an error
	response = requests.post(url_register, json={
		'email': "t.holland@gmail.com",
		'password': "12345678",
		'name_first': "Tom",
		'name_last': "Holland",
	})
	user = response.json()

def test_users_all(url):
	'''
	test correct user_all
	'''

	# set url
	url_register = f'{url}auth/register'
	url_users_all = f'{url}users/all'

	# register a new user
	response = requests.post(url_register, json={
		'email': "t.holland@gmail.com",
		'password': "12345678",
		'name_first': "Tom",
		'name_last': "Holland",
	})
	user = response.json()

	# excepted result
	exp_result = {
		'users': [{
			'email': 't.holland@gmail.com',
			'handle_str': 'tomholland',
			'name_first': 'Tom',
			'name_last': 'Holland',
			'u_id': 0,
			'profile_img_url': '',
		}]
	}

	# give a list of all the users
	response = requests.get(url_users_all, params={
		'token': user['token'],
	})
	result = response.json()
	assert result == exp_result

def test_admin_userpermission_change(url):
	'''
	test correct admin_userpermission_change
	'''

	# set url
	url_register = f'{url}auth/register'
	url_create = f'{url}channels/create'
	url_invite = f'{url}channel/invite'
	url_admin_userpermission_change = f'{url}admin/userpermission/change'
	# register a new user
	response = requests.post(url_register, json={
		'email': "t.holland@gmail.com",
		'password': "12345678",
		'name_first': "Tom",
		'name_last': "Holland",
	})
	user1 = response.json() 

	# register a new user
	response = requests.post(url_register, json={
		'email': "h.styles@gmail.com",
		'password': "12345678",
		'name_first': "Harry",
		'name_last': "Styles",
	})
	user2 = response.json() 

	# register a new user
	response = requests.post(url_register, json={
		'email': "n.beck@gmail.com",
		'password': "12345678",
		'name_first': "Noah",
		'name_last': "Beck",
	})
	user3 = response.json() 

	# create a new channel
	response = requests.post(url_create, json={
		'token': user1['token'],
		'name': 'COMP1531',
		'is_public': False,
	})
	channel = response.json()    

	# invite some one to the channel
	response = requests.post(url_invite, json={
		'token': user1['token'],
		'channel': channel['channel_id'],
		'u_id': user2['u_id'],
	})

	# set the value of permission_id
	Owner_permission = 1
	Invild_permission = 3
	invalid_u_id = 5

	# change someone's permission_id but failed for an invalid u_id
	response = requests.post(url_admin_userpermission_change, json={
		'token': user1['token'],
		'u_id': invalid_u_id,
		'permission_id': Owner_permission,
	})
	assert response.status_code == InputError.code 

	# change someone's permission_id but failed for an invalid permission_id
	response = requests.post(url_admin_userpermission_change, json={
		'token': user1['token'],
		'u_id': user2['u_id'],
		'permission_id': Invild_permission,
	})
	assert response.status_code == InputError.code 

	# change someone's permission_id but failed beacuse the implementer is 
	# not an Owner_permission user
	response = requests.post(url_admin_userpermission_change, json={
		'token': user3['token'],
		'u_id': user2['u_id'],
		'permission_id': Owner_permission,
	})
	assert response.status_code == AccessError.code 

def test_search(url):
	'''
	test correct search
	'''

	# set url
	url_register = f'{url}auth/register'
	url_create = f'{url}channels/create'
	url_send = f'{url}message/send'
	url_search = f'{url}search'

	# register a new user
	response = requests.post(url_register, json={
		'email': "t.holland@gmail.com",
		'password': "12345678",
		'name_first': "Tom",
		'name_last': "Holland",
	})
	user = response.json()

	# create a new channel
	response = requests.post(url_create, json={
		'token': user['token'],
		'name': 'COMP1531',
		'is_public': False,
	})
	channel = response.json()  

	# send a message
	response = requests.post(url_send, json={
		'token': user['token'],
		'channel_id': channel['channel_id'],
		'message': 'Hello World!',
	})

	# send a message   
	response = requests.post(url_send, json={
		'token': user['token'],
		'channel_id': channel['channel_id'],
		'message': '!dlroW olleH',
	})

	# expected result
	exp_result = 'Hello World!'

	# search for the given string
	response = requests.get(url_search, params={
		'token': user['token'],
		'query_str': 'Hello',
	})
	result = response.json()
	assert result['messages'][0]['message'] == exp_result

def test_users_all_invalid_token1(url):
	'''
	test if 400 error is recieved when token is invalid
	'''

	# set url
	url_register = f'{url}auth/register'
	url_users_all = f'{url}users/all'

	# register a new user
	requests.post(url_register, json={
		'email': "t.holland@gmail.com",
		'password': "12345678",
		'name_first': "Tom",
		'name_last': "Holland",
	})

	# check if it will raise AccessError when token is invalid
	response = requests.get(url_users_all, params={
		'token': 'ThisIsAnInvalidToken',
	})
	assert response.status_code == AccessError.code       

def test_users_all_invalid_token2(url):

	# set url
	url_register = f'{url}auth/register'
	url_users_all = f'{url}users/all'
	url_logout = f'{url}auth/logout'

	# register a new user
	response = requests.post(url_register, json={
		'email': "t.holland@gmail.com",
		'password': "12345678",
		'name_first': "Tom",
		'name_last': "Holland",
	})
	user = response.json()

	requests.post(url_logout, json={
		'token': user['token'],
	})

	# check if it will raise AccessError user is logged out
	url_users_all = f'{url}users/all'
	response = requests.get(url_users_all, params={
		'token': user['token'],
	})
	assert response.status_code == AccessError.code 

def test_admin_userpermission_change_invalid_token1(url):
	'''
	test if 400 error is recieved when token is invalid
	'''

	# set url
	url_register = f'{url}auth/register'
	url_admin_userpermission_change = f'{url}admin/userpermission/change'

	# register a new user
	requests.post(url_register, json={
		'email': "t.holland@gmail.com",
		'password': "12345678",
		'name_first': "Tom",
		'name_last': "Holland",
	})

	# register a new user
	response = requests.post(url_register, json={
		'email': "t.zhang@gmail.com",
		'password': "87654321",
		'name_first': "Tom",
		'name_last': "Zhang",
	})
	user = response.json()

	# check if it will raise AccessError when token is invalid
	response = requests.post(url_admin_userpermission_change, json={
		'token': 'ThisIsAnInvalidToken',
		'u_id': user['u_id'],
		'permission_id': 1,
	})
	assert response.status_code == AccessError.code 

def test_admin_userpermission_change_invalid_token2(url):
	'''
	test if 400 error is recieved when token is invalid
	'''

	# set url
	url_register = f'{url}auth/register'
	url_logout = f'{url}auth/logout'
	url_admin_userpermission_change = f'{url}admin/userpermission/change'

	# register a new user
	response = requests.post(url_register, json={
		'email': "t.holland@gmail.com",
		'password': "12345678",
		'name_first': "Tom",
		'name_last': "Holland",
	})
	user1 = response.json()

	# register a new user
	response = requests.post(url_register, json={
		'email': "t.zhang@gmail.com",
		'password': "87654321",
		'name_first': "Tom",
		'name_last': "Zhang",
	})
	user2 = response.json()

	# log out
	requests.post(url_logout, json={
		'token': user1['token'],
	})

# check if it will raise AccessError when token is invalid
	response = requests.post(url_admin_userpermission_change, json={
		'token': user1['token'],
		'u_id': user2['u_id'],
		'permission_id': 1,
	})
	assert response.status_code == AccessError.code 

def test_search_invalid_token1(url):
	'''
	test if 400 error is recieved when token is invalid
	'''

	# set url
	url_register = f'{url}auth/register'
	url_create = f'{url}channels/create'
	url_send = f'{url}message/send'
	url_search = f'{url}search'
	
	# register a new user
	response = requests.post(url_register, json={
		'email': "t.holland@gmail.com",
		'password': "12345678",
		'name_first': "Tom",
		'name_last': "Holland",
	})
	user = response.json()

	# create a new channel
	response = requests.post(url_create, json={
		'token': user['token'],
		'name': 'COMP1531',
		'is_public': False,
	})
	channel = response.json()

	# send a message
	response = requests.post(url_send, json={
		'token': user['token'],
		'channel_id': channel['channel_id'],
		'message': 'Hello',
	})

	# check if it will raise AccessError when token is invalid
	response = requests.get(url_search, params={
		'token': 'ThisIsAnInvalidToken',
		'query_str': 'Hello',
	})
	assert response.status_code == AccessError.code 

def test_search_invalid_token2(url):
	'''
	test if 400 error is recieved when token is invalid
	'''

	# set url
	url_register = f'{url}auth/register'
	url_create = f'{url}channels/create'
	url_send = f'{url}message/send'
	url_logout = f'{url}auth/logout'
	url_search = f'{url}search'
	
	# register a new user
	response = requests.post(url_register, json={
		'email': "t.holland@gmail.com",
		'password': "12345678",
		'name_first': "Tom",
		'name_last': "Holland",
	})
	user = response.json()

	# create a new channel
	response = requests.post(url_create, json={
		'token': user['token'],
		'name': 'COMP1531',
		'is_public': False,
	})
	channel = response.json()

	# send a message
	response = requests.post(url_send, json={
		'token': user['token'],
		'channel_id': channel['channel_id'],
		'message': 'Hello',
	})

	# log out
	requests.post(url_logout, json={
		'token': user['token'],
	})

	# check if it will raise AccessError when token is invalid
	response = requests.get(url_search, params={
		'token': user['token'],
		'query_str': 'Hello',
	})
	assert response.status_code == AccessError.code 