from error import InputError, AccessError
from data import data, User, Channel 
from helper import authorise

@authorise
def channels_list(token):
	'''
	Input format:
	(
		token: string,
	)
	list the channels that contains the given user
	Output format:
	{
		channels: [{ channel_id, name }]
	}
	'''

	# find the matching user by token 
	u_id = User.get_uid_from_token(token)

	# create an empty list to store the result
	all = []

	# search through all the channels for the required ones
	for channel in data['channels']:
		if Channel.is_user_in_channel(u_id, channel.get_channel_id()) == True:
			channel_info = {}
			channel_info['channel_id'] = channel.get_channel_id()
			channel_info['name'] = channel.get_name()

			# put the found channels at the tail of the result list
			all.append(channel_info)

	return {'channels': all}

@authorise
def channels_listall(token):
	'''
	Input format:
	(
		token: string,
	)
	list all the channels
	Output format:
	{
		channels: [{ channel_id, name }]
	}
	'''
	# create an empty list to store the result
	all = []

	# get the information of all the channels 
	for channel in data['channels']:
		channel_info = {}
		channel_info['channel_id'] = channel.get_channel_id()
		channel_info['name'] = channel.get_name()
		all.append(channel_info)

	# put the found channels at the tail of the result list
	return {'channels': all}

@authorise
def channels_create(token, name, is_public):
	'''
	Input format:
	(
		token: string,
		name: string,
		is_public: boolean,
	)
	create a new channel
	Output format:
	{
		channel_id: interger,
	}
	'''
	# find the matching user by token 
	u_id = User.get_uid_from_token(token)

	# name must be less or equal to 20 cahracters
	if len(name) >= 20:
		raise InputError(description="Invalid Name")

	# create a new empty channel Class    
	new_channel = Channel()

	# set attributes
	new_channel.set_name(name)
	new_channel.set_channel_id(len(data['channels']))
	new_channel.set_all_members([])
	new_channel.set_owner_members([])
	new_channel.set_is_public(is_public)

	# find the information of the owner
	user_index = User.find_user(u_id)
	user = data['users'][user_index]

	# add the information of the user to this channel
	user_info = {
		'u_id': user.get_u_id(), 
		'name_first': user.get_name_first(), 
		'name_last': user.get_name_last(),
		'profile_img_url': user.get_profile_img_url(),
	}
	new_channel.add_owner_members(user_info)
	new_channel.add_all_members(user_info)

	data['channels'].append(new_channel)

	# return channel_id
	return {
		'channel_id': new_channel.get_channel_id(),
	}
