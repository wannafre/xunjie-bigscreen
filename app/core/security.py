from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str, salt: str = "") -> bool:
    """
    Verify a plain text password against its bcrypt hash, using the custom salt.
    """
    return pwd_context.verify(plain_password + salt, hashed_password)

def get_password_hash(password: str, salt: str = "") -> str:
    """
    Generate bcrypt hash from plain text password, using the custom salt.
    """
    return pwd_context.hash(password + salt)
