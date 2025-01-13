from typing import List

from django.contrib.contenttypes.models import ContentType
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
    UpdateOrCreateProductReqSchema,
    ImageRespSchema,
    ErrorSchema, NoContent,
)

router = Router()

# TODO CACHING


# TODO TEST
@router.post(
    "/login/access-token/",
    response={
        200: LoginRespSchema,
        401: ErrorSchema
    },
)
def get_access_token(request, body: LoginReqSchema):
    return body.generate_jwt_tokens()


# TODO TEST
@router.post(
    "/login/refresh-token/",
    response={
        200: LoginRespSchema,
        401: ErrorSchema
    }
)
def get_access_token_from_refresh_token(request, body: RefreshReqSchema):
    return body.generate_jwt_tokens()


# TODO TEST
@router.get(
    "/products",
    response=List[ProductRespSchema],
    auth=JWTAuth()
)
@paginate(PageNumberPagination)
def get_products(request):
    return Product.objects.filter(user=request.user)


# TODO TEST
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


# TODO TEST
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
    return 204, ""


# TODO TEST
@router.post(
    "/products/",
    response={201: ProductRespSchema},
    auth=JWTAuth()
)
def create_product(request, payload: UpdateOrCreateProductReqSchema):
    return Product.objects.create(user=request.user, **payload.dict())


# TODO TEST
@router.put(
    "/products/{product_id}/",
    response={
        200: ProductRespSchema
    },
    auth=JWTAuth()
)
def update_product(request, product_id: int, payload: UpdateOrCreateProductReqSchema):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    for key, value in payload.dict().items():
        setattr(product, key, value)

    product.save()
    return product


# TODO TEST
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

    return 201, response


# TODO TEST
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
    return 204, ""
