'''
http test for the server for the auth functions
created by Xinran Zhu on 18/10/20
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

def test_auth_register(url):
    '''
    A http test to check if auth_register correctly creates a new account,
    stores the relative information and return a valid u_id and token.
    (assuming auth_logout is working properly)
    '''
    # Create three new users
    url_register = f'{url}auth/register'
    response = requests.post(url_register, json={
        'email': "email01@gmail.com",
        'password': "123456",
        'name_first': "Alexander",
        'name_last': "Abdelrahman",
    })
    result1 = response.json()

    response = requests.post(url_register, json={
        'email': "email02@gmail.com",
        'password': "456789",
        'name_first': "Hamilton",
        'name_last': "Abercrombie",
    })
    result2 = response.json()

    response = requests.post(url_register, json={
        'email': "email03@gmail.com",
        'password': "654321",
        'name_first': "Constantine",
        'name_last': "MacDonough",
    })
    result3 = response.json()

    # Testing whether u_id and token are different for each user

    assert result1['u_id'] != result2['u_id']
    assert result1['u_id'] != result3['u_id']
    assert result2['u_id'] != result3['u_id']
    assert(result1['token'] != result2['token'])
    assert(result1['token'] != result3['token'])
    assert(result2['token'] != result3['token'])

    # check if the tokens are valid
    # if valid: auth_logout should return {'is_success': True}
    url_logout = f'{url}auth/logout'
    response = requests.post(url_logout, json={
        'token': result1['token'],
    })
    assert response.json() == {'is_success': True}

    response = requests.post(url_logout, json={
        'token': result2['token'],
    })
    assert response.json() == {'is_success': True}

    response = requests.post(url_logout, json={
        'token': result3['token'],
    })
    assert response.json() == {'is_success': True}

def test_register_invalid_email_format(url):
    '''
    Test if the register raises an InputError when an email with an invalid format
    is passed in. In this http test a 400 error should be received
    '''
    # Create a new user with invalid email
    url_register = f'{url}auth/register'
    response = requests.post(url_register, json={
        'email': "invalid_email",
        'password': "100086",
        'name_first': "Constantine",
        'name_last': "MacDonough",
    })
    assert response.status_code == InputError.code

def test_register_invalid_email_repetition(url):
    '''
    Test if an InputError(400) is received when passing in an email address which is
    already being used by another user.
    '''
    url_register = f'{url}auth/register'

    # create two users with the same email address
    requests.post(url_register, json={
        'email': "repeat@gmail.com",
        'password': "1111111",
        'name_first': "Estevan",
        'name_last': "MacCormack",
    })

    response = requests.post(url_register, json={
        'email': "repeat@gmail.com",
        'password': "2222222",
        'name_first': "Jonathan",
        'name_last': "MacGillivray",
    })

    assert response.status_code == InputError.code

def test_register_invalid_password(url):
    '''
    Test if an InputError(400) is received when the password entered is less than 6 characters long
    '''
    url_register = f'{url}auth/register'
    # Create an user with a too short password
    response = requests.post(url_register, json={
        'email': "password@gmail.com",
        'password': "123",
        'name_first': "Napoleon",
        'name_last': "Machacek",
    })
    assert response.status_code == InputError.code

def test_register_invalid_name_first_short(url):
    '''
    Test if an InputError(400) is received when the name_first entered is empty
    '''
    # Create an user with an empty first name
    url_register = f'{url}auth/register'
    response = requests.post(url_register, json={
        'email': "name_first@gmail.com",
        'password': "1234567",
        'name_first': "",                   # First name entered is empty
        'name_last': "MacCartney",
    })
    assert response.status_code == InputError.code

def test_register_invalid_name_first_long(url):
    '''
    Test if an InputError(400) is received when the name_first entered has more that 50 characters
    '''
    # First name entered is too long
    length = 51
    letters_and_digits = string.ascii_letters + string.digits
    long_name = ''.join((random.choice(letters_and_digits) for i in range(length)))

    # Create an user with a too long first name
    url_register = f'{url}auth/register'
    response = requests.post(url_register, json={
        'email': "name_first@gmail.com",
        'password': "1234567",
        'name_first': long_name,    # name_first has 51 characters
        'name_last': "Wagenknecht",
    })
    assert response.status_code == InputError.code

def test_register_invalid_name_last_short(url):
    '''
    Test if an InputError(400) is received when the name_last entered is empty
    '''
    # Create an user with an empty last name
    url_register = f'{url}auth/register'
    response = requests.post(url_register, json={
        'email': "name_last@gmail.com",
        'password': "1234567",
        'name_first': "Madelina",
        'name_last': "",            # Last name entered is empty
    })
    assert response.status_code == InputError.code


def test_register_invalid_name_last_long(url):
    '''
    Test if an InputError(400) is received when the name_last entered has more that 50 characters
    '''
    # create a random string with length 51
    length = 51
    letters_and_digits = string.ascii_letters + string.digits
    long_name = ''.join((random.choice(letters_and_digits) for i in range(length)))

    # Create an user with a too long last name
    url_register = f'{url}auth/register'
    response = requests.post(url_register, json={
        'email': "name_first@gmail.com",
        'password': "1234567",
        'name_first': "Vivienne",
        'name_last': long_name,     # name_last has 51 characters
    })
    assert response.status_code == InputError.code

def test_login_valid_email(url): 
    '''
    Test if an InputError(400) is received when log in whith an invalid email
    '''
    # normal registration of a new account
    url_register = f'{url}auth/register'
    requests.post(url_register, json={
        'email': "email01@gmail.com",
        'password': "123456",
        'name_first': "Alexander",
        'name_last': "Abdelrahman",
    })
    # try to log in with an invalid email
    url_login = f'{url}auth/login'
    response = requests.post(url_login, json={
        'email': "name_last@gmail.com",
        'password': "1234567",
    })
    assert response.status_code == InputError.code

def test_login_belongs_to_user(url):
    '''
    Test if an InputError(400) is received when the email used to login
    does not belong to any user.
    '''
    # Register new users
    url_register = f'{url}auth/register'
    requests.post(url_register, json={
        'email': "email01@gmail.com",
        'password': "123456",
        'name_first': "Alexander",
        'name_last': "Abdelrahman",
    })
    requests.post(url_register, json={
        'email': "email02@gmail.com",
        'password': "456789",
        'name_first': "Hamilton",
        'name_last': "Abercrombie",
    })

    # Email does not belong to a user
    url_login = f'{url}auth/login'
    response = requests.post(url_login, json={
        'email': "nemail03@gmail.com",
        'password': "123456",
    })
    assert response.status_code == InputError.code

    response = requests.post(url_login, json={
        'email': "nemail04@gmail.com",
        'password': "456789",
    })
    assert response.status_code == InputError.code

def test_login_incorrect_password(url):
    '''
    Test if an InputError(400) is received when the email used to login is valid but the
    password does not match
    '''
    # Register new users
    url_register = f'{url}auth/register'
    requests.post(url_register, json={
        'email': "email01@gmail.com",
        'password': "123456",
        'name_first': "Alexander",
        'name_last': "Abdelrahman",
    })
    requests.post(url_register, json={
        'email': "email02@gmail.com",
        'password': "456789",
        'name_first': "Hamilton",
        'name_last': "Abercrombie",
    })

    # Password is not correct
    url_login = f'{url}auth/login'
    response = requests.post(url_login, json={
        'email': "nemail01@gmail.com",
        'password': "456789",
    })
    assert response.status_code == InputError.code

    response = requests.post(url_login, json={
        'email': "nemail02@gmail.com",
        'password': "123456",
    })
    assert response.status_code == InputError.code

def test_login_return_correct_id_and_token(url):
    '''
    Test if login return the correct id and token when valid email and matched token
    are passed in.
    '''
    # Register new users
    url_register = f'{url}auth/register'
    response = requests.post(url_register, json={
        'email': "email01@gmail.com",
        'password': "123456",
        'name_first': "Alexander",
        'name_last': "Abdelrahman",
    })
    user1 = response.json()
    response = requests.post(url_register, json={
        'email': "email02@gmail.com",
        'password': "456789",
        'name_first': "Hamilton",
        'name_last': "Abercrombie",
    })
    user2 = response.json()
    response = requests.post(url_register, json={
        'email': "email03@gmail.com",
        'password': "654321",
        'name_first': "Constantine",
        'name_last': "MacDonough",
    })
    user3 = response.json()

    # Logout is required before logging in since the users are automatically
    # logged in after the registration
    url_logout = f'{url}auth/logout'

    requests.post(url_logout, json={
        'token': user1['token'],
    })
    requests.post(url_logout, json={
        'token': user2['token'],
    })

    requests.post(url_logout, json={
        'token': user3['token'],
    })

    # Testing whether u_id and token are different for each user
    url_login = f'{url}auth/login'
    response = requests.post(url_login, json = {
        'email': "email01@gmail.com", 
        'password': "123456",
    })
    result01 = response.json()

    response = requests.post(url_login, json = {
        'email': "email02@gmail.com", 
        'password': "456789",
    })
    result02 = response.json()

    response = requests.post(url_login, json = {
        'email': "email03@gmail.com", 
        'password': "654321",
    })
    result03 = response.json()

    # checking if repetitive u_id or token are accidentally generated
    assert(result01['u_id'] != result02['u_id'])
    assert(result01['u_id'] != result03['u_id'])
    assert(result02['u_id'] != result03['u_id'])

    assert(result01['token'] != result02['token'])
    assert(result01['token'] != result03['token'])
    assert(result02['token'] != result03['token'])

    # check if the tokens are valid
    # if valid: auth_logout should return {'is_success': True}
    
    response = requests.post(url_logout, json={
        'token': result01['token'],
    })
    assert response.json() == {'is_success': True}

    response = requests.post(url_logout, json={
        'token': result02['token'],
    })
    assert response.json() == {'is_success': True}

    response = requests.post(url_logout, json={
        'token': result03['token'],
    })
    assert response.json() == {'is_success': True}

def test_logout_valid(url):
    '''
    Test if a user can be successfully logged out when a valid token is passed in.
    '''
    # Register several new users
    url_register = f'{url}auth/register'
    requests.post(url_register, json={
        'email': "email01@gmail.com",
        'password': "123456",
        'name_first': "Alexander",
        'name_last': "Abdelrahman",
    })
    response = requests.post(url_register, json={
        'email': "email02@gmail.com",
        'password': "456789",
        'name_first': "Hamilton",
        'name_last': "Abercrombie",
    })
    requests.post(url_register, json={
        'email': "email03@gmail.com",
        'password': "654321",
        'name_first': "Constantine",
        'name_last': "MacDonough",
    })
    user2 = response.json()

    # Check if the valid token yields a successful logout
    url_logout = f'{url}auth/logout'
    response = requests.post(url_logout, json={
        'token': user2['token'],
    })
    assert response.json() == {
        'is_success': True,
    }

def test_logout_invalid01(url):
    '''
    Test if a false is returned by logout when an invalid token is passed in.
    '''
    # create a new user
    url_register = f'{url}auth/register'
    requests.post(url_register, json={
        'email': "email01@gmail.com",
        'password': "123456",
        'name_first': "Alexander",
        'name_last': "Abdelrahman",
    })
     # Not allowed to logout an invalid token
    invalid_token = "ThisIsAnInvalidToken"
    url_logout = f'{url}auth/logout'
    response = requests.post(url_logout, json={
        'token': invalid_token,
    })
    assert response.status_code == AccessError.code

def test_logout_invalid02(url):
    '''
    Test if a false is returned by logout when an user is logged out twice.
    '''
    # create a new user
    url_register = f'{url}auth/register'
    r = requests.post(url_register, json={
        'email': "email01@gmail.com",
        'password': "123456",
        'name_first': "Alexander",
        'name_last': "Abdelrahman",
    })
    user = r.json()
    # Not allowed to logout an user if it has been logged out already.
    url_logout = f'{url}auth/logout'
    requests.post(url_logout, json={
        'token': user['token'],
    })
    response = requests.post(url_logout, json={
        'token': user['token'],
    })
    assert response.status_code == AccessError.code

def test_auth_passwordreset_request_invalid_email(url):
    '''
    Test if auth_passwordreset_request raises error when passed an invalid email
    '''
    # Register user
    url_register = f'{url}auth/register'
    requests.post(url_register, json={
        'email': "emailreceivebot@gmail.com",
        'password': "123456",
        'name_first': "Christopher",
        'name_last': "Columbus",
    })
    
    # Request for a reset code for the user of the invalid email
    url_request = f'{url}auth/passwordreset/request'
    response = requests.post(url_request, json={
        'email': 'invalidemail'
    })

    assert response.status_code == InputError.code

def test_auth_passwordreset_request_email_not_registered(url):
    '''
    Test if auth_passwordreset_request raises InputError when passed an email not registered
    '''
    # Register user
    url_register = f'{url}auth/register'
    requests.post(url_register, json={
        'email': "emailreceivebot@gmail.com",
        'password': "123456",
        'name_first': "Christopher",
        'name_last': "Columbus",
    })
    
    # Request for a reset code for the user of the email not registered
    url_request = f'{url}auth/passwordreset/request'
    response = requests.post(url_request, json={
        'email': 'resetcodegenerator@gmail.com'
    })

    assert response.status_code == InputError.code

def test_auth_passwordreset_request_email_not_string(url):
    '''
    Test if auth_passwordreset_request raises InputError when passed an email is not a string
    '''
    # Register user
    url_register = f'{url}auth/register'
    requests.post(url_register, json={
        'email': "emailreceivebot@gmail.com",
        'password': "123456",
        'name_first': "Christopher",
        'name_last': "Columbus",
    })
    
    # Request for a reset code for the user of the invalid email
    url_request = f'{url}auth/passwordreset/request'
    response = requests.post(url_request, json={
        'email': 1
    })

    assert response.status_code == InputError.code

def test_auth_passwordreset_reset_invalid_resetcode(url):
    '''
    Test if auth_passwordreset_reset raises an InputError when given an invalid resetcode
    '''
    # Register user
    url_register = f'{url}auth/register'
    requests.post(url_register, json={
        'email': "emailreceivebot@gmail.com",
        'password': "123456",
        'name_first': "Christopher",
        'name_last': "Columbus",
    })
    
    # Request for a reset code for the user of the email
    url_request = f'{url}auth/passwordreset/request'
    response = requests.post(url_request, json={
        'email': "emailreceivebot@gmail.com"
    })

    # Reset the password for the user with the invalid resetcode and valid newpassword
    url_reset = f'{url}auth/passwordreset/reset'
    response = requests.post(url_reset, json={
        'reset_code': 'invalidcode',
        'new_password': 'newpassword'
    })

    assert  response.status_code == InputError.code
