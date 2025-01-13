from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from core.apis.v1 import router as core_v1_router
from core.exceptions import ApiValidationError


urlpatterns = [
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )


api = NinjaAPI()


@api.exception_handler(ApiValidationError)
def api_error(request, exception):
    return api.create_response(
        request,
        {
            "detail": exception.detail,
        },
        status=exception.status_code
    )


api.add_router("v1/", core_v1_router)

urlpatterns.append(
    path('api/', api.urls)
)
