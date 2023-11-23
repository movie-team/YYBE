from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager


class User(AbstractUser):
    nickname = models.CharField(max_length=30)
    
