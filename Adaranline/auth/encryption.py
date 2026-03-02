from werkzeug.security import generate_password_hash,check_password_hash
def encrypt_password(password: str) -> str:
    return generate_password_hash(password)
def verify_password(hashed_pass: str, password: str) -> bool:
    return check_password_hash(hashed_pass, password)