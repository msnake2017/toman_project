from ninja import Router

from core.schemas import (
    LoginRespSchema,
    LoginReqSchema,
    RefreshReqSchema
)

router = Router()


# TODO TEST
@router.post(
    "/login/access-token/",
    response={
        200: LoginRespSchema,
        401: dict
    },
)
def get_access_token(request, body: LoginReqSchema):
    return body.generate_jwt_tokens()


# TODO TEST
@router.post(
    "/login/refresh-token/",
    response={
        200: LoginRespSchema,
        401: dict
    }
)
def get_access_token_from_refresh_token(request, body: RefreshReqSchema):
    return body.generate_jwt_tokens()
