import hashlib
import hmac
from config import Config

_config = Config()
_secret = _config.SECRET_KEY

def hash_password(password: str) -> str:
    """Return a hex digest using HMAC-SHA256 with SECRET_KEY"""
    if password is None:
        return ''
    return hmac.new(_secret.encode('utf-8'), password.encode('utf-8'), hashlib.sha256).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Check if password corresponds to hashed"""
    if not hashed:
        return False
    computed = hash_password(password)
    return hmac.compare_digest(computed, hashed)
