'''
Last modified on 15/11/2020
'''
from error import InputError, AccessError
from data import data, User, Channel, Message
from helper import authorise

@authorise
def channel_invite(token, channel_id, u_id):
	'''
	Input format:
	(
		token: string,
		channel_id: integer,
		u_id: integer,
	)
	Invites a user (with user id u_id) to join a channel with
	ID channel_id. Once invited the user is added to
	the channel immediately
	Output format:
	{
	}
	'''
	# find the matching user by token 
	u_id2 = User.get_uid_from_token(token)

	channel_index = Channel.find_channel(channel_id)
	user_index = User.find_user(u_id)
	# Raise InputError if channel_id does not refer to a valid channel
	if channel_index == None:
		raise InputError(description="channel_id does not refer to a valid channel")

	# Raise InputError if u_id does not refer to a valid user
	if user_index == None:
		raise InputError(description="u_id does not refer to a valid user")

	# Raise AccessError if the authorised user is not a member of the channel
	if Channel.is_user_in_channel(u_id2, channel_id) == False:
		raise AccessError(description="The user has to be a member of this channel")

	# Add the user in channel
	user = data['users'][user_index]
	user_info = {
		'u_id': u_id, 
		'name_first': user.get_name_first(), 
		'name_last': user.get_name_last(),
		'profile_img_url': user.get_profile_img_url(),
		}
	if user_info not in data['channels'][channel_index].get_all_members():
		data['channels'][channel_index].add_all_members(user_info)
	
	return {}

@authorise
def channel_details(token, channel_id):
	'''
	Input format:
	(
		token: string,
		channel_id: integer,
	)
	Given a Channel with ID channel_id that the 
	authorised user is part of, provide basic 
	details about the channel
	Output format:
	{
		'name': string,
		'owner_members': [{ u_id, name_first, name_last, profile_img_url }]
	}
	'''
	# find the matching user by token 
	u_id = User.get_uid_from_token(token)

	# Raise InputError if channel_id does not refer to a valid channel
	channel_index = Channel.find_channel(channel_id)
	if channel_index == None:
		raise InputError(description="channel_id does not refer to a valid channel")
	
	 # Raise AccessError if the authorised user is not already a member of the channel
	if Channel.is_user_in_channel(u_id, channel_id) == False:
		raise AccessError(description="The user has to be a member of this channel")

	owners = data['channels'][channel_index].get_owner_members()
	for owner in owners:
		# find the user object
		user = data['users'][owner['u_id']]
		# get the latest value
		owner['name_first'] = user.get_name_first()
		owner['name_last'] = user.get_name_last()
		owner['profile_img_url'] = user.get_profile_img_url()

	members = data['channels'][channel_index].get_all_members()
	for member in members:
		# find the user object
		user = data['users'][member['u_id']]
		# get the latest value
		member['name_first'] = user.get_name_first()
		member['name_last'] = user.get_name_last()
		member['profile_img_url'] = user.get_profile_img_url()

	return {
		'name': data['channels'][channel_index].get_name(),
		'owner_members': owners,
		'all_members': members,
	}

@authorise
def channel_messages(token, channel_id, start):
	'''
	Input format:
	(
		token: string,
		channel_id: integer,
		start: integer,
	)
	Given a Channel with ID channel_id that the authorised user is part of, 
	return up to 50 messages between index "start" and "start + 50". 
	Message with index 0 is the most recent message in the channel. 
	This function returns a new index "end" which is the value of "start + 50", or, 
	if this function has returned the least recent messages in the channel, returns -1 
	in "end" to indicate there are no more messages to load after this return.
	Output format:
	{
		'messages': [{ message_id, u_id, message, time_created, reacts, is_pinned }]],
		'start': integer,
		'end': integer,	
	}
	'''
	# find the matching user by token 
	u_id = User.get_uid_from_token(token)

	channel_index = Channel.find_channel(channel_id)
	# raise InputError if channel ID is not a valid channel
	if channel_index == None:
		raise InputError(description="channel_id does not refer to a valid channel")

	# use a list to collect messages in the channel
	_messages_in_channel = []
	for message in data['messages']:
		if message.get_channel_id() == channel_id:
			new_message = {
				'message_id': message.get_message_id(), 
				'u_id': message.get_u_id(), 
				'message': message.get_message(), 
				'time_created': message.get_time_created(),
				'reacts': message.get_reacts(),
				'is_pinned': message.get_is_pinned(),
			}
			i = 0
			for react in new_message['reacts']:
				if Message.is_message_reacted_by_user(u_id, new_message['message_id'], react['react_id']):
					new_message['reacts'][i]['is_this_user_reacted'] = True
				else:
					new_message['reacts'][i]['is_this_user_reacted'] = False
				i += 1
			_messages_in_channel.append(new_message)

	messages_in_channel = sorted(_messages_in_channel ,key = lambda e:e.__getitem__('time_created'))
	# raise InputError if start is greater than the total number of messages in the channel
	if start > len(messages_in_channel):
		raise InputError(description="start is greater than the number of messages")

	u_id = User.get_uid_from_token(token)
	# raise AccessError if Authorised user is not a member of channel with channel_id
	if Channel.is_user_in_channel(u_id, channel_id) == False:
		raise AccessError(description="The user has to be a member of this channel")

	messages = []
	for message in messages_in_channel:
		if (message['message'] != ''):
			messages.insert(0, message)

	# Set end to 1 to indicate there are no more messages to load after this return.
	end = start + 50
	if end >= len(messages):
		end = -1

	return {
		'messages': messages[start:start+50],
		'start': start,
		'end': end,
	}

