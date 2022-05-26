'''
All test functions related to http for user.py
'''
from subprocess import Popen, PIPE
import signal
from time import sleep
import re
import requests
import pytest
import string
import random
from error import InputError, AccessError

# Use this fixture to get the URL of the server. It starts the server for you,
# so you don't need to.
@pytest.fixture
def url():
    """
    Get url from this function
    """
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

def test_http_user_profile(url):
    '''
    Tests that user/profile route returns existing user
    '''
    # Sending user details to the server
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })

    # Processing the response given into the correct order input format for user_profile
    result1 = response1.json()
    result1processed = {
        'token': result1['token'],
        'u_id': result1['u_id'],
    }

    # Sending the processed input into the user/profile route
    url_profile = f'{url}user/profile'
    response2 = requests.get(url_profile, params=result1processed)
    result2 = response2.json()

    # Asserting that the response given back is what we expected
    assert result2['user'] == {
        'u_id': result1['u_id'],
        'email': 'email01@gmail.com',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
        'handle_str': 'alexanderabdelrahman',
        'profile_img_url': '',
    }

def test_http_user_profile_invalid(url):
    '''
    Tests that user/profile route recognises invalid u_id input
    '''
    # Register user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })
    result1 = response1.json()

    # Sending the invalid u_id input into the user/profile route
    url_profile = f'{url}user/profile'
    response2 = requests.get(url_profile, params={
        'token': result1['token'],
        'u_id': result1['u_id'] + 1,
    })
    
    assert response2.status_code == InputError.code

def test_http_user_profile_invalid_token(url):
    '''
    Tests that user/profile route recognises an invalid token input and raises AccessError
    '''
    # Register user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })
    result1 = response1.json()

    # Sending the invalid token input into the user/profile route
    url_profile = f'{url}user/profile'
    response2 = requests.get(url_profile, params={
        'token': f"{result1['token']}invalidtoken",     # invalid format
        'u_id': result1['u_id'],
    })
    
    assert response2.status_code == AccessError.code

    # invalidate the active token
    url_logout = f'{url}auth/logout'
    requests.post(url_logout, json={
        'token': result1['token'],
    })
    url_profile = f'{url}user/profile'
    response3 = requests.get(url_profile, params={
        'token': result1['token'],      # invalidated token
        'u_id': result1['u_id'],
    })

    assert response3.status_code == AccessError.code

def test_http_user_profile_setname(url):
    '''
    Tests that user/profile/setname route changes the given token user's name as intended
    '''
    # Register user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })

    # Processing the response given into the correct order input format for user_profile
    result1 = response1.json()
    result1processed = {
        'token': result1['token'],
        'u_id': result1['u_id'],
    }
    
    # Sending user token, new name_first and new name_last to the server to set new name
    url_setname = f'{url}user/profile/setname'
    requests.put(url_setname, json={
        'token': result1['token'],
        'name_first': 'Alex',
        'name_last': 'Abdel',
    })

    # Getting new user profile from server
    url_profile = f'{url}user/profile'
    response2 = requests.get(url_profile, params=result1processed)
    result2 = response2.json()

    # Asserting that the response given back is what we expected
    assert result2['user'] == {
        'u_id': result1['u_id'],
        'email': 'email01@gmail.com',
        'name_first': 'Alex',
        'name_last': 'Abdel',
        'handle_str': 'alexanderabdelrahman',
        'profile_img_url': '',
    }

def test_http_user_profile_setname_invalid_first_short(url):
    '''
    Test if a InputError(400) is received when the name_first entered has less than 1 character
    '''
    # Register user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })

    # Processing the response into a python object
    result1 = response1.json()
    
    # Sending user token, new name_first and new name_last to the server to set new name
    url_setname = f'{url}user/profile/setname'
    response2 = requests.put(url_setname, json={
        'token': result1['token'],
        'name_first': '',
        'name_last': 'Abdel',
    })
    
    assert response2.status_code == InputError.code

