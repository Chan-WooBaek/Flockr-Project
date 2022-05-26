'''
Testing user.py
created on 11/10/2020 by Chan Baek and Xinran Zhu
'''
import sys
sys.path.append('../')
from pytest import raises
from user import user_profile, user_profile_setname, user_profile_setemail, user_profile_sethandle, user_profile_uploadphoto
from data import data
from other import clear
from error import InputError, AccessError
from auth import auth_register, auth_logout

def test_profile_regular_single():
    '''
    Test if user_profile() return the correct information of the user
    '''
    clear()
    result = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    user = user_profile(result['token'], result['u_id'])
    
    assert user['user']['u_id'] == result['u_id']
    assert user['user']['email'] == 'email01@gmail.com'
    assert user['user']['name_first'] == 'Alexander'
    assert user['user']['name_last'] == 'Abdelrahman'
    assert user['user']['handle_str'] == 'alexanderabdelrahman'


def test_profile_regular_multiple():
    '''
    Test if user_profile() return the correct information of
    the user when there are multiple users existed
    '''

    clear()
    auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    auth_register("email02@gmail.com", "123456", "Amy", "Abdelrahman")
    result = auth_register("email03@gmail.com", "123456", "Alex", "Abdel")

    user = user_profile(result['token'], result['u_id'])

    assert user['user']['u_id'] == result['u_id']
    assert user['user']['email'] == 'email03@gmail.com'
    assert user['user']['name_first'] == 'Alex'
    assert user['user']['name_last'] == 'Abdel'
    assert user['user']['handle_str'] == 'alexabdel'

def test_profile_invalid_u_id():
    '''Test if user_profile() raises InputError when an invalid u_id is passed in'''

    clear()
    result = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    with raises(InputError):
        user_profile(result['token'], result['u_id'] + 1)

def test_profile_invalid_token():
    '''Test if user_profile() raises AccessError when an invalid token is passed in'''
    clear()
    user = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    with raises(AccessError):
        # invalid format for token
        user_profile(f"{user['token']}invalid", user['u_id'])

    # invalidate the active token
    auth_logout(user['token'])
    with raises(AccessError):
        # invalidated token
        user_profile(user['token'], user['u_id'])

def test_setname_first_name():
    """Test if user_profile_setname() changes the desired users first name"""
    clear()
    result1 = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    result2 = auth_register("email02@gmail.com", "456789", "Hamilton", "Abercrombie")
    result3 = auth_register("email03@gmail.com", "654321", "Constantine", "MacDonough")

    user_profile_setname(result1['token'], 'Alex', 'Abdel')
    user_profile_setname(result2['token'], 'Ham', 'Aber')
    user_profile_setname(result3['token'], 'Con', 'Mac')

    expected1 = user_profile(result1['token'], result1['u_id'])
    expected2 = user_profile(result2['token'], result2['u_id'])
    expected3 = user_profile(result3['token'], result3['u_id'])

    assert expected1['user']['name_first'] == 'Alex'
    assert expected2['user']['name_first'] == 'Ham'
    assert expected3['user']['name_first'] == 'Con'

def test_setname_first_name_invalid():
    """Test if user_profile_setname() raises InputError given an invalid first name"""
    clear()
    result1 = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    with raises(InputError):
        user_profile_setname(result1['token'], '', 'Abdel')

def test_setname_last_name():
    """Test if user_profile_setname() changes the desired users last name"""
    clear()
    result1 = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    result2 = auth_register("email02@gmail.com", "456789", "Hamilton", "Abercrombie")
    result3 = auth_register("email03@gmail.com", "654321", "Constantine", "MacDonough")

    user_profile_setname(result1['token'], 'Alex', 'Abdel')
    user_profile_setname(result2['token'], 'Ham', 'Aber')
    user_profile_setname(result3['token'], 'Con', 'Mac')

    expected1 = user_profile(result1['token'], result1['u_id'])
    expected2 = user_profile(result2['token'], result2['u_id'])
    expected3 = user_profile(result3['token'], result3['u_id'])

    assert expected1['user']['name_last'] == 'Abdel'
    assert expected2['user']['name_last'] == 'Aber'
    assert expected3['user']['name_last'] == 'Mac'

