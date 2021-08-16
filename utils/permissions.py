from rest_framework import permissions
from utils.cache import Cache
from rest_framework_simplejwt.state import User
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError


class CheckPermission:
    def __init__(self, request, views):
        self.views = views.__class__.__name__
        self.action = views.action
        self.request = request

    def LogView(self):
        return True

    def DomainView(self):
        return self.request.user.is_staff

    def DomainView_list(self):
        return True

    def DomainView_get_info(self):
        return True

    def DomainView_delete(self):
        return self.request.user.is_staff

    def ResolveView(self):
        if self.request.user.is_staff:
            return True
        if self.request.method.upper() == "GET":
            try:
                domain = self.request.path.strip("/").split("/")[-1]
            except Exception:
                return False
        else:
            try:
                domain = self.request.data["domain"]
            except KeyError:
                return False
        try:
            self.request.user.domain.get(domain=domain.strip())
            return True
        except Exception:
            return False

    def UserView(self):
        return self.request.user.is_staff

    def UserView_change(self):
        return True

    def UserView_info(self):
        return True

    def ver(self):
        # print("{view}_{action}".format(view=self.views, action=self.action))
        try:
            return getattr(self, "{view}_{action}".format(view=self.views, action=self.action),
                           getattr(self, self.views))()
        except Exception:
            return False


class UserPermission(permissions.BasePermission):
    message = {"msg": "您没有权限操作!", "code": 403}

    def has_permission(self, request, view):
        auth = Authentication()
        user = auth.authenticate(request)
        if user is None:
            self.message["code"] = 401
            return False
        request.user = user
        return CheckPermission(request, view).ver()


class Authentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        messages = []
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                messages.append({'token_class': AuthToken.__name__,
                                 'token_type': AuthToken.token_type,
                                 'message': e.args[0]})

        return None

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        validated_token = self.get_validated_token(raw_token)
        if validated_token is None:
            return
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            return None
        try:
            user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except User.DoesNotExist:
            return None

        if not user.is_active:
            return None

        cache_token = Cache.get(user.username)
        if cache_token is None or str(cache_token).strip() != raw_token.decode().strip():
            return None
        return self.get_user(validated_token)
