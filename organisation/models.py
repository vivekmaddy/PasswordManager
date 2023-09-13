import hashlib


from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


# Create your models here.


class Base(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OTP(Base):
    number = models.IntegerField()
    email = models.EmailField()


class Organisation(Base):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class Passwords(Base):
    org_fk = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    raw_password = models.TextField()
    hashed_password = models.TextField(default="")
    duration = models.BigIntegerField() #in seconds
    duration_from = models.DateTimeField()
    duration_to = models.DateTimeField()
    expired = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        data = (self.hashed_password).encode('utf-8')
        sha256_hash = hashlib.sha256()
        sha256_hash.update(data)
        self.hashed_password = sha256_hash.hexdigest() #hashing passwords
        super(Passwords, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.org_fk.name
    

class Members(Base):
    org_fk = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    users = models.ManyToManyField(User)


class SharedPasswords(Base):
    password = models.ForeignKey(Passwords, on_delete=models.CASCADE)
    shared_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shared_to")
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shared_by")
    view = models.BooleanField(default=True)
    edit = models.BooleanField(default=True)
