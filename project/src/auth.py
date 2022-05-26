'''
Last modified on 5/11/2020 by Chan Woo Baek
'''
from error import InputError, AccessError
from data import data, User
import smtplib
import random
import string
from helper import authorise

def auth_login(email, password):
    '''
    input format:
    {
        'email': string, 
        'password': string,
    }
    Given a registered users' email and password and generates a valid token for 
    the user to remain authenticated.
    output format:
    { 
        'u_id': string, 
        'token': string,
    }
    '''
    # check if the email format is valid
    User.check_email_format(email)
    
    # Check if the password is valid
    User.check_password(password)

    # check if email belongs to a user and if the password matches
    email_belongs_to_user = False
    email_pws_matches = True

    for user in data['users']:
        if email == user.get_email():
            email_belongs_to_user = True
            u_id = user.get_u_id()
            if User.encrypt_password(password) != user.get_password():
                email_pws_matches = False
    
    if email_belongs_to_user == False:
        raise InputError(description='Email does not belong to a user')
    
    if email_pws_matches == False:
        raise InputError(description='Incorrect Password')

    return {
        'u_id': u_id,
        'token': User.generate_token(u_id),
    }

@authorise
def auth_logout(token):
    '''
    input format:
    {
        'token':string
    }
    Given an active token, invalidates the token to log the user out.
    If a valid token is given, and the user is successfully logged out, it returns true, 
    otherwise false.
    
    output format:
    { 
        'is_success': boolean
    }
    '''
    
    User.invalidate_token(token)
    return {
        'is_success': True,
    }


def auth_register(email, password, name_first, name_last):
    '''
    input format:
    {
        'email': string,
        'password': string,
        'name_first': string,
        'name_last': string,
    }
    Create a new account for them and return a new token for authentication in their session. 
    A handle is generated. A handle is generated that is the concatentation of a lowercase-only first name and last name. 
    If the concatenation is longer than 20 characters, it is cutoff at 20 characters. 
    If the handle is already taken, it is modified by appending a number to make it unique.
    
    output format:
    { 
        'u_id': int, 
        'token': string,
    }
    '''
    # Check email
    User.check_email_format(email)
    User.check_email_repeated(email)

    # Check password
    User.check_password(password)

    # check if the lengths of first name and last name are in the range 1 ~ 50 
    User.check_name_first(name_first)
    User.check_name_last(name_last)

    new_user = User(
        email=email,
        password=User.encrypt_password(password),
        name_first=name_first,
        name_last=name_last,
        handle_str=User.generate_handle(name_first, name_last),
    )

    # the u_id is generated based on the number of existing users
    u_id = len(data['users'])
    new_user.set_u_id(u_id)

    # setting the permission_id
    if u_id is 0:
        permission_id = 1
    else:
        permission_id = 2
    new_user.set_permission_id(permission_id)
    
    data['users'].append(new_user)

    return {
        'u_id': u_id,
        'token': User.generate_token(u_id),
    }

def auth_passwordreset_request(email):
    '''
    input format:
    {
        string
    }
    Creates a random string of 6 digits/char which is the reset code.
    Makes certain that the resetcode is unique.
    Sends this resetcode to the email string given in the input.

    output format:
    {}
    '''
    # Check that the email is in string format
    if isinstance(email, str) is False:
        raise InputError(description='Email is not a string')

    # Generate reset code and confirm it is unique
    resetcode = ''.join(random.choice(string.ascii_uppercase+string.digits) for _ in range(6))
    User.check_resetcode_is_unique(resetcode)

    # Check email is a registered user
    email_valid = False
    for user in data['users']:
        if email == user.get_email():
            # Give registered user the reset code
            user.set_reset_code(resetcode)
            name = user.get_name_first()
            email_valid = True
            assert(resetcode == user.get_reset_code())
    if email_valid is False:
        raise InputError(description='Email is not valid')
    
    # Create message, sender and receiver
    message = f'''
    Hello, {name}
    Your resetcode is {resetcode}
    '''
    sender = 'resetcodegenerator@gmail.com'
    receiver = email

    # Send email
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com')
        server.ehlo()
        server.login('resetcodegenerator@gmail.com', 'resetcode1!')
        server.sendmail(sender, receiver, message)
        server.close()

        print('Email Sent!')

    except Exception:
        print("Error: unable to send email")
    
    return {}

def auth_passwordreset_reset(reset_code, new_password):
    '''
    input format:
    {
        string,
        string
    }
    Check the reset code is valid.
    Check the password is valid.
    Set the new password for the user with the given resetcode.

    output format:
    {}
    '''
    # Check that reset_code is valid
    reset_code_is_valid = False
    for user in data['users']:
        if user.get_reset_code() == reset_code:
            reset_code_is_valid = True
            target = user
    
    if reset_code_is_valid == False:
        raise InputError(description='Reset Code is not valid')

    # Check that password is valid
    User.check_password(new_password)

    # Set new password
    target.set_password(User.encrypt_password(new_password))

    return {}
