import string
import typing

PASSWORD_MIN = 10
PASSWORD_MAX = 64
USERNAME_MIN = 3
USERNAME_MAX = 64
NAME_MIN = 3
NAME_MAX = 64

PASSWORD_CHARS = set(string.digits + string.ascii_lowercase + string.ascii_uppercase + "~`!@#$%^&*()_-+={[}]|\\:;\"\'<,>.?/")
USERNAME_CHARS = set(string.digits + string.ascii_lowercase + string.ascii_uppercase + "_-")
NAME_CHARS = set(string.digits + string.ascii_lowercase + string.ascii_uppercase + " ")

def verify_password(password : str) -> bool:
    if not (PASSWORD_MIN < len(password) < PASSWORD_MAX):
        return False

    if not set(password).issubset(PASSWORD_CHARS):
        return False

    return True

def verify_username(username : str) -> bool:
    if not (USERNAME_MIN < len(username) < USERNAME_MAX):
        return False

    if not set(username).issubset(USERNAME_CHARS):
        return False

    return True

def verify_name(name : str) -> bool:
    if not (NAME_MIN < len(name) < NAME_MAX):
        return False

    if not set(name).issubset(NAME_CHARS):
        return False

    return True

# check fields all in 
def verify_form(data : dict, fields : typing.List[str]) -> bool:
    has_fields = set(data.keys()).issuperset(set(fields))
    has_none = any(data.values()) is None

    return has_fields and not has_none