from django.contrib.auth import get_user_model
from ..models import Storage

User = get_user_model()


def get_user_choices():
    return [(u.id, u.username) for u in User.objects.all()]


def get_storage_choices():
    return [(s.id, s.name) for s in Storage.objects.all() ]
