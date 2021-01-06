from rest_framework.decorators import action
from rest_framework.response import Response
from utils.cache import Cache
from .. import models
from ..lib2.codes import ResponseMessage, LogCode
from django.contrib.auth.models import User


class UserViews:

    @staticmethod
    def filter_user(username, data):
        result = []
        for domain in data:
            if username in domain["is_user"]:
                status = True
            else:
                status = False
            result.append({"domain": domain["domain"], "status": status})
        return result

    @action(detail=False, methods=["GET"], url_path='domain/(?P<username>.*)')
    def domain(self, request, *args, **kwargs):
        queryset = models.Domain.objects.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(self.filter_user(kwargs["username"], serializer.data))

        serializer = self.get_serializer(queryset, many=True)
        return Response(self.filter_user(kwargs["username"], serializer.data))

    @action(detail=False, methods=["POST"], url_path='change')
    def change(self, request, *args, **kwargs):
        try:
            username = request.data["username"]
            password = request.data["password"]
        except KeyError as key:
            return Response({"code": ResponseMessage.ArgsError, "msg": "缺少:{key}参数!".format(key=key)})
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

    @action(detail=False, methods=["POST"], url_path='active')
    def active(self, request, *args, **kwargs):
        try:
            username = request.data["username"]
            is_active = request.data["active"]
        except KeyError as key:
            return Response({"code": ResponseMessage.ArgsError, "msg": "缺少:{key}参数1".format(key=key)})
        try:
            user_obj = User.objects.get(username=username)
            user_obj.is_active = is_active
            user_obj.save()
        except User.DoesNotExist:
            return Response({"code": ResponseMessage.DataNoExistsError, "msg": "用户不存在!"})
        if is_active:
            msg = "用户激活完成!"
        else:
            msg = "用户禁用完成!"
            Cache.delete(username)
        models.Log(username=str(request.user), event=LogCode.User,
                   content="{username}{msg}".format(username=username, msg=msg)).save()
        return Response({"code": ResponseMessage.Success, "msg": msg})

    @action(detail=False, methods=["POST"], url_path='create')
    def add(self, request, *args, **kwargs):
        try:
            username = request.data["username"]
            is_superuser = request.data["is_superuser"]
            first_name = request.data["first_name"]
            email = request.data["email"]
            password = request.data["password"]
        except KeyError as key:
            return Response({"code": ResponseMessage.ArgsError, "msg": "缺少:{key}参数".format(key=key)})
        if User.objects.filter(username=username).exists():
            return Response({"code": ResponseMessage.DataExistsError, "msg": "用户已经存在!"})
        user_obj = User.objects.create(
            username=username,
            is_superuser=is_superuser,
            first_name=first_name,
            email=email,
        )
        user_obj.set_password(request.data["password"])
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
        for user in username:
            try:
                User.objects.get(username=user).delete()
            except User.DoesNotExist:
                continue
            models.Log(username=str(request.user), event=LogCode.User,
                       content="删除:{username}成功".format(username=username)).save()
        return Response({"code": ResponseMessage.Success, "msg": "用户删除成功!"})

    @action(detail=False, methods=["POST"], url_path='password')
    def password(self, request, *args, **kwargs):
        try:
            username = request.data["username"]
            user_obj = User.objects.get(username=username)
            user_obj.set_password(request.data["password"])
            user_obj.save()
        except KeyError as key:
            return Response({"code": ResponseMessage.ArgsError, "msg": "缺少:{key}参数".format(key=key)})
        except User.DoesNotExist:
            return Response({"code": ResponseMessage.DataNoExistsError,
                             "msg": "用户:{username}不存在".format(username=request.data["username"])})
        models.Log(username=str(request.user), event=LogCode.User,
                   content="修改:{username}密码成功".format(username=username)).save()
        return Response({"code": ResponseMessage.Success, "msg": "用户密码修改成功!"})

    @action(detail=False, methods=["POST"], url_path='add/domain')
    def add_domain(self, request, *args, **kwargs):
        try:
            user_obj = User.objects.get(username=request.data["username"])
            domain_obj = models.Domain.objects.get(domain=request.data["domain"])
            if domain_obj.id in [domain.id for domain in user_obj.domain.all()]:
                return Response({"code": ResponseMessage.DataExistsError,
                                 "msg": "域名:{domain}已经授权过".format(domain=domain_obj.domain)})
            user_obj.domain.add(domain_obj)
            user_obj.save()
        except KeyError as key:
            return Response({"code": ResponseMessage.ArgsError, "msg": "缺少:{key}参数".format(key=key)})
        except User.DoesNotExist:
            return Response({"code": ResponseMessage.DataNoExistsError,
                             "msg": "用户:{username}不存在".format(username=request.data["username"])})
        except models.Domain.DoesNotExist:
            return Response({"code": ResponseMessage.DataNoExistsError,
                             "msg": "域名:{domain}不存在".format(domain=request.data["domain"])})
        models.Log(username=str(request.user), event=LogCode.User, content="{username}授权{domain}域名成功".format(
            username=request.data["username"], domain=request.data["domain"])).save()
        return Response(
            {"code": ResponseMessage.Success, "msg": "域名:{domain}授权成功!".format(domain=request.data["domain"])})

    @action(detail=False, methods=["POST"], url_path='add/remove')
    def add_remove(self, request, *args, **kwargs):
        try:
            user_obj = User.objects.get(username=request.data["username"])
            domain_obj = models.Domain.objects.get(domain=request.data["domain"])
            if domain_obj.id not in [domain.id for domain in user_obj.domain.all()]:
                return Response({"code": ResponseMessage.DataNoExistsError,
                                 "msg": "域名:{domain}没有授权".format(domain=domain_obj.domain)})
            user_obj.domain.remove(domain_obj)
            user_obj.save()
        except KeyError as key:
            return Response({"code": ResponseMessage.ArgsError, "msg": "缺少:{key}参数".format(key=key)})
        except User.DoesNotExist:
            return Response({"code": ResponseMessage.DataNoExistsError,
                             "msg": "用户:{username}不存在".format(username=request.data["username"])})
        except models.Domain.DoesNotExist:
            return Response({"code": ResponseMessage.DataNoExistsError,
                             "msg": "域名:{domain}不存在".format(domain=request.data["domain"])})
        models.Log(username=str(request.user), event=LogCode.User, content="{username}取消授权{domain}域名成功".format(
            username=request.data["username"], domain=request.data["domain"])).save()
        return Response(
            {"code": ResponseMessage.Success, "msg": "域名:{domain}取消授权成功!".format(domain=request.data["domain"])})
