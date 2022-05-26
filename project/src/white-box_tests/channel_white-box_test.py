import sys
sys.path.append('../')
from auth import auth_register
from channel import channel_addowner, channel_removeowner
from channels import channels_create
from error import InputError
from pytest import raises
from other import clear


def test_channel_addowner_uid_invalid():
    '''
    test our assumpution which is that it will raise InputError if
    add a person whose u_id is invalid
    '''
    # clear data
    clear()

    # intiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)
    invalid_uid = user['u_id'] + 100

    # check if it raises InputError
    with raises(InputError):
        channel_addowner(user['token'], channel['channel_id'], invalid_uid)


def test_channel_removeowner_uid_invalid():
    '''
    test our assumpution which is that it will raise InputError if
    add a person whose u_id is invalid
    '''
    # clear data
    clear()

    # intiate data
    user = auth_register('t.holland@gmail.com', '12345678', 'Tom', 'Holland')
    channel = channels_create(user['token'], 'COMP1531', False)
    invalid_uid = user['u_id'] + 100

    # check if it raises InputError
    with raises(InputError):
        channel_removeowner(user['token'], channel['channel_id'], invalid_uid)

