from django.contrib.auth import get_user_model
from ninja import Schema
from pydantic import model_validator
from typing_extensions import Self

from .authentication import (
    create_access_token,
    create_refresh_token,
    decode_access_token
)
from .exceptions import ApiValidationError


class BaseLoginReqSchema(Schema):
    _user_id: int = None

    def generate_jwt_tokens(self) -> dict:
        payload = {
            'id': self._user_id
        }
        return {
            'access_token': create_access_token(payload),
            'refresh_token': create_refresh_token(payload)
        }


# TODO TEST
class LoginReqSchema(BaseLoginReqSchema):
    username: str
    password: str

    @model_validator(mode='after')
    def validate__user(self) -> Self:
        try:
            user = get_user_model().objects.get(username=self.username)
        except get_user_model().DoesNotExist:
            user = get_user_model().objects.create_user(username=self.username, password=self.password)
        else:
            if not user.check_password(self.password):
                raise ApiValidationError('Incorrect password', status_code=401)

        self._user_id = user.pk
        return self


# TODO TEST
class RefreshReqSchema(BaseLoginReqSchema):
    refresh_token: str

    @model_validator(mode='after')
    def validate_refresh_token(self) -> Self:
        if payload := decode_access_token(self.refresh_token):
            self._user_id = payload['id']
            return self

        raise ApiValidationError('Invalid refresh token', status_code=401)


class LoginRespSchema(Schema):
    access_token: str
    refresh_token: str