def test_setname_last_name_invalid():
    """Test if user_profile_setname() raises InputError given an invalid last name"""
    clear()
    result1 = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    with raises(InputError):
        user_profile_setname(result1['token'], 'Alex', '')

def test_profile_setname_invalid_token():
    '''Test if user_profile_setname() raises AccessError when an invalid token is passed in'''
    clear()
    user = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    with raises(AccessError):
        user_profile_setname(f"{user['token']}invalid", 'newnamefirst', 'newnamelast')

    # invalidate the active token
    auth_logout(user['token'])
    with raises(AccessError):
        # invalidated token
        user_profile_setname(user['token'], 'newnamefirst', 'newnamelast')

def test_setemail():
    """Test if user_profile_setemail changes the desired users email"""
    clear()
    result1 = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    result2 = auth_register("email02@gmail.com", "456789", "Hamilton", "Abercrombie")
    result3 = auth_register("email03@gmail.com", "654321", "Constantine", "MacDonough")

    user_profile_setemail(result1['token'], 'email01@hotmail.com')
    user_profile_setemail(result2['token'], 'email02@hotmail.com')
    user_profile_setemail(result3['token'], 'email03@hotmail.com')

    expected1 = user_profile(result1['token'], result1['u_id'])
    expected2 = user_profile(result2['token'], result2['u_id'])
    expected3 = user_profile(result3['token'], result3['u_id'])

    assert expected1['user']['email'] == 'email01@hotmail.com'
    assert expected2['user']['email'] == 'email02@hotmail.com'
    assert expected3['user']['email'] == 'email03@hotmail.com'

def test_setemail_invalid():
    """Test if user_profile_setemail raises an error when given an invalid email"""
    clear()
    result1 = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    with raises(InputError):
        user_profile_setemail(result1['token'], 'invalidemail')

def test_profile_setemail_invalid_token():
    '''Test if user_profile_setemail() raises AccessError when an invalid token is passed in'''
    clear()
    user = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    with raises(AccessError):
        # invalid format for token
        user_profile_setemail(f"{user['token']}invalid", 'newemail@hotmail.com')

    # invalidate the active token
    auth_logout(user['token'])
    with raises(AccessError):
        # invalidated token
        user_profile_setemail(user['token'], 'newemail@hotmail.com')

def test_profile_sethandle_regular():
    '''
    Test if user_profile_sethandle() successfully modified the handle_str.
    Assuming that user_profile() is working properly
    '''
    clear()
    result01 = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    user_profile_sethandle(result01['token'], "changedhandle01")
    user01 = user_profile(result01['token'], result01['u_id'])
    assert user01['user']['handle_str'] == "changedhandle01"

    result02 = auth_register("email02@gmail.com", "123456", "Alexander", "Abdelrahman")
    user_profile_sethandle(result02['token'], "changedhandle02")
    user02 = user_profile(result02['token'], result02['u_id'])
    assert user02['user']['handle_str'] == "changedhandle02"

    result03 = auth_register("email03@gmail.com", "123456", "Alexander", "Abdelrahman")
    user_profile_sethandle(result03['token'], "changedhandle03")
    user03 = user_profile(result03['token'], result03['u_id'])
    assert user03['user']['handle_str'] == "changedhandle03"

def test_profile_sethandle_handle_too_long():
    '''
    Test if user_profile_sethandle() raises InputError
    when a more than 20 characters handle_str is passed in.
    '''
    clear()
    result = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    with raises(InputError):
        user_profile_sethandle(result['token'], "thisisareallylonghandlestr")

def test_profile_sethandle_handle_too_short():
    '''
    Test if user_profile_sethandle() raises InputError
    when a less than 3 characters handle_str is passed in.
    '''
    clear()
    result = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    with raises(InputError):
        user_profile_sethandle(result['token'], "ab")

def test_profile_sethandle_handle_repeated():
    '''
    Test if user_profile_sethandle() raises InputError
    when a handle is repeated.
    '''
    clear()
    result = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    auth_register("email01@hotmail.com", "123456", "Alex", "Abdel")
    with raises(InputError):
        user_profile_sethandle(result['token'], "alexabdel")

