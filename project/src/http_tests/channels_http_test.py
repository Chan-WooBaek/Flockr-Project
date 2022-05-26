'''
http test for the server for the channels functions
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


def test_channels_create_invalid(url):
	'''
	Test if AccessError.code error is recieved when, name is too long.
	'''
	# set url
	url_register = f'{url}auth/register'
	url_create = f'{url}channels/create'

	# register a new user
	response = requests.post(url_register, json={
		'email': "h.smith@gmail.com",
		'password': "12345678",
		'name_first': "Hadise",
		'name_last': "Smith",
	})

	user = response.json()

	# create a new channel
	response = requests.post(url_create, json={
		'token': user['token'],
		'name': 'LOLOLOLOLOLOLOLOLOLOLOLOL',
		'is_public': True,
	})
	assert response.status_code == InputError.code

def test_channels_create_normal(url):
	'''
	test correct channels_create
	'''
	# set url
	url_register = f'{url}auth/register'
	url_create = f'{url}channels/create'

	# register a new user
	response = requests.post(url_register, json={
		'email': "h.smith@gmail.com",
		'password': "12345678",
		'name_first': "Hadise",
		'name_last': "Smith",
	})
	user = response.json()
	
	# create a new channel
	requests.post(url_create, json={
		'token': user['token'],
		'name': 'WOW',
		'is_public': False,
	})

	# create a new channel
	requests.post(url_create, json={
		'token': user['token'],
		'name': 'SC',
		'is_public': True,
	})

def test_channels_listall_invalid_token1(url):
	'''
	test if AccessError error is received when token is invalid
	'''
	# set url
	url_register = f'{url}auth/register'
	url_create = f'{url}channels/create'
	url_listall = f'{url}channels/listall'

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

	response = requests.get(url_listall, params={
		'token': 'ThisIsAnInvalidToken',
	})
	assert response.status_code == AccessError.code 

def test_channels_listall_invalid_token2(url):
	'''
	test if AccessError error is received when token is invalid
	'''

	# set url
	url_register = f'{url}auth/register'
	url_create = f'{url}channels/create'
	url_logout = f'{url}auth/logout'
	url_listall = f'{url}channels/listall'

	# register a new user
	response = requests.post(url_register, json={
		'email': "t.holland@gmail.com",
		'password': "12345678",
		'name_first': "Tom",
		'name_last': "Holland",
	})
	user = response.json()

	# create a new channel
	requests.post(url_create, json={
		'token': user['token'],
		'name': 'COMP1531',
		'is_public': False,
	})

	requests.post(url_logout, json={
		'token': user['token'],
	})

	# check if it will raise AccessError user is logged out
	response = requests.get(url_listall, params={
		'token': user['token'],
	})
	assert response.status_code == AccessError.code 

def test_channels_list_invalid_token1(url):
	'''
	test if AccessError error is received when token is invalid
	'''

	# set url
	url_register = f'{url}auth/register'
	url_create = f'{url}channels/create'
	url__list = f'{url}channels/list'

	# register a new user
	response = requests.post(url_register, json={
		'email': "t.holland@gmail.com",
		'password': "12345678",
		'name_first': "Tom",
		'name_last': "Holland",
	})
	user = response.json()

	# create a new channel
	requests.post(url_create, json={
		'token': user['token'],
		'name': 'COMP1531',
		'is_public': False,
	})

	# check if it will raise AccessError when token is invalid
	response = requests.get(url__list, params={
		'token': 'ThisIsAnInvalidToken',
	})
	assert response.status_code == AccessError.code 

def test_channels_list_invalid_token2(url):
	'''
	test if AccessError error is received when token is invalid
	'''

	# set url
	url_register = f'{url}auth/register'
	url_create = f'{url}channels/create'
	url_logout = f'{url}auth/logout'
	url__list = f'{url}channels/list'

	# register a new user
	response = requests.post(url_register, json={
		'email': "t.holland@gmail.com",
		'password': "12345678",
		'name_first': "Tom",
		'name_last': "Holland",
	})
	user = response.json()

	# create a new channel
	requests.post(url_create, json={
		'token': user['token'],
		'name': 'COMP1531',
		'is_public': False,
	})

	requests.post(url_logout, json={
		'token': user['token'],
	})

	# check if it will raise AccessError when token is invalid
	response = requests.get(url__list, params={
		'token': user['token'],
	})
	assert response.status_code == AccessError.code 

def test_channels_create_invalid_token1(url):
	'''
	test if AccessError error is received when token is invalid
	'''

	# set url
	url_register = f'{url}auth/register'
	url_create = f'{url}channels/create'

	# register a new user
	requests.post(url_register, json={
		'email': "t.holland@gmail.com",
		'password': "12345678",
		'name_first': "Tom",
		'name_last': "Holland",
	})

	# check if it will raise AccessError when token is invalid
	response = requests.post(url_create, json={
		'token': 'ThisIsAnInvalidToken',
		'name': 'COMP1531',
		'is_public': False,
	})
	assert response.status_code == AccessError.code 	

def test_channels_create_invalid_token2(url):
	'''
	test if AccessError error is received when token is invalid
	'''
	
	# set url
	url_register = f'{url}auth/register'
	url_create = f'{url}channels/create'
	url_logout = f'{url}auth/logout'

	# register a new user
	response = requests.post(url_register, json={
		'email': "t.holland@gmail.com",
		'password': "12345678",
		'name_first': "Tom",
		'name_last': "Holland",
	})
	user = response.json()

	url_logout = f'{url}auth/logout'
	requests.post(url_logout, json={
		'token': user['token'],
	})

	# check if it will raise AccessError when token is invalid
	url_create = f'{url}channels/create'
	response = requests.post(url_create, json={
		'token': user['token'],
		'name': 'COMP1531',
		'is_public': False,
	})
	assert response.status_code == AccessError.code 	