def test_http_user_profile_setname_invalid_first_long(url):
    '''
    Test if a InputError(400) is received when the name_first entered has more that 50 characters
    '''
    # Register user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })

    # Processing the response into a python object
    result1 = response1.json()

    # Creating invalid long name string
    length = 51
    letters_and_digits = string.ascii_letters + string.digits
    long_name = ''.join((random.choice(letters_and_digits) for i in range(length)))
    
    # Sending user token, new name_first and new name_last to the server to set new name
    url_setname = f'{url}user/profile/setname'
    response2 = requests.put(url_setname, json={
        'token': result1['token'],
        'name_first': long_name,
        'name_last': 'Abdel',
    })
    
    assert response2.status_code == InputError.code

def test_http_user_profile_setname_invalid_last_short(url):
    '''
    Test if a InputError(400) is received when the name_first entered has less than 1 character
    '''
    # Register user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })

    # Processing the response into a python object
    result1 = response1.json()
    
    # Sending user token, new name_first and new name_last to the server to set new name
    url_setname = f'{url}user/profile/setname'
    response2 = requests.put(url_setname, json={
        'token': result1['token'],
        'name_first': 'Alex',
        'name_last': '',
    })
    
    assert response2.status_code == InputError.code

def test_http_user_profile_setname_invalid_last_long(url):
    '''
    Test if a InputError(400) is produced when the name_first entered has more that 50 characters
    '''
    # Register user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })

    # Processing the response into a python object
    result1 = response1.json()

    # Creating invalid long name string
    length = 51
    letters_and_digits = string.ascii_letters + string.digits
    long_name = ''.join((random.choice(letters_and_digits) for i in range(length)))
    
    # Sending user token, new name_first and new name_last to the server to set new name
    url_setname = f'{url}user/profile/setname'
    response2 = requests.put(url_setname, json={
        'token': result1['token'],
        'name_first': 'Alex',
        'name_last': long_name,
    })
    
    assert response2.status_code == InputError.code

def test_http_user_profile_setname_invalid_token(url):
    '''
    Tests that user/profile route recognises an invalid token input and raises AccessError
    '''
    # Register user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })
    result1 = response1.json()

    # Sending the invalid token input into the user/profile route
    url_setname = f'{url}user/profile/setname'
    response2 = requests.put(url_setname, json={
        'token': f"{result1['token']}invalidtoken",
        'name_first': 'newnamefirst',
        'name_last': 'newnamelast',
    })
    assert response2.status_code == AccessError.code

    # invalidate the active token
    url_logout = f'{url}auth/logout'
    requests.post(url_logout, json={
        'token': result1['token'],
    })
    url_setname = f'{url}user/profile/setname'
    response3 = requests.put(url_setname, json={
        'token': result1['token'],      # invalidated token
        'name_first': 'newnamefirst',
        'name_last': 'newnamelast',
    })

    assert response3.status_code == AccessError.code


def test_http_user_profile_setemail(url):
    '''
    Tests that user/profile/setemail route changes the given token user's email as intended
    '''
    # Register user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })

    # Processing the response given into the correct order input format for user_profile
    result1 = response1.json()
    result1processed = {
        'token': result1['token'],
        'u_id': result1['u_id'],
    }
    
    # Sending user token, new email to the server to set new email
    url_setemail = f'{url}user/profile/setemail'
    requests.put(url_setemail, json={
        'token': result1['token'],
        'email': 'email01@hotmail.com'
    })

    # Getting new user profile from server
    url_profile = f'{url}user/profile'
    response2 = requests.get(url_profile, params=result1processed)
    result2 = response2.json()

    # Asserting that the response given back is what we expected
    assert result2['user'] == {
        'u_id': result1['u_id'],
        'email': 'email01@hotmail.com',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
        'handle_str': 'alexanderabdelrahman',
        'profile_img_url': '',
    }

def test_http_user_profile_setemail_invalid(url):
    '''
    Tests if an InputError(400) is produced when user/profile/setemail route receives an invalid email
    '''
    # Register user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })

    # Processing the response given into a python object
    result1 = response1.json()
    
    # Sending user token, new invalid email to the server to set new email
    url_setemail = f'{url}user/profile/setemail'
    response2 = requests.put(url_setemail, json={
        'token': result1['token'],
        'email': 'email01@hotmail'
    })

    # Asserting that we recieve an error 400
    assert response2.status_code == InputError.code

