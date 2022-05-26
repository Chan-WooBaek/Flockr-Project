from data import data, User, Channel, Message
from error import InputError, AccessError
from datetime import datetime, timezone
import threading
from helper import authorise

@authorise
def message_send(token, channel_id, message):
    '''
    Send a message from authorised_user to the channel specified by channel_id
	Input format:
    (
        token: string,
		channel_id: integer,
		message: string,
    )
    Output format:
    {
        message_id: integer
    }
    '''
    # find the matching user by token 
    u_id = User.get_uid_from_token(token)

    # InputError when message is more than 1000 characters
    if len(message) > 1000:
        raise InputError(description="Message Too Long")

    user_index = User.find_user(u_id)
    # AccessError when the authorised user has not 
    # joined the channel they are trying to post to
    if Channel.is_user_in_channel(u_id, channel_id) == False and data['users'][user_index].get_permission_id() != 1:
        raise AccessError(description="Authorised User Not In Channel")
    
    # Assumption: InputError when message is empty string
    if len(message) == 0:
        raise InputError(description="Invalid Message(empty string)")

    # intiate message, message_id is non-neagtive interger which starts from 0
    message_detail = Message()
    message_detail.set_message_id(len(data['messages']))
    message_detail.set_message(message)
    message_detail.set_u_id(u_id)
    message_detail.set_channel_id(channel_id)
    message_detail.set_reacts([{'react_id': 1, 'u_ids': []}])
    message_detail.set_is_pinned(False)
    dt_now = datetime.utcnow()
    timestamp = int(dt_now.replace(tzinfo=timezone.utc).timestamp())
    message_detail.set_time_created(timestamp)
    # insert message to the front of data['messages']
    data['messages'].append(message_detail)

    # return a dictionary which contains message_id
    return {
        'message_id': message_detail.get_message_id()
    }

@authorise
def message_remove(token, message_id):
    '''
    Given a message_id for a message, this message is removed from the channel
	Input format:
    (
        token: string,
		message_id: integer,
    )
    Output format:
    {
    }
    '''
    # find the matching user by token
    u_id = User.get_uid_from_token(token)

    message_index = Message.find_message(message_id)    
    # InputError when message (based on ID) no longer exists
    if message_index == None or data['messages'][message_index].get_message() == '':
        raise InputError(description="Message Not Exist")

    remove_message = data['messages'][message_index]
    user_index = User.find_user(u_id)
    # AccessError when none of the following are true:
    # Message with message_id was sent by the authorised user making this request
    # The authorised user is an owner of this channel or the flockr
    if remove_message.get_u_id() != u_id and Channel.is_user_owner(u_id, remove_message.get_channel_id()) == False \
    and data['users'][user_index].get_permission_id() != 1:
        raise AccessError(description="No Permission")
    
    # remove the message from the channel. If the message is empty string, it no longer exist.
    data['messages'][message_index].set_message('')

    return {
    }

@authorise
def message_edit(token, message_id, message):
    '''
    Given a message, update it's text with new text. 
    If the new message is an empty string, the message is deleted.
	Input format:
    (
        token: string,
		message_id: integer,
        message: string,
    )
    Output format:
    {
    }
    '''
    # find the matching user by token 
    u_id = User.get_uid_from_token(token)

    message_index = Message.find_message(message_id)
    # Assumption: InputError when message (based on ID) no longer exists
    if message_index == None or data['messages'][message_index].get_message() == '':
        raise InputError(description="Message Not Exist")
    
    edit_message = data['messages'][message_index]
    user_index = User.find_user(u_id)
    # AccessError when none of the following are true:
    # Message with message_id was sent by the authorised user making this request
    # The authorised user is an owner of this channel or the flockr
    if edit_message.get_u_id() != u_id and Channel.is_user_owner(u_id, edit_message.get_channel_id()) == False \
    and data['users'][user_index].get_permission_id() != 1:
        raise AccessError(description="No Permission")

    if len(message) > 1000:
        raise InputError(description="Invalid Message")

    # update message's text with new text.
    data['messages'][message_index].set_message(message)

    return {
    }

@authorise
def message_sendlater(token, channel_id, message, time_sent):
    '''
    Send a message from authorised_user to the channel specified by channel_id 
    automatically at a specified time in the future
    (
        token: string
        channel_id: integer
        message: string
        time_sent: integer
    )
    Output format:
    {
    }
    '''
    # find the matching user by token
    u_id = User.get_uid_from_token(token)

    dt_now = datetime.utcnow()
    time_now = int(dt_now.replace(tzinfo=timezone.utc).timestamp())
    time_diff = time_sent - time_now

    channel_index = Channel.find_channel(channel_id)
    # InputError when any of:
    #   Channel ID is not a valid channel
    #   Message is more than 1000 characters
    #   Time sent is a time in the past
    if channel_index == None or len(message) > 1000 or time_diff < 0:
        raise InputError(description="Invalid Channel ID or Invalid Message or Invalid Time")

    # AccessError when: the authorised user has not joined the channel 
    # they are trying to post to
    if Channel.is_user_in_channel(u_id, channel_id) == False:
        raise AccessError(description="Authorised User Not In Channel")

    # Create object of Message classs
    message_detail = Message()

    # set attributes and set message empty string at first
    message_detail.set_message_id(len(data['messages']))
    message_detail.set_message('')
    message_detail.set_u_id(u_id)
    message_detail.set_channel_id(channel_id)
    message_detail.set_reacts([{'react_id': 1, 'u_ids': []}])
    message_detail.set_is_pinned(False)
    message_detail.set_time_created(time_sent)
    # insert message to the front of data['messages']
    data['messages'].append(message_detail)

    # modify message after time_diff seconds
    t = threading.Timer(time_diff, Message.modify_message, (message_detail, message,))
    t.start()

    return {
        'message_id': message_detail.get_message_id(),
    }