@authorise
def channel_leave(token, channel_id):
	'''
	Input format:
	(
		token: string,
		channel_id: integer,
	)
	Given a channel ID, the user removed as a member of this channel
	Output format:
	{
	}
	'''
	# find the matching user by token 
	u_id = User.get_uid_from_token(token)

	channel_index = Channel.find_channel(channel_id)
	# raise InputError if channel ID is not a valid channel
	if channel_index == None:
		raise InputError(description="channel ID does not refer a valid channel")

	u_id = User.get_uid_from_token(token)
	# raise AccessError if Authorised user is not a member of channel with channel_id
	if Channel.is_user_in_channel(u_id, channel_id) == False:
		raise AccessError(description="The user has to be a member of this channel")

	for member in data['channels'][channel_index].get_all_members():
		if u_id == member['u_id']:
			data['channels'][channel_index].remove_all_members(member)

	for member in data['channels'][channel_index].get_owner_members():
		if u_id == member['u_id']:
			data['channels'][channel_index].remove_owner_members(member)

	return {}

@authorise
def channel_join(token, channel_id):
	'''
	Input format:
	(
		token: string,
		channel_id: integer,
	)
	Given a channel_id of a channel that the authorised 
	user can join, adds them to that channel
	Output format:
	{
	}
	'''
	# find the matching user by token 
	u_id = User.get_uid_from_token(token)

	index = Channel.find_channel(channel_id)
	user_index = User.find_user(u_id)
	# raise InputError if channel ID is not a valid channel
	if index == None:
		raise InputError(description="channel_id does not refer a valid channel")
	# raise AccessError if channel_id refers to a channel that is private 
	# (when the authorised user is not a global owner)
	if not data['channels'][index].get_is_public() and data['users'][user_index].get_permission_id() != 1:
		raise AccessError(description="Channel that is private")

	user_index = User.find_user(u_id)
	user = data['users'][user_index]
	user_info = {
		'u_id': u_id, 
		'name_first': user.get_name_first(), 
		'name_last':user.get_name_last(),
		'profile_img_url': user.get_profile_img_url(),
	}
	if user_info not in data['channels'][index].get_all_members():
		data['channels'][index].add_all_members(user_info)
	return {}

@authorise
def channel_addowner(token, channel_id, u_id):
	'''
	Input format:
	(
		token: string,
		channel_id: integer,
		u_id: integer,
	)
	Make user with user id u_id an owner of this channel
	Output format:
	{
	}
	'''
	# find the matching user by token s
	u_id2 = User.get_uid_from_token(token)

	channel_index = Channel.find_channel(channel_id)
	# raise InputError if channel ID is not a valid channel
	if channel_index == None:
		raise InputError(description="channel_id does not refer a valid channel")
	
	# raise InputError if user with user id u_id is already an owner of the channel
	if Channel.is_user_owner(u_id, channel_id) == True:
		raise InputError(description="The user is already an owner of the channel") 

	user_index = User.find_user(u_id)
	# raise InputError if the u_id is not valid(assumptions)
	if user_index == None:
		raise InputError(description="Invalid u_id")    

	# raise AccessError when the authorised user is not an owner of the flockr, or an owner of this channel
	user_index2 = User.find_user(u_id2)
	if Channel.is_user_owner(u_id2, channel_id) == False and data['users'][user_index2].get_permission_id() != 1:
		raise AccessError(description="You are not the owner of the channel or the flockr")

	user_index = User.find_user(u_id)
	user = data['users'][user_index]
	user_info = {
		'u_id': u_id, 
		'name_first': user.get_name_first(), 
		'name_last':user.get_name_last(),
		'profile_img_url': user.get_profile_img_url(),
	}
	channel_index = Channel.find_channel(channel_id)

	
	data['channels'][channel_index].add_owner_members(user_info)
	if user_info not in data['channels'][channel_index].get_all_members():
		data['channels'][channel_index].add_all_members(user_info)

	return {}

@authorise
def channel_removeowner(token, channel_id, u_id):
	'''
	Input format:
	(
		token: string,
		channel_id: integer,
		u_id: integer,
	)
	Remove user with user id u_id an owner of this channel
	Output format:
	{
	}
	'''
	# find the matching user by token 
	u_id2 = User.get_uid_from_token(token)
	
	channel_index = Channel.find_channel(channel_id)
	# raise InputError if channel ID is not a valid channel
	if channel_index == None:
		raise InputError(description="channel_id does not refer a valid channel")
	
	user_index = User.find_user(u_id)
	# raise InputError if the u_id is not valid(assumptions)
	if user_index == None:
		raise InputError(description="Invalid u_id")               

	# raise InputError if user with user id u_id is already an owner of the channel
	if Channel.is_user_owner(u_id, channel_id) == False:
		raise InputError(description="The user is already an owner of the flockr")   

	# raise AccessError when the authorised user is not an owner of the flockr, or an owner of this channel
	u_id2 = User.get_uid_from_token(token)
	user_index2 = User.find_user(u_id2)
	if Channel.is_user_owner(u_id2, channel_id) == False and data['users'][user_index2].get_permission_id() != 1:
		raise AccessError(description="You are not the owner of the channel or the flockr")

	channel_index = Channel.find_channel(channel_id)
   
	user_info = {
		'u_id': u_id, 
		'name_first': data['users'][user_index].get_name_first(),
		'name_last': data['users'][user_index].get_name_last(),
		'profile_img_url': data['users'][user_index].get_profile_img_url(),
	}

	data['channels'][channel_index].remove_owner_members(user_info)
	return {}
