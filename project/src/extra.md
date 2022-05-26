# Object-Oriented Programming

**We created three classes:**

- `User`
- `Channel`
- `Message`

**Major changed features:**

1. The information of an user/channel/message is all stored in object instead of dictionaries.

2. An object can be created either with or without doing any initialisation (by the `__init__` method).  The unitialised attributes can be initialised by calling the set functions.

    ```python
    user.set_profile_img_url(url) # an example of where the initialisation when create an User object is impossible, which can be done intuitively by using a set function
    ```

3. Attributes of an object cannot be directly accessed, but a get function should be called. e.g.,

    ```python
    # Return the user profile
    return {
        'user': {
            'u_id': u_id,
            'email': user.get_email(),
            'name_first': user.get_name_first(),
            'name_last': user.get_name_last(),
            'handle_str': user.get_handle_str(),
            'profile_img_url': user.get_profile_img_url(),
        },
    }
    ```

4. The majority of helper functions initially placed in `helper.py` are modified to become **static methods** of the corresponding class. 

    - e.g., the function get_uid_from_token was initially called in `auth.py` by the following way

        ```python
        u_id = helper.get_uid_from_token(token)
        ```

    - It is now changed to:

        ```python
        u_id = User.get_uid_from_token(token)
        ```

    - The code for the static method:

        ```python
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
        
        ```

    - This function is determined to be modified to a static method since it is related to the User class but does not require an object to be created first. 