def test_http_user_profile_setemail_invalid_token(url):
    '''
    Tests that user/profile/setemail route recognises an invalid token input and raises AccessError
    '''
    # Register user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })
    result1 = response1.json()

    # Sending the invalid token input into the user/profile route
    url_setemail = f'{url}user/profile/setemail'
    response2 = requests.put(url_setemail, json={
        'token': f"{result1['token']}invalidtoken",
        'email': 'newemail@hotmail.com'
    })
    
    assert response2.status_code == AccessError.code

    # invalidate the active token
    url_logout = f'{url}auth/logout'
    requests.post(url_logout, json={
        'token': result1['token'],
    })
    url_setemail = f'{url}user/profile/setemail'
    response3 = requests.put(url_setemail, json={
        'token': result1['token'],      # invalidated token
        'email': 'newemail@hotmail.com'
    })

    assert response3.status_code == AccessError.code

def test_http_user_profile_sethandle(url):
    '''
    Tests that user/profile/sethandle route changes the given token user's handle as intended
    '''
    # Register user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })

    # Processing the response given into the correct order input format for user_profile
    result1 = response1.json()
    result1processed = {
        'token': result1['token'],
        'u_id': result1['u_id'],
    }
    
    # Sending user token, new handle to the server to set new handle
    url_sethandle = f'{url}user/profile/sethandle'
    requests.put(url_sethandle, json={
        'token': result1['token'],
        'handle_str': 'newhandle'
    })

    # Getting new user profile from server
    url_profile = f'{url}user/profile'
    response2 = requests.get(url_profile, params=result1processed)
    result2 = response2.json()

    # Asserting that the response given back is what we expected
    assert result2['user'] == {
        'u_id': result1['u_id'],
        'email': 'email01@gmail.com',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
        'handle_str': 'newhandle',
        'profile_img_url': '',
    }

def test_http_user_profile_sethandle_invalid_short(url):
    '''
    Tests that an InputError(400) is produced when user/profile/sethandle route receives a handle_str too short
    '''
    # Register user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })

    # Processing the response given into a python object
    result1 = response1.json()
    
    # Sending user token, new invalid handle to the server to try to set new handle
    url_sethandle = f'{url}user/profile/sethandle'
    response2 = requests.put(url_sethandle, json={
        'token': result1['token'],
        'handle_str': 's'
    })

    # Asserting that we receive an error 400
    assert response2.status_code == InputError.code

def test_http_user_profile_sethandle_invalid_long(url):
    '''
    Tests that an InputError(400) is produced when user/profile/sethandle route receives a handle_str too long
    '''
    # Register user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })

    # Processing the response given into a python object
    result1 = response1.json()
    
    # Sending user token, new invalid handle to the server to try to set new handle
    url_sethandle = f'{url}user/profile/sethandle'
    response2 = requests.put(url_sethandle, json={
        'token': result1['token'],
        'handle_str': 'handleiswaytoolongtobevalid'
    })

    assert response2.status_code == InputError.code

def test_http_user_profile_sethandle_invalid_repeated(url):
    '''
    Tests that an InputError(400) is produced when user/profile/sethandle route receives a handle_str
    which exists already.
    '''
    # Register users
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@hotmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })

    response2 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Leon',
        'name_last': 'Lionheart',
    })

    # Processing the responses given into python objects
    result1 = response1.json()
    result2 = response2.json()

    result1processed = {
        'token': result1['token'],
        'u_id': result1['u_id'],
    }

    # Sending the processed input into the user/profile route
    url_profile = f'{url}user/profile'
    response3 = requests.get(url_profile, params=result1processed)
    result3 = response3.json()
    
    # Sending user token, new invalid handle to the server to try to set new handle
    url_sethandle = f'{url}user/profile/sethandle'
    response4 = requests.put(url_sethandle, json={
        'token': result2['token'],
        'handle_str': result3['user']['handle_str'],
    })

    assert response4.status_code == InputError.code

