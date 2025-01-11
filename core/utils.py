import os
from datetime import datetime

from django.conf import settings


# TODO TEST
def get_upload_image_path(image, filename) -> str:
    now = datetime.now().strftime('%Y%m%d%H%M%S%f')
    _, file_extension = os.path.splitext(filename)
    filename = f"{image.object_id}_{now}"
    model_cls = image.content_type.model_class()
    return f"images/{model_cls.__name__.lower()}/{filename}{file_extension}"
