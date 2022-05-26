'''
data = {
    'users': [
        {
            'u_id' : integer,
            'email' : string,
            'password' : string,
            'name_first': string,
            'name_last': string,
            'handle_str': string,
            'permission_id': integer,
        }
    ],
    'channels': [
        {
            'name':string,
            'id':integer,
            'all_members':[{'u_id': integer, 'name_first': string, 'name_last': string}],
            'owner_members':[{'u_id': integer, 'name_first': string, 'name_last': string}],
            'is_public': boolean,
        }
    ],
    'messages': [
        {
            'message_id': integer, 
            'u_id': integer, 
            'message': string, 
            'channel_id': integer,
            'time_created': double,
        }
    ],
    'valid_tokens': [],

}
'''
import re
import hashlib
import jwt
from error import InputError

SECRET = 'spicythingy'


data = {
    'users': [],
    'channels': [],
    'messages': [],
    'valid_tokens': [],
}

class User(object):
    """
    new_user = {
        'u_id' : integer,
        'email' : string,
        'password' : string,
        'name_first': string,
        'name_last': string,
        'handle_str': string
        'permission_id': integer,
        'reset_code': string
    }
    """
    def __init__(self, u_id=None, email=None, password=None, name_first=None, 
    name_last=None, handle_str=None, permission_id=None, reset_code=None, profile_img_url=None):
        self.u_id = u_id
        self.email = email
        self.password = password
        self.name_first = name_first
        self.name_last = name_last
        self.handle_str = handle_str
        self.permission_id = permission_id
        self.reset_code = reset_code
        if profile_img_url is None:
            self.profile_img_url = ''

    def set_u_id(self, u_id):
        '''
        Replace the u_id by the passed in u_id
        '''
        self.u_id = u_id

    def get_u_id(self):
        '''
        Return the u_id of the object
        '''
        return self.u_id
    
    def set_email(self, email):
        '''
        Replace the email by the passed in email
        '''
        self.email = email

    def get_email(self):
        '''
        Return the email of the object
        '''
        return self.email

    def set_password(self, password):
        '''
        Replace the password by the passed in password
        '''
        self.password = password

    def get_password(self):
        '''
        Return the password of the object
        '''
        return self.password

    def set_name_first(self, name_first):
        '''
        Replace the name_first by the passed in name_first
        '''
        self.name_first = name_first

    def get_name_first(self):
        '''
        Return the name_first of the object
        '''
        return self.name_first

    def set_name_last(self, name_last):
        '''
        Replace the name_last by the passed in name_last
        '''
        self.name_last = name_last

    def get_name_last(self):
        '''
        Return the name_last of the object
        '''
        return self.name_last

    def set_handle_str(self, handle_str):
        '''
        Replace the handle_str by the passed in handle_str
        '''
        self.handle_str = handle_str
    
    def get_handle_str(self):
        '''
        Return the handle_str of the object
        '''
        return self.handle_str

    def set_permission_id(self, permission_id):
        '''
        Replace the permission_id by the passed in permission_id
        '''
        self.permission_id = permission_id
    
    def get_permission_id(self):
        '''
        Return the permission_id of the object
        '''
        return self.permission_id
    
    def set_reset_code(self, reset_code):
        '''
        Replace the reset_code by the passed in reset_code
        '''
        self.reset_code = reset_code
    
    def get_reset_code(self):
        '''
        Return the reset_code of the object
        '''
        return self.reset_code
    
    def get_profile_img_url(self):
        '''
        Return the profile_img_url of the object
        '''
        return self.profile_img_url

    def set_profile_img_url(self, profile_img_url):
        '''
        Replace the profile_img_url by the passed in profile_img_url
        '''
        self.profile_img_url = profile_img_url


    @staticmethod
    def check_name_first(name):
        '''
        check if the name is between 1 and 50 characters.
        '''
        # check if the first name is empty
        if name == '':
            raise InputError(description='Invalid first name: less than 1 character')

        # check if the first name is too long
        if len(name) > 50:
            raise InputError(description='Invalid first name: more than 50 characters')

    @staticmethod
    def check_name_last(name):
        '''
        check if the name is between 1 and 50 characters.
        '''
        # check if the last name is empty
        if name == '':
            raise InputError(description='Invalid last name: less than 1 character')

        # check if the last name is too long
        if len(name) > 50:
            raise InputError(description='Invalid last name: more than 50 characters')

    @staticmethod
    def check_email_format(email):
        '''
        An InputError will be raised if the passed in email has an invalid format.
        '''
        regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if re.search(regex, email) is None:
            raise InputError(description='Invalid Email Format')

    @staticmethod
    def check_email_repeated(email):
        '''
        An input error will be raised if the passed in email is already existing
        '''
        # check if the email has been used for previous registration
        is_repeated_email = False
        for user in data['users']:
            if email == user.get_email():
                is_repeated_email = True
                break
        if is_repeated_email:
            raise InputError(description='Used Email Address')

    @staticmethod
    def check_password(password):
        '''
        An InputError will be raised if the passed password is invalid
        '''
        # check if the password is less than 6 characters long
        if len(password) < 6:
            raise InputError(description='Invalid Password: less than 6 characters')
    
    @staticmethod
    def check_handle(handle_str):
        '''
        An InputError will be raised if the password handle is invalid
        '''
        # check if the handle is between 3 and 20 characters
        if len(handle_str) > 20 or len(handle_str) < 3:
            raise InputError(description="Invalid handle format, plesae make sure it is between 3 and 20 characters")
        
        # check that the handle does not already exist
        for user in data['users']:
            if handle_str == user.get_handle_str():
                raise InputError(description="Used hanlde")
    
    @staticmethod
    def check_resetcode_is_unique(reset_code):
        '''
        An InputError is raised if the passed in reset_code has been used for other users
        '''
        for user in data['users']:
            if reset_code == user.get_reset_code():
                raise InputError(description='Email is not unique')

    @staticmethod
    def find_user(u_id):
        '''
        Return the index of the user whose u_id matches the passed in
        u_id. None will be returned if it is not found.
        '''
        index = None
        i = 0
        for user in data['users']:
            if u_id == user.get_u_id():
                index = i
                break
            i += 1

        return index

    @staticmethod
    def encrypt_password(password):
        '''
        Return the hashsed password string.
        '''
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def generate_token(u_id):
        '''
        Return the token generated based on the passed in u_id.
        If the token does not exist, add it to the valid_tokens list
        The payload:
        {
            "u_id": integer,
        }
        '''
        payload = {
            "u_id": u_id,
        }
        token = jwt.encode(payload, SECRET, algorithm='HS256').decode('utf-8')
        if token not in data['valid_tokens']:
            data['valid_tokens'].append(token)
        return token
    
    @staticmethod
    def get_uid_from_token(token):
        '''
        Return the u_id decoded from the passed in token.
        If the token is not in the valid_tokens list, return None.
        If the u_id does not exist, return None.
        '''
        if token not in data['valid_tokens']:
            return None
        payload = jwt.decode(token.encode('utf-8'), SECRET, algorithms=['HS256'])
        if User.find_user(payload['u_id']) is None:
            return None
        else:
            return payload['u_id']
            
    @staticmethod
    def invalidate_token(token):
        '''
        Assumes the token passed in is valid
        Remove the token from the valid_tokens list
        '''
        data['valid_tokens'].remove(token)


    @staticmethod
    def generate_handle(name_first, name_last):
        '''
        A handle is generated that is the concatentation of a lowercase-only first name and last name. 
        If the concatenation is longer than 20 characters, it is cutoff at 20 characters. 
        If the handle is already taken, it is modified by appending a number to make it unique.
        '''
    
        name_string = name_first.lower() + name_last.lower()
        if len(name_string) > 20:
            name_string = name_string[0:20]

        for user in data['users']:
            if name_string == user.get_handle_str():     # repetative string
                # check if there is a number in the string already
                if not name_string.isdigit() and not name_string.isalpha():
                    for index, ch in enumerate(name_string):
                        if '0' <= ch <= '9': # the first number is reached
                            num = int(name_string[index:]) + 1
        
                            name_string = name_string[:index]
                            if len(name_string) + len(str(num)) > 20:
                                name_string = name_string[:20 - len(str(num))] + str(num)
                            else:
                                name_string += str(num)
                            # break
                else:
                    num = 0
                    name_string = name_string[:20 - len(str(num))] + str(num)

        return name_string