def test_http_user_profile_sethandle_invalid_token(url):
    '''
    Tests that user/profile/sethandle route recognises invalid token and raises
    an AccessError
    '''
    # Register user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })
    result1 = response1.json()

    # Sending the invalid token input into the user/profile route
    url_sethandle = f'{url}user/profile/sethandle'
    response2 = requests.put(url_sethandle, json={
        'token': f"{result1['token']}invalidtoken",
        'handle_str': 'newhandlestr'
    })
    
    assert response2.status_code == AccessError.code

    # invalidate the active token
    url_logout = f'{url}auth/logout'
    requests.post(url_logout, json={
        'token': result1['token'],
    })
    url_sethandle = f'{url}user/profile/sethandle'
    response3 = requests.put(url_sethandle, json={
        'token': result1['token'],      # invalidated token
        'handle_str': 'newhandlestr'
    })

    assert response3.status_code == AccessError.code


def test_uploadphoto_invalid_token(url):
    '''
    Test if user_profile_uploadphoto() raises AccessError 
    when an invalid token is passed in
    '''
    
    # create a new user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })
    user = response1.json()

    # a valid url of a jpg file
    img_url = "https://www.courant.com/resizer/D9qmAnzR8PY5q-GBdUBBVuNVUTs=/415x311/top/arc-anglerfish-arc2-prod-tronc.s3.amazonaws.com/public/NTWCZKYTDJBI7CASRJ32F2RN6E.jpg"
    
    url_uploadphoto = f'{url}user/profile/uploadphoto'

    # invalid format for token
    response = requests.post(url_uploadphoto, json = {
        'token': f"{user['token']}invalid",
        'img_url': img_url,
        'x_start': 20,
        'y_start': 20,
        'x_end': 30,
        'y_end': 30,
    })
    assert response.status_code == AccessError.code

    # invalidate the active token
    url_logout = f'{url}auth/logout'
    requests.post(url_logout, json={
        'token': user['token'],
    })

    # pass in the invalidated token
    response = requests.post(url_uploadphoto, json = {
        'token': user['token'],
        'img_url': img_url,
        'x_start': 20,
        'y_start': 20,
        'x_end': 30,
        'y_end': 30,
    })
    assert response.status_code == AccessError.code


def test_upload_invalid_dimensions(url):
    '''
    Test if an InputError is raised when an invalid dimension is passed in
    '''

    # create a new user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })
    user = response1.json()

    # a valid url of a jpg file
    img_url = "https://www.courant.com/resizer/D9qmAnzR8PY5q-GBdUBBVuNVUTs=/415x311/top/arc-anglerfish-arc2-prod-tronc.s3.amazonaws.com/public/NTWCZKYTDJBI7CASRJ32F2RN6E.jpg"
    
    # pass in different invalid dimensions

    url_uploadphoto = f'{url}user/profile/uploadphoto'

    # negative x_start
    response = requests.post(url_uploadphoto, json = {
        'token': user['token'],
        'img_url': img_url,
        'x_start': -10,
        'y_start': 10,
        'x_end': 20,
        'y_end': 20,
    })
    assert response.status_code == InputError.code

    # negative y_start
    response = requests.post(url_uploadphoto, json = {
        'token': user['token'],
        'img_url': img_url,
        'x_start': 10,
        'y_start': -10,
        'x_end': 20,
        'y_end': 20,
    })
    assert response.status_code == InputError.code
    
    # negative x_end
    response = requests.post(url_uploadphoto, json = {
        'token': user['token'],
        'img_url': img_url,
        'x_start': 10,
        'y_start': 10,
        'x_end': -20,
        'y_end': 20,
    })
    assert response.status_code == InputError.code
    
    # negative y_end
    response = requests.post(url_uploadphoto, json = {
        'token': user['token'],
        'img_url': img_url,
        'x_start': 10,
        'y_start': 10,
        'x_end': 20,
        'y_end': -20,
    })
    assert response.status_code == InputError.code
    
    # x_start too large
    response = requests.post(url_uploadphoto, json = {
        'token': user['token'],
        'img_url': img_url,
        'x_start': 5000,
        'y_start': 10,
        'x_end': 20,
        'y_end': 20,
    })
    assert response.status_code == InputError.code

    # y_start too large
    response = requests.post(url_uploadphoto, json = {
        'token': user['token'],
        'img_url': img_url,
        'x_start': 10,
        'y_start': 5000,
        'x_end': 20,
        'y_end': 20,
    })
    assert response.status_code == InputError.code

    # x_end too large
    response = requests.post(url_uploadphoto, json = {
        'token': user['token'],
        'img_url': img_url,
        'x_start': 10,
        'y_start': 10,
        'x_end': 5000,
        'y_end': 20,
    })
    assert response.status_code == InputError.code

    # y_end too large
    response = requests.post(url_uploadphoto, json = {
        'token': user['token'],
        'img_url': img_url,
        'x_start': 10,
        'y_start': 10,
        'x_end': 20,
        'y_end': 5000,
    })
    assert response.status_code == InputError.code

    # x_end < x_start
    response = requests.post(url_uploadphoto, json = {
        'token': user['token'],
        'img_url': img_url,
        'x_start': 10,
        'y_start': 10,
        'x_end': 5,
        'y_end': 200,
    })
    assert response.status_code == InputError.code
       
    # y_end < y_start
    response = requests.post(url_uploadphoto, json = {
        'token': user['token'],
        'img_url': img_url,
        'x_start': 10,
        'y_start': 50,
        'x_end': 20,
        'y_end': 20,
    })
    assert response.status_code == InputError.code


