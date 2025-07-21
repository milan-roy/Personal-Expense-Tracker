import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(entered_password,hashed_password):
    return bcrypt.checkpw(entered_password.encode(), hashed_password.encode())
