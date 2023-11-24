from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from customer import choices
from django.db.models import OneToOneField
import uuid


def gen_uuid():
    uid = uuid.uuid4()
    if Customer.objects.filter(wallet_id=uid).exists():
        return gen_uuid()
    return uid


class CustomerUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    groups = models.ManyToManyField(Group, related_name='customer_user_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customer_user_permissions', blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Customer(models.Model):
    wallet_id = models.UUIDField(unique=True, default=gen_uuid)
    sex_tape = models.CharField(choices=choices.Gender.CHOICES, max_length=6)
    dni = models.BigIntegerField(unique=True)
    birth_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = OneToOneField('customer.CustomerUser', on_delete=models.CASCADE, related_name='customer')

