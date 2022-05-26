'''
Backend test functions for auth.py
Last modified on 19/10/20 by Xinran Zhu
'''
import sys
sys.path.append('../')
from auth import auth_login, auth_logout, auth_register
from pytest import raises
from error import InputError, AccessError
import random
import string
from other import clear


def test_register_regular01():
    '''
    A test to check if auth_register correctly creates a new account, stores the relative information and
    return a valid u_id and token.
    (assuming auth_logout is working properly)
    '''
    clear()
    # create three new users
    result1 = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    result2 = auth_register("email02@gmail.com", "456789", "Hamilton", "Abercrombie")
    result3 = auth_register("email03@gmail.com", "654321", "Constantine", "MacDonough")

    # Testing whether u_id and token are different for each user

    assert(result1['u_id'] != result2['u_id'])
    assert(result1['u_id'] != result3['u_id'])
    assert(result2['u_id'] != result3['u_id'])

    # check if the tokens are valid
    # if valid: auth_logout should return {'is_success': True}
    assert auth_logout(result1['token']) == {
        'is_success': True,
    }
    assert auth_logout(result2['token']) == {
        'is_success': True,
    }
    assert auth_logout(result3['token']) == {
        'is_success': True,
    }

def test_register_invalid_email_format():
    '''
    Test if the register raises an InputError when an email with an invalid format 
    is passed in.
    '''
    clear()
    # register a new user with an invalid email format
    with raises(InputError):
        auth_register("invalid_email", "100086", "Constantine", "MacDonough")

def test_register_invalid_email_repetition():
    '''
    Test if an InputError is raised when passing in an email address which is 
    already being used by another user.
    '''
    clear()
    # register two users with the same email
    auth_register("repeat@gmail.com", "1111111", "Estevan", "MacCormack")
    with raises(InputError):
        auth_register("repeat@gmail.com", "2222222", "Jonathan", "MacGillivray")

def test_register_invalid_password():
    '''
    Test if an InputError is raised when the password entered is less than 6 characters long
    '''
    clear()
    # Create an user with a too short password
    with raises(InputError):
        auth_register("password@gmail.com", "123", "Napoleon", "Machacek")

def test_register_invalid_name_first_short():
    '''
    Test if an InputError is raised when the name_first entered is empty
    '''
    clear()
    # Create an user with an empty first name
    with raises(InputError):
        auth_register("name_first@gmail.com", "1234567", "", "MacCartney")

def test_register_invalid_name_first_long():
    '''
    Test if an InputError is raised when the name_first entered is too long
    '''
    clear()
    # First name entered is too long
    length = 51
    letters_and_digits = string.ascii_letters + string.digits
    long_name = ''.join((random.choice(letters_and_digits) for i in range(length)))

    # Create an user with a too long first name
    with raises(InputError):
        auth_register("name_first@gmail.com", "1234567", long_name, "Wagenknecht")

def test_register_invalid_name_last_short():
    '''
    Test if an InputError is raised when the name_last entered is empty
    '''
    clear()
    # Last name entered is empty
    with raises(InputError):
        auth_register("name_last@gmail.com", "1234567", "Madelina", "")

def test_register_invalid_name_last_long():
    '''
    Test if an InputError is raised when the name_last entered has more than 50 characters
    '''
    clear()
    # Last name entered is too long
    length = 51
    letters_and_digits = string.ascii_letters + string.digits
    long_name = ''.join((random.choice(letters_and_digits) for i in range(length)))
    with raises(InputError):
        auth_register("name_last@gmail.com", "1234567", "Vivienne", long_name)

def test_logout_valid():
    '''
    Test if a user can be successfully logged out when a valid token is passed in.
    '''
    clear()
    # Register several new users
    auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    user2 = auth_register("email02@gmail.com", "456789", "Hamilton", "Abercrombie")

    # Check if the valid token yields a successful logout
    auth_register("email03@gmail.com", "123456", "Alexander", "Abdelrahman")
    assert auth_logout(user2['token']) == {
        'is_success': True,
    }

def test_logout_invalid01():
    '''
    Test if a false is returned by logout when an invalid token is passed in.
    '''
    clear()
    # Not allowed to logout an invalid token
    auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    invalid_token = "ThisIsAnInvalidToken"
    with raises(AccessError):
        auth_logout(invalid_token)

def test_logout_invalid02():
    '''
    Test if a false is returned by logout when an user is logged out twice.
    '''
    clear()
    # Not allowed to logout an user if it has been logged out already.
    user = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    auth_logout(user['token'])
    with raises(AccessError):
        auth_logout(user['token'])

def test_login_valid_email():
    '''
    Test if an InputError is raised when log in whith an invalid email
    '''
    clear()
    # Invalid email format
    auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    with raises(InputError):
        auth_login("invalid_email", "100086")

def test_login_belongs_to_user():
    '''
    Test if an InputError is raised when the email used to login
    does not belong to any user.
    '''
    clear()
    # Register new users
    auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    auth_register("email02@gmail.com", "456789", "Hamilton", "Abercrombie")

    # Email does not belong to a user
    with raises(InputError):
        auth_login("email03@gmail.com", "123456")
    with raises(InputError):
        auth_login("email04@gmail.com", "456789")


def test_login_incorrect_password():
    '''
    Test if an InputError is raised when the email used to login is valid but the
    password does not match.
    '''
    clear()
    # Register new users
    auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    auth_register("email02@gmail.com", "456789", "Hamilton", "Abercrombie")

    # Password is not correct
    with raises(InputError):
        auth_login("email01@gmail.com", "456789")
    with raises(InputError):
        auth_login("email02@gmail.com", "123456")

def test_login_return_correct_id_and_token():
    '''
    Test if login correctly return a valid u_id and token of the user
    '''
    clear()
    # Register new users
    user1 = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    user2 = auth_register("email02@gmail.com", "456789", "Hamilton", "Abercrombie")
    user3 = auth_register("email03@gmail.com", "654321", "Constantine", "MacDonough")

    # Logout is required before logging in since the users are automatically
    # logged in after the registration
    auth_logout(user1['token'])
    auth_logout(user2['token'])
    auth_logout(user3['token'])

    # Testing whether u_id and token are different for each user

    result01 = auth_login("email01@gmail.com", "123456")
    result02 = auth_login("email02@gmail.com", "456789")
    result03 = auth_login("email03@gmail.com", "654321")

    # checking if repetitive u_id or token are accidentally generated
    assert(result01['u_id'] != result02['u_id'])
    assert(result01['u_id'] != result03['u_id'])
    assert(result02['u_id'] != result03['u_id'])
    
    assert(result01['token'] != result02['token'])
    assert(result01['token'] != result03['token'])
    assert(result02['token'] != result03['token'])

    # check if the tokens are valid
    # if valid: auth_logout should return {'is_success': True}
    assert auth_logout(result01['token']) == {
        'is_success': True,
    }
    assert auth_logout(result02['token']) == {
        'is_success': True,
    }
    assert auth_logout(result03['token']) == {
        'is_success': True,
    }

