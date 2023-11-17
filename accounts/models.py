from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager


# class UserManager(BaseUserManager):
#     # 일반 user 생성
#     def create_user(self, username, email, nickname, password=None):
#         if not nickname:
#             raise ValueError('must have user nickname')
#         user = self.model(
#             username = username,
#             email = self.normalize_email(email),
#             nickname = nickname,
#         )
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     # 관리자 user 생성
#     def create_superuser(self, username, email, nickname, password=None):
#         user = self.create_user(
#             username = username,
#             email = email,
#             password = password,
#             nickname = nickname,
#         )
#         user.is_admin = True
#         user.save(using=self._db)
#         return user

# class User(AbstractBaseUser):
#     id = models.AutoField(primary_key=True)
#     username = models.CharField(default='', max_length=100, null=False, blank=False, unique=True)
#     email = models.EmailField(default='', max_length=100, null=True, blank=True, unique=True)
#     nickname = models.CharField(default='', max_length=100, null=False, blank=False, unique=True)
    
#     # User 모델의 필수 field
#     is_active = models.BooleanField(default=True)    
#     is_admin = models.BooleanField(default=False)
    
#     # 헬퍼 클래스 사용
#     objects = UserManager()

#     USERNAME_FIELD = 'username'
#     # 필수로 작성해야하는 field
#     REQUIRED_FIELDS = ['nickname']

#     def __str__(self):
#         return self.username

class User(AbstractUser):
    nickname = models.CharField(max_length=10)
    def __str__(self):
        return self.username