def test_uploadphoto_invalid_jpg(url):
    '''
    Test if an InputError is raised when the img_url of a non-jpg image is passed in
    '''
    # create a new user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })
    user = response1.json()
    
    # png image
    img_url = "https://img.lovepik.com/element/40082/9836.png_300.png"

    url_uploadphoto = f'{url}user/profile/uploadphoto'

    # uploading a non jpg image
    response = requests.post(url_uploadphoto, json = {
        'token': user['token'],
        'img_url': img_url,
        'x_start': 10,
        'y_start': 10,
        'x_end': 20,
        'y_end': 20,
    })
    assert response.status_code == InputError.code

def test_uploadphoto_invalid_url(url):
    '''
    Test if an InputError is raised when an invalid img_url is passed in
    '''
    
    # create a new user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })
    user = response1.json()
    
    # invalid url
    img_url = "ThisIsAnInvalidUrl"

    url_uploadphoto = f'{url}user/profile/uploadphoto'

    # trying to uplaod an image from an invalid url
    response = requests.post(url_uploadphoto, json = {
        'token': user['token'],
        'img_url': img_url,
        'x_start': 10,
        'y_start': 10,
        'x_end': 20,
        'y_end': 20,
    })
    assert response.status_code == InputError.code

def test_uploadphoto_regular(url):
    '''
    Test if the img_url of a user is modified when the function 
    user_profile_uploadphoto is called.
    '''
    # create a new user
    url_register = f'{url}auth/register'
    response1 = requests.post(url_register, json={
        'email': 'email01@gmail.com',
        'password': '123456',
        'name_first': 'Alexander',
        'name_last': 'Abdelrahman',
    })
    user = response1.json()
    
    # a valid url of a jpg file
    img_url = "https://www.courant.com/resizer/D9qmAnzR8PY5q-GBdUBBVuNVUTs=/415x311/top/arc-anglerfish-arc2-prod-tronc.s3.amazonaws.com/public/NTWCZKYTDJBI7CASRJ32F2RN6E.jpg"

    url_uploadphoto = f'{url}user/profile/uploadphoto'

    # pass in valid arguments
    requests.post(url_uploadphoto, json = {
        'token': user['token'],
        'img_url': img_url,
        'x_start': 10,
        'y_start': 10,
        'x_end': 20,
        'y_end': 20,
    })

    # upload the img_url
    url_profile = f'{url}user/profile'
    response2 = requests.get(url_profile, params={
        'token': user['token'],
        'u_id': user['u_id'],
    })
    result = response2.json()
    # check if the profile_img_url is modified
    assert result['user']['profile_img_url'] != ''