def test_profile_sethandle_invalid_token():
    '''Test if user_profile_sethandle() raises AccessError when an invalid token is passed in'''
    # create a new user

    clear()
    user = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    with raises(AccessError):
        # invalid format for token
        user_profile_sethandle(f"{user['token']}invalid", 'newhandlestr')

    # invalidate the active token
    auth_logout(user['token'])
    with raises(AccessError):
        # invalidated token
        user_profile_sethandle(user['token'], 'newhandlestr')

def test_uploadphoto_invalid_token():
    '''Test if user_profile_uploadphoto() raises AccessError when an invalid token is passed in'''
    
    clear()

    # create a new user
    user = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")

    # a valid url of a jpg file
    img_url = "https://www.courant.com/resizer/D9qmAnzR8PY5q-GBdUBBVuNVUTs=/415x311/top/arc-anglerfish-arc2-prod-tronc.s3.amazonaws.com/public/NTWCZKYTDJBI7CASRJ32F2RN6E.jpg"
    with raises(AccessError):
        # invalid format for token
        user_profile_uploadphoto(f"{user['token']}invalid", img_url, 20, 20, 30, 30)

    # invalidate the active token
    auth_logout(user['token'])
    with raises(AccessError):
        # invalidated token
        user_profile_uploadphoto(user['token'], img_url, 20, 20, 30, 30)

def test_upload_invalid_dimensions():
    '''
    Test if an InputError is raised when an invalid dimension is passed in
    '''

    clear()
    user = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")
    img_url = "https://www.courant.com/resizer/D9qmAnzR8PY5q-GBdUBBVuNVUTs=/415x311/top/arc-anglerfish-arc2-prod-tronc.s3.amazonaws.com/public/NTWCZKYTDJBI7CASRJ32F2RN6E.jpg"
    
    # pass in different invalid dimensions

    # negative x_start
    with raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, -10, 10, 20, 20)
    
    # negative y_start
    with raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 10, -10, 20, 20)
    
    # negative x_end
    with raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 10, 10, -20, 20)
    
    # negative y_end
    with raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 10, 10, 20, -20)
    
    # x_start too large
    with raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 5000, 10, 20, 20)
    
    # y_start too large
    with raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 10, 5000, 20, 20)
    
    # x_end too large
    with raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 10, 10, 5000, 20)
    
    # y_end too large
    with raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 10, 10, 20, 5000)

    # x_end < x_start
    with raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 10, 10, 5, 200)
    
    # y_end < y_start
    with raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 10, 50, 20, 20)

def test_uploadphoto_invalid_jpg():
    '''
    Test if an InputError is raised when the img_url of a non-jpg image is passed in
    '''
    
    clear()
    # create a new user
    user = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")

    # png image
    img_url = "https://img.lovepik.com/element/40082/9836.png_300.png"

    # uploading a non jpg image
    with raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 10, 10, 20, 20)

def test_uploadphoto_invalid_url():
    '''
    Test if an InputError is raised when an invalid img_url is passed in
    '''
    
    clear()
    # create a new user
    user = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")

    # invalid url
    img_url = "ThisIsAnInvalidUrl"

    # trying to uplaod an image from an invalid url
    with raises(InputError):
        user_profile_uploadphoto(user['token'], img_url, 10, 10, 20, 20)


# This is the equivalent backend black box tests for the one in the user_http_test
# However the generation of the profile_img_url requires the server to be running,
# therefore this test is excluded.
# def test_uploadphoto_regular():
#     '''
#     Test if the img_url of a user is modified when the function 
#     user_profile_uploadphoto is called.
#     '''

#     clear()

#     # create a new user
#     user = auth_register("email01@gmail.com", "123456", "Alexander", "Abdelrahman")

#     # a valid url of a jpg file
#     img_url = "https://www.courant.com/resizer/D9qmAnzR8PY5q-GBdUBBVuNVUTs=/415x311/top/arc-anglerfish-arc2-prod-tronc.s3.amazonaws.com/public/NTWCZKYTDJBI7CASRJ32F2RN6E.jpg"

#     # pass in valid arguments
#     user_profile_uploadphoto(user['token'], img_url, 10, 10, 20, 20)

#     result = user_profile(user['token'], user['u_id'])
#     assert result['profile_img_url'] != ''