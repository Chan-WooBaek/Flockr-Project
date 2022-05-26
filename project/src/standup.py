'''
Created on 05/11/2020
Contains functions: standup_start, standup_active, standup_send
'''
from data import data, User, Channel, Message
from datetime import datetime, timedelta, timezone
from error import InputError, AccessError
from datetime import datetime, timezone
from helper import authorise
import threading

@authorise
def standup_start(token, channel_id, length):
    '''
    input format:
    {
        token: string
        channel_id: integer
        length: integer
    } 

    For a given channel, start the standup period whereby 
    for the next "length" seconds if someone calls 
    "standup_send" with a message, it is buffered during 
    the X second window then at the end of the X second 
    window a message will be added to the message queue in 
    the channel from the user who started the standup. X is 
    an integer that denotes the number of seconds that the 
    standup occurs for.

    output format:
    {'time_finish': integer}
    '''
    # find the matching user by token 
    u_id = User.get_uid_from_token(token)

    # Channel ID is not a valid channel
    index = Channel.find_channel(channel_id)
    if index is None:
        raise InputError(description="Channel not found")
    channel = data['channels'][index]

    # user is not in channel
    if not Channel.is_user_in_channel(u_id, channel_id):
        raise AccessError(description="The user has to be a member of this channel")

    # An active standup is currently running in this channel
    if standup_active(token, channel_id)['is_active']:
        raise InputError(description="Active standup exists")
    
    dt_time_finish = datetime.utcnow() + timedelta(seconds=int(length))
    time_finish = int(dt_time_finish.replace(tzinfo=timezone.utc).timestamp())
    channel.set_time_finish(time_finish)

    # create a new message to be sent at the time_finish
    # it is first initialised to be an empty string and the new messages using
    # standup_send will be appended to the string

    # Create object of Message classs
    # set attributes and set message empty string at first
    message = Message(
        len(data['messages']), 
        u_id, 
        '', 
        channel_id, 
        int(datetime.utcnow().replace(tzinfo=timezone.utc).timestamp()), 
        [{'react_id': 1, 'u_ids': []}], 
        False,
    )

    # Add the message to the list of messages
    data['messages'].append(message)

    # modify message after time_diff seconds
    t = threading.Timer(length, Channel.standup_send_final_message, (channel, message,))
    t.start()
    return {'time_finish': time_finish}

@authorise
def standup_active(token, channel_id):
    '''
    input format:
    {
        token: string
        channel_id: integer
        length: integer
    }

    For a given channel, return whether 
    a standup is active in it, and what time the a
    standup finishes. If no standup is active, then 
    time_finish returns None

    output format
    {'is_active': boolean, 'time_finish': integer}
    '''
    # find the matching user by token s
    u_id = User.get_uid_from_token(token)

    # Channel ID is not a valid channel
    index = Channel.find_channel(channel_id)
    if index is None:
        raise InputError(description="Channel not found")
    channel = data['channels'][index]

    # user is not in channel
    if not Channel.is_user_in_channel(u_id, channel_id):
        raise AccessError(description="The user has to be a member of this channel")
    time_finish = channel.get_time_finish()
    is_active = True
    if time_finish is None:
        return {'is_active': False, 'time_finish': None}
    
    if time_finish < int(datetime.utcnow().replace(tzinfo=timezone.utc).timestamp()):
        is_active = False
    
    return {'is_active': is_active, 'time_finish': time_finish}

@authorise
def standup_send(token, channel_id, message):
    '''
    input format:
    {
        token: string
        channel_id: integer
        message: string
    }

    Sending a message to get buffered in the 
    standup queue, assuming a standup is currently active

    output format:
    {}
    '''
    # find the matching user by token s
    u_id = User.get_uid_from_token(token)

    # get the user object with this u_id
    user_index = User.find_user(u_id)
    user = data['users'][user_index]

    # Channel ID is not a valid channel
    channel_index = Channel.find_channel(channel_id)
    if channel_index is None:
        raise InputError(description="Channel not found")
    channel = data['channels'][channel_index]

    # user is not in channel
    if not Channel.is_user_in_channel(u_id, channel_id):
        raise AccessError(description="The user has to be a member of this channel")

    # Message is more than 1000 characters
    if len(message) > 1000:
        raise InputError(description="The message is too long.")

    # An active standup is not currently running in this channel
    if not standup_active(token, channel_id)['is_active']:
        raise InputError(description="Active standup exists")
    
    # Formating the message
    new_message = f"{user.get_handle_str()}: {message}\n"

    # append the new_massage to the existing message queue
    channel.standup_message_append(new_message)
    return {}