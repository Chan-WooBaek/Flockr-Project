'''
Server file which runs our flask
'''
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from error import InputError
import user
import auth
import channel
import channels
import message
import other
import os
import standup

def defaultHandler(err):
    '''
    Handles errors
    '''
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__, static_url_path='/static/')
CORS(APP)
APP.config["IMAGE_UPLOADS"] = f"{os.getcwd()}/src/static"

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    '''
    Checks if we can echo, raises InputError if we cannot
    '''
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })


@APP.route("/auth/register", methods=['POST'])
def register():
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
    info_in = request.get_json()
    info_out = auth.auth_register(
        info_in['email'],
        info_in['password'], 
        info_in['name_first'], 
        info_in['name_last'],
    )
    return dumps(info_out)
    
@APP.route("/auth/logout", methods=['POST'])
def logout():
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
    info_in = request.get_json()
    info_out = auth.auth_logout(info_in['token'])
    return dumps(info_out)

@APP.route("/auth/login", methods=['POST'])
def login():
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
    info_in = request.get_json()
    info_out = auth.auth_login(
        info_in['email'],
        info_in['password'],
    )
    return dumps(info_out)

@APP.route("/user/profile", methods=['GET'])
def profile():
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
        }
    }
    '''
    # Convert the input in json format into a python object
    # info_in = request.get_json()
    token = str(request.args.get('token'))
    u_id = int(request.args.get('u_id'))
    # Input the python object into user_profile
    info_out = user.user_profile(
        token,
        u_id
    )

    # Return the output in json format
    return dumps(info_out)

@APP.route("/user/profile/setname", methods=['PUT'])
def setname():
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
    # Convert the input in json format into a python object
    info_in = request.get_json()

    # Input the python object into user_profile_setname
    user.user_profile_setname(
        info_in['token'],
        info_in['name_first'],
        info_in['name_last'],
    )

    # Return the output in json format
    return dumps({})

@APP.route("/user/profile/setemail", methods=['PUT'])
def setemail():
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
    # Convert the input in json format into a python object
    info_in = request.get_json()

    # Input the python object into user_profile_setemail
    user.user_profile_setemail(
        info_in['token'],
        info_in['email'],
    )

    # Return the output in json format
    return dumps({})

@APP.route("/user/profile/sethandle", methods=['PUT'])
def sethandle():
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
    # Convert the input in json format into a python object
    info_in = request.get_json()

    # Input the python object into user_profile_sethandle
    user.user_profile_sethandle(
        info_in['token'],
        info_in['handle_str'],
    )

    # Return the output in json format
    return dumps({})

@APP.route("/channel/invite", methods=['POST'])
def invite():
    '''
    input format:
    {
        token: string,
        channel_id: integer,
        u_id: integer,
    }
    Invites a user (with user id u_id) to join a channel with ID channel_id. 
    Once invited the user is added to the channel immediately.

    output format:
    {}
    '''
    info_in = request.get_json()
    info_out = channel.channel_invite(
        info_in['token'],
        info_in['channel_id'],
        info_in['u_id'],
    )
    return dumps(info_out)


@APP.route("/channel/details", methods=['GET'])
def details():
    '''
    input format:
    {
        token: string,
        channel_id: integer,
    }
    Given a Channel with ID channel_id that the authorised user 
    sis part of, provide basic details about the channel.

    output format:
    {  
        name: string,
        owner_members: [{u_id: integer, name_first: string, name_last: string }]
        all_members: [{u_id: integer, name_first: string, name_last: string }]
    }
    '''
    info_in = {
        'token': request.args.get('token'),
        'channel_id': int(request.args.get('channel_id')),
    }
    info_out = channel.channel_details(
        info_in['token'],
        info_in['channel_id'],
    )
    return dumps(info_out)

@APP.route("/channel/messages", methods=['GET'])
def messages():
    '''
    input format:
    {
        token: string,
        channel_id: integer,
        start: integer,
    }
    Given a Channel with ID channel_id that the authorised user is part of, 
    return up to 50 messages between index "start" and "start + 50". Message 
    with index 0 is the most recent message in the channel. This function returns
    a new index "end" which is the value of "start + 50", or, if this function 
    has returned the least recent messages in the channel, returns -1 in "end" 
    to indicate there are no more messages to load after this return.

    output format:
    {  
        messages: [{message_id: integer, u_id: integer, message: string, time_created: integer}],
        start: integer
        end: integer
    }
    '''
    info_in = {
        'token': request.args.get('token'),
        'channel_id': int(request.args.get('channel_id')),
        'start': int(request.args.get('start')),
    }
    info_out = channel.channel_messages(
        info_in['token'],
        info_in['channel_id'],
        info_in['start'],
    )
    return dumps(info_out)

@APP.route("/channel/leave", methods=['POST'])
def leave():
    '''
    input format:
    {
        token: string,
        channel_id: integer,
    }
    Given a channel ID, the user removed as a member of this channel.

    output format:
    {}
    '''
    info_in = request.get_json()
    info_out = channel.channel_leave(
        info_in['token'],
        info_in['channel_id'],
    )
    return dumps(info_out)

@APP.route("/channel/join", methods=['POST'])
def join():
    '''
    input format:
    {
        token: string,
        channel_id: integer,
    }
    Given a channel_id of a channel that the authorised user can join, adds 
    them to that channelGiven a channel_id of a channel that the authorised 
    user can join, adds them to that channel.
    
    output format:
    {}
    '''
    info_in = request.get_json()
    info_out = channel.channel_join(
        info_in['token'],
        info_in['channel_id'],
    )
    return dumps(info_out)

@APP.route("/channel/addowner", methods=['POST'])
def addowner():
    '''
    input format:
    {
        token: string,
        channel_id: integer,
        u_id: integer,
    }
    Make user with user id u_id an owner of this channel
    output format:
    {}
    '''
    info_in = request.get_json()
    info_out = channel.channel_addowner(
        info_in['token'],
        info_in['channel_id'],
        info_in['u_id'],
    )
    return dumps(info_out)

@APP.route("/channel/removeowner", methods=['POST'])
def removeowner():
    '''
    input format:
    {
        token: string,
        channel_id: integer,
        u_id: integer,
    }
    Remove user with user id u_id an owner of this channel
    output format:
    {}
    '''
    info_in = request.get_json()
    info_out = channel.channel_removeowner(
        info_in['token'],
        info_in['channel_id'],
        info_in['u_id'],
    )
    return dumps(info_out)

@APP.route("/channels/list", methods=['GET'])
def _list():
    '''
    input format:
    {
        token: string,
    }
    Provide a list of all channels (and their 
    associated details) that the authorised user is part of
    output format:
    {
        'channels':[{
            'channel_id': interger,
            'name': string,
        }],

    }
    '''
    info_in = {
        'token': request.args.get('token')
    }
    info_out = channels.channels_list(
        info_in['token']
    )
    return dumps(info_out)

@APP.route("/channels/listall", methods=['GET'])
def listall():
    '''
    input format:
    {
        token: string,
    }
    Provide a list of all channels (and their 
    associated details)
    output format:
    {
        'channels':[{
            'channel_id': interger,
            'name': string,
        }],

    }
    '''
    info_in = {
        'token': request.args.get('token')
    }
    info_out = channels.channels_listall(
        info_in['token']
    )
    return dumps(info_out)

@APP.route("/channels/create", methods=['POST'])
def create():
    '''
    input format:
    {
        token: string,
        name: string,
        is_public: boolean
    }
    Creates a new channel with that name that is 
    either a public or private channel
    output format:
    {}
    '''
    info_in = request.get_json()
    info_out = channels.channels_create(
        info_in['token'],
        info_in['name'],
        info_in['is_public'],
    )
    return dumps(info_out)

@APP.route("/message/send", methods=['POST'])
def send():
    '''
    input format:
    {
        token: string,
        channel_id: channel_id
        message: string
    }
    Send a message from authorised_user to the channel specified by channel_id
    output format:
    {}
    '''
    info_in = request.get_json()
    info_out = message.message_send(
        info_in['token'],
        info_in['channel_id'],
        info_in['message'],
    )
    return dumps(info_out)

@APP.route("/message/remove", methods=['DELETE'])
def remove():
    '''
    input format:
    {
        token: string,
        message_id: integer
    }
    Given a message_id for a message, this message is removed from the channel
    output format:
    {}
    '''
    info_in = request.get_json()
    info_out = message.message_remove(
        info_in['token'],
        info_in['message_id'],
    )
    return dumps(info_out)

@APP.route("/message/edit", methods=['PUT'])
def edit():
    '''
    input format:
    {
        token: string,
        message_id: integer,
        message: string,
    }
    Given a message_id for a message, this message is removed from the channel
    output format:
    {}
    '''
    info_in = request.get_json()
    info_out = message.message_edit(
        info_in['token'],
        info_in['message_id'],
        info_in['message'],
    )
    return dumps(info_out)

@APP.route("/clear", methods=['DELETE'])
def clear():
    '''
    input format:
    {}
    Resets the internal data of the application 
    to it's initial state
    output format:
    {}
    '''
    other.clear()
    return dumps({})

@APP.route("/users/all", methods=['GET'])
def users_all():
    '''
    input format:
    {
        token: string,
    }
    Returns a list of all users and their associated details
    out format:
    {
        'users':[{
            u_id: integer,
            email: string,
            name_first: string,
            name_last: string,
            handle_str: string
        }]
    }
    '''
    info_in = {
        'token': request.args.get('token')
    }
    info_out = other.users_all(
        info_in['token']
    )
    return dumps(info_out)

@APP.route("/admin/userpermission/change", methods=['POST'])
def admin_userpermission_change():
    '''
    input format:
    {
        token: string,
        u_id: integer,
        permission_id: integer,
    }
    Given a User by their user ID, set their permissions to new 
    permissions described by permission_id
    output format:
    {}
    '''
    info_in = request.get_json()
    info_out = other.admin_userpermission_change(
        info_in['token'],
        info_in['u_id'],
        info_in['permission_id'],
    )
    return dumps(info_out)    

@APP.route("/search", methods=['GET'])
def search():
    '''
    input format:
    {
        token: string,
        query_str: string,
    }
    Given a query string, return a collection of messages 
    in all of the channels that the user has joined that 
    match the query
    output format:
    {
        'messages': [{
            message_id: integer,
            u_id: integer,
            message: string, 
            time_created: integer,
        }]
    }
    '''
    info_in = {
        'token': request.args.get('token'),
        'query_str': request.args.get('query_str'),
    }
    info_out = other.search(
        info_in['token'],
        info_in['query_str'],
    )
    return dumps(info_out)  

@APP.route("/message/react", methods=['POST'])
def react():
    '''
    input format:
    {
        token: string,
        message_id: integer,
        react_id: integer
    }
    Given a message within a channel the authorised 
    user is part of, add a "react" to that particular message
    output format:
    {
    }
    '''
    info_in = request.get_json()
    info_out = message.message_react(
        info_in['token'],
        info_in['message_id'],
        info_in['react_id'],
    )
    return dumps(info_out)  

@APP.route("/message/unreact", methods=['POST'])
def unreact():
    '''
    input format:
    {
        token: string,
        message_id: integer,
        react_id: integer
    }
    Given a message within a channel the authorised 
    user is part of, remove a "react" to that particular message
    output format:
    {
    }
    '''
    info_in = request.get_json()
    info_out = message.message_unreact(
        info_in['token'],
        info_in['message_id'],
        info_in['react_id'],
    )
    return dumps(info_out)  

@APP.route("/message/sendlater", methods=['POST'])
def sendlater():
    '''
    input format:
    {
        token: string,
        channel_id: channel_id
        message: string
        time_sent: integer
    }
    Send a message from authorised_user to the channel specified by
    channel_id automatically at a specified time in the future
    output format:
    {
        message_id: integer
    }
    '''
    info_in = request.get_json()
    info_out = message.message_sendlater(
        info_in['token'],
        info_in['channel_id'],
        info_in['message'],
        info_in['time_sent'],
    )
    return dumps(info_out)

@APP.route("/auth/passwordreset/request", methods=['POST'])
def passwordreset_request():
    '''
    input format:
    {
        email: string
    }
    Given a valid email which belongs to a user stored,
    send a resetcode to the given email
    {}
    '''
    info_in = request.get_json()
    auth.auth_passwordreset_request(info_in['email'])
    
    return dumps({})

@APP.route("/auth/passwordreset/reset", methods=['POST'])
def passwordreset_reset():
    '''
    input format:
    {
        reset_code: string
        new_password: string
    }
    Given a reset code which belongs to a user and a new valid password,
    change the target users' password to the new valid password.
    {}
    '''
    info_in = request.get_json()
    auth.auth_passwordreset_reset(
        info_in['reset_code'],
        info_in['new_password']
    )
    
    return dumps({})

@APP.route("/message/pin", methods=['POST'])
def pin():
    '''
    input format:
    {
        token: string,
        message_id: integer,
    }
    Given a message within a channel, mark it as "pinned" to be given 
    special display treatment by the frontend
    output format:
    {
    }
    '''
    info_in = request.get_json()
    info_out = message.message_pin(
        info_in['token'],
        info_in['message_id'],
    )
    return dumps(info_out)  

@APP.route("/message/unpin", methods=['POST'])
def unpin():
    '''
    input format:
    {
        token: string,
        message_id: integer,
    }
    Given a message within a channel, remove it's mark as unpinned
    output format:
    {
    }
    '''
    info_in = request.get_json()
    info_out = message.message_unpin(
        info_in['token'],
        info_in['message_id'],
    )
    return dumps(info_out) 
@APP.route("/user/profile/uploadphoto", methods=['POST'])
def uploadphoto():
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
    info_in = request.get_json()
    info_out = user.user_profile_uploadphoto(
        info_in['token'],
        info_in['img_url'],
        int(info_in['x_start']),
        int(info_in['y_start']),
        int(info_in['x_end']),
        int(info_in['y_end']),
    )
    return dumps(info_out)

@APP.route('/static/<path:path>')
def send_js(path):
    '''
    Send the image back to server based on the passed in path.
    '''
    return send_from_directory(APP.config["IMAGE_UPLOADS"], path)

@APP.route("/standup/start", methods=['POST'])
def start():
    '''
    input format:
    {
        token: string,
        channel_id: channel_id
        length: integer
    }
    For a given channel, start the standup period whereby 
    for the next "length" seconds if someone calls "standup_send" 
    with a message, it is buffered during the X second window 
    then at the end of the X second window a message will be added 
    to the message queue in the channel from the user who started 
    the standup. X is an integer that denotes the number of seconds 
    that the standup occurs for
    output format:
    {
        time_finish: integer
    }
    '''
    info_in = request.get_json()
    info_out = standup.standup_start(
        info_in['token'],
        info_in['channel_id'],
        info_in['length'],
    )
    return dumps(info_out)

@APP.route("/standup/active", methods=['GET'])
def active():
    '''
    input format:
    {
        token: string,
        channel_id: integer
    }
    For a given channel, return whether a standup is 
    active in it, and what time the standup finishes. 
    If no standup is active, then time_finish returns None
    output format:
    {
        is_active: boolean
        time_finish: integer
    }
    '''
    info_in = {
        'token': request.args.get('token'),
        'channel_id': int(request.args.get('channel_id'))
    }
    info_out = standup.standup_active(
        info_in['token'],
        info_in['channel_id'],
    )
    return dumps(info_out)

@APP.route("/standup/send", methods=['POST'])
def standup_send():
    '''
    input format:
    {
        token: string,
        channel_id: channel_id,
        message: string
    }
    Sending a message to get buffered in the 
    standup queue, assuming a standup is currently active
    output format:
    {
        time_finish: integer
    }
    '''
    info_in = request.get_json()
    info_out = standup.standup_send(
        info_in['token'],
        info_in['channel_id'],
        info_in['message'],
    )
    return dumps(info_out)

if __name__ == "__main__":
    APP.run(port=0) # Do not edit this port
