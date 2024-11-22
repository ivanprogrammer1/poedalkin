from django.utils import timezone

from uuid import uuid4
from django.db import models
from shop.model_mixins import AddressFields
from django.contrib.auth.models import AbstractUser

def upload_user_picture(instance, filename):
    return F"user/{instance.username}/{filename}"

class User(AbstractUser, AddressFields):
    REQUIRED_FIELDS = []
    
    user_pictue = models.ImageField(upload_to=upload_user_picture, null=True, blank=True)
    personal_data = models.CharField(max_length=500, verbose_name="ФИО", blank=True, default="")
    #phone = models.CharField(max_length=200, verbose_name="Телефон", blank=True, default="")
    comment = None

class SessionOAuthManager(models.Manager):

    def active(self, **kwargs):
        return self.get_queryset().filter(
            is_active=True,
            **kwargs
        )

class SessionOAuth(models.Model):

    #Токен активирован и работает
    TOKEN_ACTIVE = "0"

    #Токен деактивирован, его можно обновить
    TOKEN_REFRESH = "1"

    #Токен деактивирован, с ним ничего нельзя поделать
    TOKEN_DELETE = "3"   

    #Токен был создан, но не был активирован
    TOKEN_START = "4" 

    STATUSES = [TOKEN_ACTIVE, TOKEN_REFRESH, TOKEN_DELETE, TOKEN_START]

    class SessionException(Exception):
        pass

    class UserNotFound(SessionException):
        def __init__(self, msg="User with token not found", *args, **kwargs):
            super().__init__(msg, *args, **kwargs)

    class AuthCodeWasUsed(SessionException):
        def __init__(self, msg="Authorization code was used", *args, **kwargs):
            super().__init__(msg, *args, **kwargs)

    class TokenWasExpires(SessionException):
        def __init__(self, msg="Access token was expired", *args, **kwargs):
            super().__init__(msg, *args, **kwargs)

    objects = SessionOAuthManager()

    #Токен активен
    is_active = models.BooleanField(default=True)

    #Пользователь
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    #Код авторизации
    authorization_code = models.CharField(
        max_length=200,
        unique=True,
    )

    #Код авторизации был использован
    auth_code_was_used = models.BooleanField(
        default=False
    )

    #Код доступа
    access_token = models.CharField(
        max_length=200,
        unique=True
    )

    #Код доступа
    refresh_token = models.CharField(
        max_length=200,
        unique=True
    )

    #Дата конца доступа access_token
    expires_access_token = models.DateTimeField()

    #Дата конца доступа refresh_token
    expires_refresh_token = models.DateTimeField()

    #Дата конца доступа auth_token
    expires_auth_token = models.DateTimeField()

    #Дата создания
    login_time = models.DateTimeField()

    #Имя устройства
    device_name = models.CharField(
        max_length=200,
        default="",
        null=True,
        blank=True
    )

    def update_token_by_status(self):
        status = self.get_status_token()

        if(status == self.TOKEN_DELETE):
            self.delete()

        elif(status == self.TOKEN_START):
            self.is_active = False
            self.save()

        elif(status == self.TOKEN_REFRESH):
            self.is_active = False
            self.save()

        elif(status == self.TOKEN_ACTIVE):
            self.is_active = True
            self.save()


    def get_status_token(self):
        dt = timezone.now() + timezone.timedelta(minutes=10)

        if(not self.auth_code_was_used and self.expires_auth_token > dt):
            print(1)
            return self.TOKEN_START

        elif(not self.auth_code_was_used and self.expires_auth_token <= dt):
            print(2)
            return self.TOKEN_DELETE

        elif(self.expires_access_token <= dt and self.expires_refresh_token > dt):
            print(3)
            return self.TOKEN_REFRESH

        elif(self.expires_access_token <= dt and self.expires_refresh_token <= dt):
            print(4)
            return self.TOKEN_DELETE

        return self.TOKEN_ACTIVE

    @staticmethod
    def create_authorisation_code():
        return str(uuid4())

    @staticmethod
    def create_access_token():
        return str(uuid4())

    @staticmethod
    def create_refresh_token():
        return str(uuid4())

    @staticmethod
    def get_expires_access_token_data():
        return timezone.now() + timezone.timedelta(days=1)

    @staticmethod
    def get_expires_refresh_token_data():
        return timezone.now() + timezone.timedelta(days=2)

    @staticmethod
    def get_expires_auth_token_data():
        return timezone.now() + timezone.timedelta(minutes=30)

    def refresh_token_was_expired(self):
        return self.expires_refresh_token > timezone.now()

    @staticmethod
    def create_session(user, device_name=None):
        session = SessionOAuth(
            user=user,
            device_name=device_name,

            authorization_code=SessionOAuth.create_authorisation_code(),
            access_token=SessionOAuth.create_access_token(),
            refresh_token=SessionOAuth.create_refresh_token(),

            expires_access_token=SessionOAuth.get_expires_access_token_data(),
            expires_refresh_token=SessionOAuth.get_expires_refresh_token_data(),
            expires_auth_token=SessionOAuth.get_expires_auth_token_data(),

            login_time=timezone.now()
        )
        return session

    def __str__(self):
        return F"{self.user} - {self.device_name} - {self.is_active} - {self.expires_auth_token} - {self.expires_access_token} - {self.expires_refresh_token}"