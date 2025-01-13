from datetime import datetime, timedelta
from typing import Optional

import jwt

from django.conf import settings
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from ninja.security import HttpBearer


# TODO TEST
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


# TODO TEST
def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


# TODO TEST
def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# TODO TEST
class JWTAuth(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> Optional[get_user_model()]:
        if payload := decode_access_token(token):
            try:
                user = get_user_model().objects.get(
                    pk=payload.get("id")
                )
                request.user = user
                return user
            except get_user_model().DoesNotExist:
                return None
        return None
