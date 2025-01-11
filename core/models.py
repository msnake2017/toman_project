from abc import abstractmethod

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .utils import get_upload_image_path


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


# TODO TEST
class BaseModelWithImage(BaseModel):

    class Meta:
        abstract = True

    @property
    @abstractmethod
    def MAX_IMAGE_COUNT(self) -> int:  # noqa
        raise NotImplementedError()

    @property
    @abstractmethod
    def MAX_IMAGE_SIZE_MB(self) -> int:  # noqa
        raise NotImplementedError()

    @property
    def images(self) -> QuerySet["Image"]:
        return Image.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object=self,
        )


# TODO TEST
class Image(BaseModel):
    image = models.ImageField(verbose_name=_('image'), upload_to=get_upload_image_path)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def _validate_image_size_limit(self) -> None:
        model_cls = self.content_type.model_class()
        max_size_mb = getattr(model_cls, 'MAX_IMAGE_SIZE_MB')
        if self.image.size > max_size_mb * 1024 * 1024:
            raise ValidationError(_('Image size cannot exceed %s MB.') % max_size_mb)

    def _validate_image_count_limit(self) -> None:
        model_cls = self.content_type.model_class()
        max_image_count = getattr(model_cls, 'MAX_IMAGE_COUNT')
        if not Image.objects.filter(content_type=self.content_type, object_id=self.object_id).count() < max_image_count:
            raise ValidationError(_('Image count cannot exceed %s MB.') % max_image_count)

    def clean(self):
        super().clean()
        self._validate_image_size_limit()
        self._validate_image_count_limit()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# TODO TEST
class Product(BaseModelWithImage):
    title = models.CharField(_('title'), max_length=255)
    price = models.PositiveIntegerField(_('price'))
    description = models.TextField(_('description'))
    updated_at = models.DateTimeField(auto_now=True)

    MAX_IMAGE_COUNT = 5
    MAX_IMAGE_SIZE_MB = 2
