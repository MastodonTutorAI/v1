import bcrypt    
def hash_password(password):
    """
    Hashes a password using bcrypt.
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

print(hash_password('student'))