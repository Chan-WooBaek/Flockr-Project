'''
Functions for user.py
created on 11/10/2020 by Chan Baek and Xinran Zhu
'''
from data import data, User
from error import InputError, AccessError
import urllib.request
from PIL import Image
from flask import Flask, request
import os

APP = Flask(__name__, static_url_path='/static/')
APP.config["IMAGE_UPLOADS"] = f"{os.getcwd()}/src/static"


def user_profile(token, u_id):
    '''
    input format:
    (
        token: string
        u_id: integer
    )
    For a valid user, returns information about their user_id, email, first name, last name, and handle

    output format:
    {
        user: {
            'u_id': integer,
            'email': string,
            'name_first': string,
            'name_last': string,
            'handle_str': string,
            'profile_img_url': string,
        }
    }
    '''
    # Check if token is valid
    if User.get_uid_from_token(token) is None:
        raise AccessError(description="Invalid Token")

    # Check that user exists
    index = User.find_user(u_id)
    if index is None:
        raise InputError(description="User not found")

    user = data['users'][index]

    # Return the user profile
    return {
        'user': {
            'u_id': u_id,
            'email': user.get_email(),
            'name_first': user.get_name_first(),
            'name_last': user.get_name_last(),
            'handle_str': user.get_handle_str(),
            'profile_img_url': user.get_profile_img_url(),
        },
    }

def user_profile_setname(token, name_first, name_last):
    '''
    input format:
    (
        token: string
        name_first: string
        name_last: string
    )
    For a valid user, renames current name_first and name_last of token user into
    given name_first and name_last

    output format:
    {}
    '''
    # Get u_id
    u_id = User.get_uid_from_token(token)

    # Check if token is valid
    if u_id is None:
        raise AccessError(description="Invalid Token")

    # Check that the first and last name is valid
    User.check_name_first(name_first)
    User.check_name_last(name_last)

    # Set the new name for the user given
    data['users'][u_id].set_name_first(name_first)
    data['users'][u_id].set_name_last(name_last)
    return {
    }

def user_profile_setemail(token, email):
    '''
    input format:
    (
        token: string
        email: string
    )
    For a valid user, renames current email of token user into
    given email

    output format:
    {}
    '''
    # Get u_id
    u_id = User.get_uid_from_token(token)

    # Check if token is valid
    if u_id is None:
        raise AccessError(description="Invalid Token")

    # Check email is valid
    User.check_email_format(email)
    User.check_email_repeated(email)

    # Set the new email for the user given
    data['users'][u_id].set_email(email)
    return {
    }

def user_profile_sethandle(token, handle_str):
    '''
    input format:
    (
        token: string
        handle: string
    )
    For a valid user, renames current handle of token user into
    given handle

    output format:
    {}
    '''
    # Get u_id
    u_id = User.get_uid_from_token(token)
    
    # Check if token is valid
    if u_id is None:
        raise AccessError(description="Invalid Token")

    # Check that the handle is valid
    User.check_handle(handle_str)

    data['users'][u_id].set_handle_str(handle_str)
    return {
    }

def user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    '''
    Input format:
    {
        token: string,
        img_url: string,
        x_start: integer,
        y_start: integer
        x_end: integer,
        y_end: integer,
    }
    Given a URL of an image on the internet, crops the image within bounds 
    (x_start, y_start) and (x_end, y_end). Position (0,0) is the top left.
    Output format:
    {}  
    '''
    u_id = User.get_uid_from_token(token)

    # check if the token is valid
    if u_id is None:
        raise AccessError(description="Invalid Token")

    # find the corresponding user object
    user_index = User.find_user(u_id)
    user = data['users'][user_index]

    # the filename of the image is determined by the handle of the user
    filename = f"{user.get_handle_str()}.jpg"

    # the file is saved under the static directory
    # InputError is raised if the url is not valid
    filepath = os.path.join(APP.config['IMAGE_UPLOADS'], filename)
    try:
        header = urllib.request.urlretrieve(img_url, filepath)[1]
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError):
        raise InputError(description="Invalid URL")

    # Image uploaded is not a JPG
    if header['Content-Type'] not in ['image/jpeg','image/jpg']:
        raise InputError(description="Invalid image type")

    # cropping the image
    image = Image.open(filepath)
    width, height = image.size

    # check if the coordinates are in the valid dimensions.
    is_x_ok = x_start in range(width + 1) and x_end in range(width + 1) and x_start < x_end
    is_y_ok = y_start in range(height + 1) and y_end in range(height + 1) and y_start < y_end
    if not is_x_ok or not is_y_ok:
        raise InputError(description="Invalid dimensions")

    image_cropped = image.crop((x_start, y_start, x_end, y_end))

    image_cropped.save(filepath)

    # generate the unique url for this image and store it in the user object
    url = f"{str(request.host_url)}static/{filename}"
    user.set_profile_img_url(url)
    
    return {}