@authorise
def message_react(token, message_id, react_id):
    '''
    Given a message within a channel the authorised user is part of add a "react" to that particular message
    Input format:
    (
        token: string, 
        message_id: integer, 
        react_id: integer
    )
    Output format:
    {
    }
    '''
    # find the matching user by token
    u_id = User.get_uid_from_token(token)

    # InputError when any of:
    # message_id is not a valid message within a channel that the authorised user has joined
    # react_id is not a valid React ID. The only valid react ID the frontend has is 1
    # Message with ID message_id already contains an active React with ID react_id from the authorised user
    message_index = Message.find_message(message_id)
    if message_index == None or Channel.is_user_in_channel(u_id, data['messages'][message_index].get_channel_id()) == False or \
    react_id != 1 or Message.is_message_reacted_by_user(u_id, message_id, react_id) == True:
        raise InputError(description="Invalid Message ID or Invalid React ID")

    # Append u_id into  react['u_ids']
    for react in data['messages'][message_index].get_reacts():
        if react['react_id'] == react_id:
            react['u_ids'].append(u_id)

    return {
    }

@authorise
def message_unreact(token, message_id, react_id):
    '''
    Given a message within a channel the authorised user is part of add a "react" to that particular message
    Input format:
    (
        token: string, 
        message_id: integer, 
        react_id: integer
    )
    Output format:
    {
    }
    '''
    # find the matching user by token s
    u_id = User.get_uid_from_token(token)

    # InputError when any of:
    # message_id is not a valid message within a channel that the authorised user has joined
    # react_id is not a valid React ID. The only valid react ID the frontend has is 1
    # Message with ID message_id already contains an active React with ID react_id from the authorised user
    message_index = Message.find_message(message_id)
    if message_index == None or Channel.is_user_in_channel(u_id, data['messages'][message_index].get_channel_id()) == False or \
    react_id != 1 or Message.is_message_reacted_by_user(u_id, message_id, react_id) == False:
        raise InputError(description="Invalid Message ID or Invalid React ID")

    # Append u_id into  react['u_ids']
    for react in data['messages'][message_index].get_reacts():
        if react['react_id'] == react_id:
            react['u_ids'].remove(u_id)

    return {
    }

@authorise
def message_pin(token, message_id):
	'''
	Given a message within a channel, mark it as "pinned" to be given 
	special display treatment by the frontend
	Input format:
	(
		token: string,
		message_id: int,
	)
	Output format:
	{
	}
	'''
    # find the matching user by token s
	u_id = User.get_uid_from_token(token)
	
	message_index = Message.find_message(message_id)
	# InputError when any of:
	#   message_id is not a valid message
	#   Message with ID message_id is already pinned
	if message_index == None or data['messages'][message_index].get_is_pinned():
		raise InputError(description="Invalid Message or Already Pinned")

	# AccessError when any of:
	#   The authorised user is not a member of the channel that the message is within
	#   The authorised user is not an owner
	channel_id = data['messages'][message_index].get_channel_id()
	if Channel.is_user_in_channel(u_id, channel_id) == False or Channel.is_user_owner(u_id, channel_id) == False:
		raise AccessError(description="Not a Owner")

	# set is_pinned to be Trueqqqqqqqqq
	data['messages'][message_index].set_is_pinned(True)
	
	return {
	}

@authorise
def message_unpin(token, message_id):
	'''
	Given a message within a channel, remove it's mark as unpinned
	Input format:
	(
		token: string,
		message_id: int,
	)
	Output format:
	{
	}
	'''
    # find the matching user by token 
	u_id = User.get_uid_from_token(token)
	
	message_index = Message.find_message(message_id)
	# InputError when any of:
	#   message_id is not a valid message
	#   Message with ID message_id is already unpinned
	if message_index == None or data['messages'][message_index].get_is_pinned() == False:
		raise InputError(description="Invalid Message or Already Unpinned")

	# AccessError when any of:
	#   The authorised user is not a member of the channel that the message is within
	#   The authorised user is not an owner
	channel_id = data['messages'][message_index].get_channel_id()
	if Channel.is_user_in_channel(u_id, channel_id) == False or Channel.is_user_owner(u_id, channel_id) == False:
		raise AccessError(description="Not a Owner")
	
	# set is_pinned to be Flase
	data['messages'][message_index].set_is_pinned(False)
	
	return {
	}
