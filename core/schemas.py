from datetime import datetime
from typing import Optional, List

from django.contrib.auth import get_user_model
from ninja import Schema
from pydantic import model_validator, Field, field_validator
from typing_extensions import Self

from .authentication import (
    create_access_token,
    create_refresh_token,
    decode_access_token
)
from .exceptions import ApiValidationError


class NoContent(Schema):
    pass


class ErrorSchema(Schema):
    detail: str


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


class ImageRespSchema(Schema):
    id: int
    image: str


class BaseProductSchema(Schema):
    title: str
    price: int = Field(..., gt=0)
    description: str


class ProductRespSchema(BaseProductSchema):
    id: int
    created_at: datetime
    updated_at: datetime
    images: Optional[List[ImageRespSchema]]


class CreateProductReqSchema(BaseProductSchema): ...  # noqa


class UpdateProductReqSchema(Schema):
    title: str | None = None
    description: str | None = None
    price: int | None

    @field_validator('price', mode='before')
    @classmethod
    def ensure_list(cls, value: int | None) -> int | None:
        if isinstance(value, int):
            if value <= 0:
                raise ApiValidationError('Invalid price', status_code=400)

        return value
