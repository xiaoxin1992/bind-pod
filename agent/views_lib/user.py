from rest_framework.decorators import action
from rest_framework.response import Response
from utils.cache import Cache
from .. import models
from ..lib2.codes import ResponseMessage, LogCode
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class UserViews:

    @action(detail=False, methods=["get"], url_path="domain")
    def domain_to_user(self, request, *args, **kwargs):
        queryset = models.Domain.objects.all()
        domain = request.GET.get("domain", "").strip()
        if len(domain) != 0:
            queryset = queryset.filter(domain__contains=domain)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=["GET"], url_path='info')
    def info(self, request, *args, **kwargs):
        request.user = "root"
        try:
            userObj = User.objects.get(username=request.user)
            data = {
                "username": userObj.username,
                "display_name": userObj.first_name,
                "email": userObj.email,
                "is_staff": userObj.is_staff
            }
            return Response({"code": ResponseMessage.Success, "data": data})
        except User.DoesNotExist:
            return Response({"code": ResponseMessage.DataError, "msg": "获取用户信息失败"})

    @action(detail=False, methods=["POST"], url_path='change/passwd')
    def change(self, request, *args, **kwargs):
        try:
            username = request.data["username"]
            old_password = request.data["old_password"]
            password = request.data["password"]
        except KeyError as key:
            return Response({"code": ResponseMessage.ArgsError, "msg": "缺少:{key}参数!".format(key=key)})
        if authenticate(username=username, password=old_password) is None:
            return Response({"code": ResponseMessage.Failed, "msg": "密码认证失败"})
        if str(request.user) != username:
            return Response({"code": ResponseMessage.Failed, "msg": "密码修改失败!"})
        try:
            user_obj = User.objects.get(username=username)
            user_obj.set_password(password)
            user_obj.save()
        except User.DoesNotExist:
            return Response({"code": ResponseMessage.DataNoExistsError, "msg": "用户不存在!"})
        Cache.delete(username)
        msg = "密码修改完成!"
        models.Log(username=str(request.user), event=LogCode.User,
                   content="{username}{msg}".format(username=username, msg=msg)).save()
        return Response({"code": ResponseMessage.Success, "msg": "密码修改完成!"})

    @action(detail=False, methods=["POST"], url_path='create')
    def add(self, request, *args, **kwargs):
        try:
            username = request.data["username"]
            first_name = request.data["first_name"]
            email = request.data["email"]
            password = request.data["password"]
            is_active = request.data["is_active"]
            is_staff = request.data["is_staff"]
        except KeyError as key:
            return Response({"code": ResponseMessage.ArgsError, "msg": "缺少:{key}参数".format(key=key)})
        if User.objects.filter(username=username).exists():
            return Response({"code": ResponseMessage.DataExistsError, "msg": "用户已经存在!"})
        user_obj = User.objects.create(
            username=username,
            is_staff=is_staff,
            first_name=first_name,
            email=email,
            is_active=is_active,
        )
        user_obj.set_password(password)
        user_obj.save()
        models.Log(username=str(request.user), event=LogCode.User,
                   content="创建:{username}成功".format(username=username)).save()
        return Response({"code": ResponseMessage.Success, "msg": "用户创建成功!"})

    @action(detail=False, methods=["POST"], url_path='delete')
    def delete(self, request, *args, **kwargs):
        try:
            username = request.data["username"]
        except KeyError as key:
            return Response({"code": ResponseMessage.ArgsError, "msg": "缺少:{key}参数".format(key=key)})
        user_obj = User.objects.filter(username__in=username)
        if not user_obj.exists():
            return Response({"code": ResponseMessage.DataNoExistsError, "msg": "用户不能为空"})
        for user in user_obj:
            models.Log(username=str(request.user), event=LogCode.User,
                       content="删除:{username}成功".format(username=user.username)).save()
        user_obj.delete()
        return Response({"code": ResponseMessage.Success, "msg": "用户删除成功!"})

    @action(detail=False, methods=["POST"], url_path='change')
    def password(self, request, *args, **kwargs):
        try:
            password = request.data.get("password", "")
            user_obj = User.objects.get(username=request.data["username"])
            user_obj.first_name = request.data["first_name"]
            user_obj.email = request.data["email"]
            user_obj.is_active = request.data["is_active"]
            user_obj.is_staff = request.data["is_staff"]
            if len(password.strip()) != 0:
                user_obj.set_password(password)
            user_obj.save()
        except KeyError as key:
            return Response({"code": ResponseMessage.ArgsError, "msg": "缺少:{key}参数".format(key=key)})
        except User.DoesNotExist:
            return Response({"code": ResponseMessage.DataNoExistsError,
                             "msg": "用户:{username}不存在".format(username=request.data["username"])})
        models.Log(username=str(request.user), event=LogCode.User,
                   content="修改:{username}信息成功".format(username=request.data["username"])).save()
        return Response({"code": ResponseMessage.Success, "msg": "用户信息修改成功!"})

    @action(detail=False, methods=["POST"], url_path='domain/authorize')
    def domain_add_user(self, request, *args, **kwargs):
        try:
            domain = request.data["domain"]
            users = request.data["users"]
            if not isinstance(users, list):
                raise KeyError("users")
        except KeyError as key:
            return Response({"code": ResponseMessage.ArgsError, "msg": "缺少:{key}参数".format(key=key)})
        domainObj = models.Domain.objects.get(domain=domain)
        usersObj = models.User.objects.filter(username__in=users)
        domainObj.user.clear()
        domainObj.user.add(*usersObj)
        domainObj.save()
        return Response({"code": ResponseMessage.Success, "msg": "授权完成"})
