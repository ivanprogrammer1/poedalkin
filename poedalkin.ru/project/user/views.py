import base64
import json
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import SessionOAuth, User
from django.http import JsonResponse
from django.shortcuts import render

from django.middleware.csrf import get_token
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, JsonResponse

from .utils import is_valid_password, is_hard_password, get_user, get_basket

from .serializers import UserObjectSerializer

import logging

class UserView(View):

    def get(self, *args, **kwars):
        try:
            user = get_user(self.request)
            return JsonResponse({
                "success": True, "result": UserObjectSerializer(user).data
            })

        except SessionOAuth.SessionException as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            })
        
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": "Another error",
                "message": str(e)
            })

        return JsonResponse({
            "success": False,
            "error": "Don't know"
        })

class LoginView(View):

    REGISTRATION = "reg"
    AUTHORISATION = "auth"

    def get(self, *args, **kwargs):
        return render(self.request, "user/login.html", {"csrf_token": get_token(self.request), "l_bracket": "{{", "r_bracket": "}}"})

    def post(self, *args, **kwargs):

        login = self.request.POST.get("login", "")
        password = self.request.POST.get("password", "")
        rep_password = self.request.POST.get("rep_password", "")

        errors = {}

        if(not login):
            errors["login"] = "Логин не заполнен"

        elif len(login) < 4:
            errors["login"] = "Логин слишком простой. Менее 4 символов"

        if(not password):
            errors["password"] = "Пароль не заполнен"

        type = self.request.POST.get("type", False)

        if not type or not type in [self.REGISTRATION, self.AUTHORISATION]:
            return JsonResponse(
                {"result": False, "errors": {"message": "Не существующий тип операции"}}
            )

        if(errors):
            return JsonResponse({"result": False, "errors": errors})

        if type == self.REGISTRATION:
            user_exist = User.objects.filter(username=login).exists()

            if(user_exist):
                errors["login"] = "Пользователь с таким логином уже существует"
                return JsonResponse({"result": False, "errors": errors})
            else:

                if(not is_valid_password(password)):
                    errors["password"] = "Пароль содержит некорректные символы. Корректные символы: цифры и английские буквы" 
                    return JsonResponse({"result": False, "errors": errors})

                if(not is_hard_password(password)):
                    errors["password"] = "Пароль слишком простой. Должен содержать как миниум 4 буквы в верхнем регистре, 4 буквы в нижнем и 2 цифры"
                    return JsonResponse({"result": False, "errors": errors})

                if(password != rep_password):
                    errors["rep_password"] = "Пароли не совпадают"
                    return JsonResponse({"result": False, "errors": errors})

                user = User(
                    username = login,
                    password = password
                )

                user.save()
                auth_login(self.request, user)

                redirect_str = ""

                if(self.request.GET.get("redirect_to")):
                    redirect_str = base64.b64decode(self.request.GET.get("redirect_to")).decode("utf-8")
                
                return JsonResponse({"result": True, "redirect": redirect_str})

        elif type == self.AUTHORISATION:
            user = authenticate(self.request, username=login, password=password)
            if user:
                auth_login(self.request, user)

                redirect_str = ""

                if(self.request.GET.get("redirect_to")):
                    redirect_str = base64.b64decode(self.request.GET.get("redirect_to")).decode("utf-8")

                return JsonResponse({"result": True, "redirect": redirect_str})
            else:
                return JsonResponse({"result": False, "errors": {"message": "Не существует пользователя с таким логином и паролем"}}) 

class AuthCodeView(View):

    def get(self, *args, **kwargs):

        if(not self.request.user.is_authenticated):
            full_path = str(self.request.build_absolute_uri())
            encode_path = full_path.encode("utf-8")
            base64_path = base64.b64encode(encode_path)
            return HttpResponseRedirect(reverse("login") + F"?redirect_to={base64_path.decode('utf-8')}")

        return render(
            self.request, 
            "user/auth_code.html", 
            {
                "csrf_token": get_token(self.request),
                "state": self.request.GET.get("state", "")
            }
        )   

    def post(self, *args, **kwargs):

        if(not self.request.user.is_authenticated):
            return HttpResponseRedirect(reverse("login"))

        device_meta = self.request.META.get("HTTP_USER_AGENT", None)

        sessions_active = SessionOAuth.objects.active(
            device_name=device_meta,
            user=self.request.user
        )

        sessions_active.delete()

        session = SessionOAuth.create_session(
            user=self.request.user,
            device_name=device_meta
        )

        session.save()

        full_path = "ru.poedalkin.oauth://success?code=" + session.authorization_code + "&state=" + self.request.POST.get("state", "")

        return JsonResponse({
            "result": True,
            "redirect": full_path
        })


@method_decorator(csrf_exempt, name='dispatch')
class AccessCodeView(View):

    def get(self, *args, **kwargs):

        auth_token = self.request.GET.get("code", False)

        if not auth_token:
            return JsonResponse({
                "result": False,
                "errors": {"message": "Отсутствует токен авторизации"}
            })

        session = SessionOAuth.objects.active(
            authorization_code=auth_token,
            auth_code_was_used=False
        ).first()

        if(session):

            session.auth_code_was_used = True
            session.save()

            return JsonResponse({
                "result": True,
                "access_token": session.access_token,
                "refresh_token": session.refresh_token
            })

        else:
            return JsonResponse({
                "result": False,
                "errors": {"message": "Токен авторизации был использован или его не существует"}
            })

class RefreshCodeView(View):
    def get(self, *args, **kwargs):

        refresh_code = self.request.GET.get("refresh_code", False)

        old_session = SessionOAuth.objects.filter(
            refresh_token=refresh_code,
        ).first()

        if(old_session):

            session = SessionOAuth.create_session(
                user=old_session.user,
                device_name=old_session.device_name
            )

            old_session.delete()

            session.auth_code_was_used = True
            session.save()

            return JsonResponse({
                "success": True,
                "result": {
                    "access_token": session.access_token,
                    "refresh_token": session.refresh_token
                }
            })

        return JsonResponse({
            "success": False,
            "error": "Код не соответствует одной из сессий"
        })


class UserUpdateView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        
        try:
            user = get_user(self.request)
        except SessionOAuth.SessionException as e:
            return JsonResponse({"success": False, "result": str(e)})

        dataJson = json.loads(self.request.body)

        phone = dataJson.get("phone", "")
        street = dataJson.get("street", "")
        house = dataJson.get("house", "")
        apartment = dataJson.get("apartment", "")
        entrance = dataJson.get("entrance", "")
        floor = dataJson.get("floor", "")
        door_code = dataJson.get('door_code', "")

        user.phone = phone
        user.street = street
        user.house = house
        user.apartment = apartment
        user.entrance = entrance
        user.floor = floor
        user.door_code = door_code

        user.save()

        return JsonResponse({
            "success": True,
            "result": UserObjectSerializer(user).data
        })

def checkActiveToken(request):
    code = request.headers.get("Authorization", "")

    session = SessionOAuth.objects.filter(
        access_token=code
    ).first()

    status_code = ""

    if(not session):
        status_code = SessionOAuth.TOKEN_DELETE
    else:
        status_code = session.get_status_token()
        session.update_token_by_status()

    return JsonResponse(
        {
            "success": True, 
            "result": {
                "status_code": status_code
            }
        }
    )