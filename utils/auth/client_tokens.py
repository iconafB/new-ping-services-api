import secrets
import hashlib

def  generate_secure_token(length_bytes:int=32)->str:
    
    return secrets.token_urlsafe(length_bytes)

def hash_token(token:str):

    return hashlib.sha256(token.encode("utf-8")).hexdigest()