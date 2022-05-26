from data import data, User, Message
from helper import get_uid_from_token, find_user, authorise
from error import InputError, AccessError

def clear():
	'''
	Resets the internal data of the application to 
	it's initial state
	Input format:
    ()
    Output format:
    {}
	'''
	data['users'].clear()
	data['channels'].clear()
	data['messages'].clear()
	data['valid_tokens'].clear()
	return {}

@authorise
def users_all(token):
	'''
	Returns a list of all users and their associated details
	Input format:
    (
        token: string,
    )
    Output format:
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
	users_detail = []
	for datum in data['users']:
		datum_detail = {}
		datum_detail['u_id'] = datum.get_u_id()
		datum_detail['email'] = datum.get_email()
		datum_detail['name_first'] = datum.get_name_first()
		datum_detail['name_last'] = datum.get_name_last()
		datum_detail['handle_str'] = datum.get_handle_str()
		datum_detail['profile_img_url'] = datum.get_profile_img_url()
		users_detail.append(datum_detail)
	return {
		'users': users_detail,
	}

@authorise
def admin_userpermission_change(token, u_id, permission_id):
	'''
	Given a User by their user ID, set their permissions to new permissions 
	described by permission_id
	Input format:
    (
        token: string,
		u_id: integer,
		permission_id: integer,
    )
    Output format:
    {}

	'''
	# find the matching user by token 
	user_index = User.find_user(u_id)
	if user_index == None:
		raise InputError(description="Invalid u_id")

	u_id2 = User.get_uid_from_token(token)
	user_index2 = User.find_user(u_id2)	

	Owner_permission = 1

	if permission_id not in range(1, 3):
		raise InputError(description="Invalid permission_id")

	if data['users'][user_index2].get_permission_id() is not Owner_permission:
		raise AccessError(description="Authorised user is not an owner")

	
	data['users'][u_id].set_permission_id(permission_id)
	return {}

@authorise
def search(token, query_str):
	'''
	Given a query string, return a collection of messages in all 
	of the channels that the user has joined that match the query
	Input format:
    (
        token: string,
		query_str: string,
    )
    Output format:
    {
		message: {
			message_id: integer,
			u_id: integer,
			message: string,
			time_created: integer,
			reacts: integer,
			is_pinned: boolean,
		}
    }
	'''
	# this function will return 'message', a list of dictionaries
	# create a new list to store the result
	message_results = {'messages':[]}

	u_id = User.get_uid_from_token(token)

	# find all the channel_id that the authorised user is in and 
	# collect them in a new list
	channel_id_list = []
	for channel in data['channels']:
		for find_uid_channel in channel.get_all_members():
			if u_id == find_uid_channel['u_id']:
				channel_id_list.append(channel.get_channel_id())
	
	# search through all the messages in the channels of the authorised 
	# user to find the correct message and put them in a new dictionary
	for _channel in channel_id_list:
		for message in data['messages']:
			if _channel == message.get_channel_id():
				mess_str = message.get_message()
				check_str = query_str
				if check_str in mess_str:
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
					message_results['messages'].append(new_message)
	return message_results

