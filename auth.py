import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Hash the password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Verify the password
def verify_password(stored_password, input_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), stored_password.encode('utf-8'))

# Generate JWT Token
def generate_jwt(user_id, email):
    expiration = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode({
        'user_id': user_id,  # hna ghadi tkhdm b type d data li khdemtiha d
        'email': email,      # ghay khassek tbeddel les variables d les fonctions tahuma bach i koun dekchi compatible 
        'exp': expiration
    }, os.getenv('JWT_SECRET'), algorithm='HS256')
    return token
