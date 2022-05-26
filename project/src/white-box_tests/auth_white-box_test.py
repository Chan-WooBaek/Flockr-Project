'''
White-box test of auth.py
'''
import sys
sys.path.append('../')

from data import data
from auth import auth_register,auth_passwordreset_request, auth_passwordreset_reset
from other import clear
from pytest import raises
from error import InputError
import hashlib

def test_handle_str_large():
    '''
    White-box test: test when the repeated concatentation
    has less than or equal to 20 characters
    '''
    clear()
    auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    auth_register("email02@gmail.com", "123456", "Alexander", "Abdelrahman") 
    auth_register("email03@gmail.com", "123456", "Alexander", "Abdelrahman")   
    auth_register("email04@gmail.com", "123456", "Alexander", "Abdelrahman")    
    auth_register("email05@gmail.com", "123456", "Alexander", "Abdelrahman")    
    auth_register("email06@gmail.com", "123456", "Alexander", "Abdelrahman")    
    auth_register("email07@gmail.com", "123456", "Alexander", "Abdelrahman")   
    auth_register("email08@gmail.com", "123456", "Alexander", "Abdelrahman") 
    auth_register("email09@gmail.com", "123456", "Alexander", "Abdelrahman")   
    auth_register("email10@gmail.com", "123456", "Alexander", "Abdelrahman")    
    auth_register("email11@gmail.com", "123456", "Alexander", "Abdelrahman") 
    auth_register("email12@gmail.com", "123456", "Alexander", "Abdelrahman") 

    assert data['users'][1].get_handle_str() == "alexanderabdelrahma0"
    assert data['users'][11].get_handle_str() == "alexanderabdelrahm10"

def test_handle_str_small():
    '''
    White-box test: test when the repeated concatentation has more than 20 characters
    '''
    clear()
    auth_register("email01@gmail.com", "123456", "Alex", "Abdel")
    auth_register("email02@gmail.com", "123456", "Alex", "Abdel") 
    auth_register("email03@gmail.com", "123456", "Alex", "Abdel")  
    auth_register("email04@gmail.com", "123456", "Alex", "Abdel")    
    auth_register("email05@gmail.com", "123456", "Alex", "Abdel")   
    auth_register("email06@gmail.com", "123456", "Alex", "Abdel")   
    auth_register("email07@gmail.com", "123456", "Alex", "Abdel")   
    auth_register("email08@gmail.com", "123456", "Alex", "Abdel") 
    auth_register("email09@gmail.com", "123456", "Alex", "Abdel")   
    auth_register("email10@gmail.com", "123456", "Alex", "Abdel")   
    auth_register("email11@gmail.com", "123456", "Alex", "Abdel") 
    auth_register("email12@gmail.com", "123456", "Alex", "Abdel") 

    assert data['users'][1].get_handle_str() == "alexabdel0"
    assert data['users'][11].get_handle_str() == "alexabdel10"

def test_passwordreset_request():
    '''
    White-box test: test if auth_passwordreset_request functions as intended
    '''
    clear()

    auth_register("emailreceivebot@gmail.com", "123456", "Alexander", "Abdelrahman")
    auth_passwordreset_request("emailreceivebot@gmail.com")

    assert data['users'][0].get_reset_code() != None

def test_passwordreset_request_invalid_email_format():
    '''
    White-box test: test if auth_passwordreset_request raises an InputError when input email string
    is not valid
    '''
    clear()

    auth_register("emailreceivebot@gmail.com", "123456", "Alexander", "Abdelrahman")

    with raises(InputError):
        auth_passwordreset_request('invalidemail')

def test_passwordreset_request_email_not_string():
    '''
    White-box test: test if auth_passwordreset_request raises an InputError when input email is not
    a string
    '''
    clear()

    auth_register("emailreceivebot@gmail.com", "123456", "Alexander", "Abdelrahman")
    
    with raises(InputError):
        auth_passwordreset_request(1)
    
    with raises(InputError):
        auth_passwordreset_request(None)

def test_passwordreset_request_email_not_in_data():
    '''
    White-box test: tests if auth_passwordreset_request raises an InputError when the input email does
    not exist within data['users']
    '''
    clear()

    auth_register("emailreceivebot@gmail.com", "123456", "Alexander", "Abdelrahman")

    with raises(InputError):
        auth_passwordreset_request('emailnotindata@gmail.com')

def test_passwordreset_reset():
    '''
    White-box test: tests if auth_passwordreset_reset functions as intended
    '''
    clear()
    auth_register("emailreceivebot@gmail.com", "123456", "Alexander", "Abdelrahman")
    auth_passwordreset_request('emailreceivebot@gmail.com')
    auth_passwordreset_reset(data['users'][0].get_reset_code(), 'passwordnew')

    assert data['users'][0].get_password() == hashlib.sha256('passwordnew'.encode()).hexdigest()

def test_passwordreset_reset_invalid_pws():
    '''
    White-box test: tests if auth_passwordreset_reset raises an InputError when the input password
    is invalid
    '''
    clear()
    auth_register("emailreceivebot@gmail.com", "123456", "Alexander", "Abdelrahman")
    auth_passwordreset_request('emailreceivebot@gmail.com')
    
    with raises(InputError):
        auth_passwordreset_reset(data['users'][0].get_reset_code(), 'pass')

def test_passwordreset_reset_invalid_reset_code():
    '''
    White-box test: tests if auth_passwordreset_reset raises an InputError when the input resetcode
    is invalid
    '''
    clear()
    auth_register("emailreceivebot@gmail.com", "123456", "Alexander", "Abdelrahman")
    auth_passwordreset_request('emailreceivebot@gmail.com')
    
    with raises(InputError):
        auth_passwordreset_reset('invalidcode', 'password')
