import hashlib, hmac, secrets
from datetime import datetime, timedelta, timezone
import jwt
from .config import settings
try:
    import bcrypt
except ImportError:
    bcrypt=None
def hash_password(password:str)->str:
    if bcrypt:
        return bcrypt.hashpw(password.encode(),bcrypt.gensalt(rounds=12)).decode()
    salt=secrets.token_bytes(16); digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,310_000)
    return f"pbkdf2${salt.hex()}${digest.hex()}"
def verify_password(password:str,stored:str)->bool:
    if stored.startswith("$2") and bcrypt:
        return bcrypt.checkpw(password.encode(),stored.encode())
    if stored.startswith("pbkdf2$"):
        _,salt_hex,digest_hex=stored.split("$",2); candidate=hashlib.pbkdf2_hmac("sha256",password.encode(),bytes.fromhex(salt_hex),310_000)
        return hmac.compare_digest(candidate.hex(),digest_hex)
    return False
def create_token(user)->str:
    now=datetime.now(timezone.utc)
    payload={"sub":user.id,"email":user.email,"role":user.role,"iat":now,"exp":now+timedelta(minutes=settings.jwt_expire_minutes)}
    return jwt.encode(payload,settings.jwt_secret,algorithm=settings.jwt_algorithm)
def decode_token(token:str)->dict:
    return jwt.decode(token,settings.jwt_secret,algorithms=[settings.jwt_algorithm])