class Channel(object):
    '''
    'new_channel': {
            'name':string,
            'channel_id':integer,
            'all_members':[{'u_id': integer, 'name_first': string, 'name_last': string}],
            'owner_members':[{'u_id': integer, 'name_first': string, 'name_last': string}],
            'is_public': boolean,
            'time_finish': integer
    }
    '''
    def __init__(self, name=None, channel_id=None, all_members=None,
                owner_members=None, is_public=None, time_finish=None):
        self.name = name
        self.channel_id = channel_id
        self.all_members = all_members
        self.owner_members = owner_members
        self.is_public = is_public
        self.time_finish = time_finish
        self.standup_message = ''
    def set_name(self, name):
        '''
        Replace the name by the passed in name
        '''
        self.name = name

    def get_name(self):
        '''
        Return the name of the object
        '''
        return self.name

    def set_channel_id(self, channel_id):
        '''
        Replace the channel_id by the passed in channel_id
        '''
        self.channel_id = channel_id

    def get_channel_id(self):
        '''
        Return the channel_id of the object
        '''
        return self.channel_id
    
    def set_all_members(self, all_members):
        '''
        Replace the all_numbers by the passed in all_numbers
        '''
        self.all_members = all_members

    def get_all_members(self):
        '''
        Return the all_numbers of the object
        '''
        return self.all_members

    def set_owner_members(self, owner_members):
        '''
        Replace the owner_members by the passed in name
        '''
        self.owner_members = owner_members

    def get_owner_members(self):
        '''
        Return the owner_members of the object
        '''
        return self.owner_members

    def set_is_public(self, is_public):
        '''
        Replace the is_public by the passed in name
        '''
        self.is_public = is_public

    def get_is_public(self):
        '''
        Return the is_public of the object
        '''
        return self.is_public

    def add_all_members(self, user):
        '''
        add the channel.all_members
        '''
        self.all_members.append(user)

    def add_owner_members(self, user):
        '''
        add the channel.owner_members
        '''
        self.owner_members.append(user)

    def remove_all_members(self, user):
        '''
        remove the channel.all_members
        '''
        self.all_members.remove(user)

    def remove_owner_members(self, user):
        '''
        remove the channel.owner_members
        '''
        self.owner_members.remove(user)
    
    def set_time_finish(self, time_finish):
        '''
        add the channel.time_finish
        '''
        self.time_finish = time_finish
    def get_time_finish(self):
        '''
        Return the time_finish of the object
        '''
        return self.time_finish

    def set_standup_message(self, message):
        '''
        set the standup_message of the object
        '''
        self.standup_message = message
    def get_standup_message(self):
        '''
        Return the standup_message of the object
        '''
        return self.standup_message

    def standup_message_append(self, new_message):
        '''
        Append the new passed in message to the existing messgae
        '''
        self.standup_message += new_message
    
    @staticmethod
    def find_channel(channel_id):
        '''
        Return the index of the channel whose channel_id matches the passed in
        channel_id. None will be returned if it is not found.
        '''
        index = None
        i = 0
        for channel in data['channels']:
            if channel.get_channel_id() == channel_id:
                index = i
                break
            i += 1
        return index

    @staticmethod
    def is_user_in_channel(u_id, channel_id):
        '''
        Check if the user with the passed in u_id is a member of the channel
        with the passed in channel_id.
        '''
        index = Channel.find_channel(channel_id)
        channel = data['channels'][index]
        all_members = channel.get_all_members()
        for member in all_members:
            if u_id == member['u_id']:
                return True

        return False

    @staticmethod
    def is_user_owner(u_id, channel_id):
        '''
        Check if the user with the passed in u_id is an owner of the channel
        with the passed in channel_id.
        '''
        index = Channel.find_channel(channel_id)
        channel = data['channels'][index]
        owner_members = channel.get_owner_members()
        for member in owner_members:
            if u_id == member['u_id']:
                return True

        return False

    @staticmethod
    def standup_send_final_message(channel, message_detail):
        message = channel.get_standup_message()
        message_detail.set_message(message)
        channel.set_standup_message('')

