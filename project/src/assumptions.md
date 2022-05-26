# General Assumptions

- `u_id`,  `channel_id`  and `message_id`  are non-negative integers starting from 0.

- Names of users and channels are not required to be unique.

- The first name and last name of an user are not allowed to contain any numbers.

    e.g., `Shrek2` is an invalid first name.

- All the arguments passed in to the functions are assumed not None.

- The encrypting system used to store password is `hashlib.sha256()`
    - The passords are all stored as hashed strings.
    - This is a one-way function, meaning that there is no mechanism to regain the password from the hashed string.
    - Therefore the user is not able to request for seeing the password if they've forgot it.
    
- The token is generated based on the` jwt` system. Where the algorithm is `'HS256'` and the encoding function `'utf-8'`.
    - The secrete key `spicythingy` is kept unchanged throughout the whole program. Therefore the token will be the same for each `u_id` regardless of the number of times that this token has been created.
    - The token is considered as invalid when either one of the followings is true:
        - The format of the token string is invalid and cannot be decoded by `jwt`.
        - The `u_id` encoded in this token does not match to any existing users.
        - The token is not found in the database where to store all the valid token strings.

## General assumptions in Iteration 1 only

- The data generated does not persist. 
- Token is an integer with the same value as the u_id

## General assumptions in Iteration 2 only

- The data generated does not persist. 



# auth.py

- Tokens returned from auth_register and auth_login for the same user are identical.
- When the user is logged in again after being logged out, the already invalidated token will be considered as valid again.
  
    - This is done by regenerating the same token for each `u_id`.
- The `u_id` of an user is not allowed to be changed once the user is registered. There is no mechanism to delete a `u_id` so all the users will have a unique `u_id` in the chromological order of the registration time (an integer starting from 0). e.g.,

    ```shell
    u_id		registration
    0			1st
    1			2nd
    2			3rd
    3			4th
    ...
    10000		9999th
    ```

## auth_register

- A user that has been registered through auth_register will automatically be logged in.


- If the handle is already taken, it is modified by appending a number to make it unique where this number increments from 1. Therefore the number being appended equals the number of repeats of this concatentation. e.g.

    ```python
    "firstlast" 	# first ocurrence
    "firstlast1"	# first repeat
    "firstlast2"	# secoud repeat
    "firstlast3"	# third repeat
    ```

- A number will only be appended to a string to make it unique if the overall length after this modification is still <= 20. Otherwise, the last few characters of the string will be replaced an integer. e.g., if the string `aaaaabbbbbcccccddddd` has appeared once, then to make the new incoming `aaaaabbbbbcccccddddd` unique, the new incoming string will be `aaaaabbbbbcccccdddd0` with the last character `d` being replaced by the integer `0`. If `aaaaabbbbbcccccddddd` has appeared for 5 times, then the new incoming string (the 6th one) will be modified to `aaaaabbbbbcccccdddd4`. If `aaaaabbbbbcccccddddd` has appeared for 11 times, then the new incoming string (the 12th one) will be modified to `aaaaabbbbbcccccddd10`. In this case, it is assumed that the number of repeated concatentations will not exceeds $2^{20}$ (otherwise there will be insufficient number of digits to represent different `handle_str`).

    ```python
    "aaaaabbbbbcccccddddd"
    "aaaaabbbbbcccccdddd0"
    "aaaaabbbbbcccccdddd1"
    "aaaaabbbbbcccccdddd2"
    "aaaaabbbbbcccccdddd3"
    ...
    "aaaaabbbbbcccccddd10"
    "aaaaabbbbbcccccddd11"
    "aaaaabbbbbcccccddd12"
    ```

## auth_login

- Logging in after registration will not make any difference and will simply return the already existed token and u_id of the user. No error will be raised in this case.

- There is no mechanism to check if a user has been logged in already in order to stop the user from logging in twice in a row (without being logged out in the middle). Therefore, a user can be logged in multiple times with no extra token generated. This means that there will always be no more than one token being considered `valid` for the same user.


## auth_logout

- `auth_logout` returns `{'is_success': False}` if the `u_id` obtained from the `token` passed in is invalid or does not match to any existing user.
- To logout an user, it simply means to invalidate the token of this user. An `AccessError` will be raised if anyone is attempting to use this invalid token (originally valid) to access anything (i.e., to call any function that requires a token)
- When the user is logged in again, the same token will be considered valid again. This is because the way to generate token in this case only depends on the `u_id` of the user (while the header and the secrete key is unchanged).
- When trying to log out a user who has already been logged out, `{'is_success': False}` will be returned.

## auth_passwordreset_request

- `auth_passwordreset_request` returns an InputError when the email given is not a string or isn't a registered user in `data['users']`

# channel.py

## General assumptions in channel.py

- An owner of a channel is automatically considered as a member of this channel.

## channel_invite

- Inviting a user who is already in this channel will do nothing.

## channel_join

- it will not do anything if the user is already in the channel.

## channel_addowner

- The new owner added does not have to be in the channel. This user will become both a member and an owner of this channel simultaneously when `channel_addowner` is called.
- InputError will be raised if the `u_id` passed in is invalid.

## channel_remove_owner

- It will raise InputError if the `u_id` passed in is invalid.
- Owners can remove themselves.



# channels.py

## channels_create

- The name of a channel can be an empty string.
- The user who creates the channel will be automatically set to be the owner.



# user.py

- If an identical email/handle is passed into user_profile_setemail or user_profile_sethandle to the original email/handle, InputError will be raised.
- Repeated names will not raise an InputError (Even if the new name is identical to this user's original name).
- When the name is changed using user_profile_setname, the handle for the user with the changed name will not be affected.
- The system assumes the user always passes in the arguments for uploading photo correctly. i.e., it assumes that `(token, img_url, x_start, y_start, x_end, y_end)` are passed in successfully and none of them has the value `None`.



# message.py

## message_send

- It will raises InputError if user wants to send message which is an empty string.

## message_remove

- A removed message is an empty string.
- Even if a message was removed, it's message_id still exists.

## message_edit

- It will raise InputError if the message no long exists, that is, the message_id
is invalid or it's empty string which means it has been removed.




# Standup
- If an user is not a member of a channel and is willing to start an active standup or check if there is an active standup in this channel, and `AccessError` will be raised.
- The final message sent by `standup_send` as a summary is allowed to exceed the 1000 character limits. However, each message sent during the standup period are still restricted by the 1000 characters limits.

