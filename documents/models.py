
import uuid
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.get_username(), instance.id)


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.FileField(upload_to=user_directory_path)
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='documents',
    )


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to=user_directory_path)
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='images',
    )