class Message(object):
    '''
    'messages': [
        {
            'message_id': integer, 
            'u_id': integer, 
            'message': string, 
            'channel_id': integer,
            'time_created': double,
        }
    ],
    '''
    def __init__(self, message_id=None, u_id=None, message=None, channel_id=None, time_created=None, reacts=None, is_pinned=None):
        self.message_id = message_id
        self.u_id = u_id
        self.message = message
        self.channel_id = channel_id
        self.time_created = time_created
        self.reacts = reacts
        self.is_pinned = is_pinned

    def set_message_id(self, message_id):
        '''
        Replace the message_id by the passed in message_id
        '''
        self.message_id = message_id

    def set_u_id(self, u_id):
        '''
        Replace the u_id by the passed in u_id
        '''
        self.u_id = u_id

    def set_message(self, message):
        '''
        Replace the message by the passed in message
        '''
        self.message = message
        
    def set_channel_id(self, channel_id):
        '''
        Replace the channel_id by the passed in channel_id
        '''
        self.channel_id = channel_id

    def set_time_created(self, time_created):
        '''
        Replace the time_created by the passed in time_created
        '''
        self.time_created = time_created

    def set_reacts(self, reacts):
        '''
        Replace the reacts by the passed in time_created
        '''
        self.reacts = reacts

    def set_is_pinned(self, is_pinned):
        '''
        Replace the is_pinned by the passed in time_created
        '''
        self.is_pinned = is_pinned

    def get_message_id(self):
        '''
        Return the message_id of the object
        '''
        return self.message_id

    def get_u_id(self):
        '''
        Return the u_id of the object
        '''
        return self.u_id

    def get_message(self):
        '''
        Return the message of the object
        '''
        return self.message
        
    def get_channel_id(self):
        '''
        Return the channel_id of the object
        '''
        return self.channel_id

    def get_time_created(self):
        '''
        Return the time_created of the object
        '''
        return self.time_created

    def get_reacts(self):
        '''
        Return the reacts of the objec
        '''
        return self.reacts

    def get_is_pinned(self):
        '''
        Return the is_pinned of the objec
        '''
        return self.is_pinned

    @staticmethod    
    def find_message(message_id):
        '''
        Return the index of the message whose message_id matches the passed in
        message_id. None will be returned if it is not found.
        '''
        index = None
        i = 0
        for message in data['messages']:
            if message.get_message_id() == message_id:
                index = i
                break
            i += 1
        return index

    @staticmethod    
    def is_message_reacted_by_user(u_id, message_id, react_id):
        '''
        Check if the message is already reacted by the authorised user
        '''
        message_index = Message.find_message(message_id)
        for react in data['messages'][message_index].get_reacts():
            if react['react_id'] == react_id:
                for _u_id in react['u_ids']:
                    if _u_id == u_id:
                        return True
        
        return False

    @staticmethod   
    def modify_message(_message, message):
        _message.set_message(message)
