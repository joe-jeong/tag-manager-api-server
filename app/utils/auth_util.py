import random
import string
from app.model.user import User

def generate_user_code():
    is_duplicated = True
    while is_duplicated:
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        is_duplicated = True if User.get_by_code(code) else False
    return code