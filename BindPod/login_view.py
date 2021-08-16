from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import exceptions
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework import HTTP_HEADER_ENCODING
from utils.cache import Cache
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from utils import logs
from agent import models


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs):
        data = self.auth(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data

    def auth(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            pass
        self.user = authenticate(**authenticate_kwargs)
        if self.user is None:
            raise exceptions.AuthenticationFailed("用户名密码错误!")
        elif not self.user.is_active:
            raise exceptions.AuthenticationFailed("用户被禁用，请联系管理员!")
        models.Log(username=self.user.username, event=0, content="登陆成功!").save()
        return {
            "user": self.user.username,
            "active": self.user.is_active,
            "user_display": self.user.first_name,
            "is_staff": self.user.is_staff,
            "user_type": "admin" if self.user.is_staff else "user",
        }


class LogOutSerializer(serializers.Serializer):
    username = serializers.CharField(help_text="用户名")


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        data = {
            "display_name": serializer.validated_data["user_display"],
            "username": serializer.validated_data["user"],
            "Token": serializer.validated_data["access"],
            "UserType": serializer.validated_data["user_type"],
            "active": serializer.validated_data["user_type"],
            "is_staff": serializer.validated_data["is_staff"],
        }
        Cache.set(request.data["username"], serializer.validated_data["access"])
        return Response(data, status=status.HTTP_200_OK)


class LogoutView(TokenViewBase):
    serializer_class = LogOutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        header = request.META.get('HTTP_AUTHORIZATION')
        if isinstance(header, str):
            header = header.encode(HTTP_HEADER_ENCODING)
        try:
            tag, token = header.split()
            cache_token = Cache.get(serializer.data["username"])
            if cache_token is not None and str(cache_token).strip() == token.decode().strip():
                Cache.delete(serializer.data["username"])
                try:
                    user_obj = User.objects.get(username=serializer.data["username"])
                    models.Log(username=user_obj.username, event=0, content="注销登陆成功!").save()
                except User.DoesNotExist:
                    logs.print("error", "{user}不存在，无法记录注销日志".format(user=serializer.data["username"]))
        except ValueError:
            pass
        except AttributeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response({"code": 200, "msg": "注销成功!"}, status=status.HTTP_200_OK)
