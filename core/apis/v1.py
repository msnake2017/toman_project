from typing import List

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from ninja import Router, UploadedFile, File
from ninja.pagination import (
    paginate,
    PageNumberPagination
)

from core.authentication import JWTAuth
from core.exceptions import ApiValidationError
from core.models import Product, Image
from core.schemas import (
    LoginRespSchema,
    LoginReqSchema,
    RefreshReqSchema,
    ProductRespSchema,
    CreateProductReqSchema,
    ImageRespSchema,
    ErrorSchema,
    NoContent,
    UpdateProductReqSchema,
)

router = Router()

PRODUCT_LIST_CACHE_KEY = 'products:user:{user_id}'


@router.post(
    "/login/access-token/",
    response={
        200: LoginRespSchema,
        401: ErrorSchema
    },
)
def get_access_token(request, body: LoginReqSchema):
    return body.generate_jwt_tokens()


@router.post(
    "/login/refresh-token/",
    response={
        200: LoginRespSchema,
        401: ErrorSchema
    }
)
def get_access_token_from_refresh_token(request, body: RefreshReqSchema):
    return body.generate_jwt_tokens()


@router.get(
    "/products",
    response=List[ProductRespSchema],
    auth=JWTAuth()
)
@paginate(PageNumberPagination)
def get_products(request):
    cache_key = PRODUCT_LIST_CACHE_KEY.format(user_id=request.user.id)
    if not (products := cache.get(cache_key)):
        products = Product.objects.filter(user=request.user)
        cache.set(cache_key, products)

    return products


@router.get(
    "/products/{product_id}",
    response={
        200: ProductRespSchema,
        404: ErrorSchema
    },
    auth=JWTAuth()
)
def get_product(request, product_id: int):
    return get_object_or_404(Product, id=product_id, user=request.user)


@router.delete(
    "/products/{product_id}",
    response={
        204: NoContent,
        404: ErrorSchema
    },
    auth=JWTAuth()
)
def delete_product(request, product_id: int):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    images = product.images
    product.delete()
    images.delete()
    cache.delete(PRODUCT_LIST_CACHE_KEY.format(user_id=request.user.id))
    return 204, ""


@router.post(
    "/products/",
    response={201: ProductRespSchema},
    auth=JWTAuth()
)
def create_product(request, payload: CreateProductReqSchema):
    product = Product.objects.create(user=request.user, **payload.dict())
    cache.delete(PRODUCT_LIST_CACHE_KEY.format(user_id=request.user.id))
    return product


# TODO TEST
@router.put(
    "/products/{product_id}/",
    response={
        200: ProductRespSchema
    },
    auth=JWTAuth()
)
def update_product(request, product_id: int, payload: UpdateProductReqSchema):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    for key, value in payload.dict(exclude_none=True).items():
        setattr(product, key, value)

    product.save()
    cache.delete(PRODUCT_LIST_CACHE_KEY.format(user_id=request.user.id))
    return product


@router.post(
    "/products/{product_id}/images/",
    response={
        201: List[ImageRespSchema],
        400: ErrorSchema
    },
    auth=JWTAuth(),
)
def upload_images_for_product(request, product_id: int, images: List[UploadedFile] = File(...)):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    content_type = ContentType.objects.get_for_model(product)
    response = []
    for image in images:
        try:
            response.append(
                Image.objects.create(
                    object_id=product.id,
                    content_type=content_type,
                    image=image
                )
            )
        except ValidationError as e:
            raise ApiValidationError(
                e.messages[0],
                400
            )

    cache.delete(PRODUCT_LIST_CACHE_KEY.format(user_id=request.user.id))
    return 201, response


@router.delete(
    "/products/{product_id}/images/{image_id}/",
    response={
        204: NoContent,
        404: ErrorSchema
    },
    auth=JWTAuth(),
)
def delete_product_image(request, product_id: int, image_id: int):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    content_type = ContentType.objects.get_for_model(product)
    image = get_object_or_404(Image, id=image_id, object_id=product.pk, content_type=content_type)
    image.delete()
    cache.delete(PRODUCT_LIST_CACHE_KEY.format(user_id=request.user.id))
    return 204, ""
