from django.conf import settings
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from ..lib2.verification_tools import Verification
from ..lib2.codes import ResponseMessage, LogCode
from ..lib2.named import Dns
from .. import models


class SerializerVerificationCheck:
    """
    检查Serializer参数是否正常
    """

    @staticmethod
    def serializer_ver(serializer):
        serializer_check = serializer.is_valid(raise_exception=False)
        if not serializer_check:
            key = [i for i in serializer.errors][0]
            raise ValidationError({
                "code": ResponseMessage.ArgsError,
                "msg": "{field} {msg}".format(field=key, msg=serializer.errors[key])
            })


class Resolve(SerializerVerificationCheck):

    def bind(self, server, key, code, domain, port=53):
        return Dns(server=server, key=key, code=code, domain=domain, port=port)

    def verification_handle(self, request):
        self.serializer_ver(self.get_serializer(data=request.data))
        self.verification()

    def verification(self):
        if self.request.data["type"].upper() == "MX":
            self.request.data["name"] = "@"
            address = self.request.data["address"]
            self.request.data["address"] = "{address}.".format(address=address) if address[-1] != "." else address
        # ver = VerificationResolve(self.request.data["name"], self.request.data["address"])
        self.verification_data(self.request.data["address"], self.request.data["type"])

    @staticmethod
    def verification_data(address, resolve_type):
        if resolve_type.upper() == "AAAA":
            if not Verification.is_ip(address, version=6):
                raise ValidationError({"code": ResponseMessage.ArgsError, "msg": "AAAA类型必须是一个合法的IPV6地址"})
        elif resolve_type.upper() == "A":
            if not Verification.is_ip(address, version=4):
                raise ValidationError({"code": ResponseMessage.ArgsError, "msg": "A类型必须是一个合法的IPV4地址"})
        elif resolve_type.upper() == "NS":
            if not Verification.is_ip(address, 4) and not Verification.is_ip(address,
                                                                             6) and not Verification.is_full_domain(
                    address):
                raise ValueError({"code": ResponseMessage.ArgsError, "msg": "ns记录必须是一个IP地址或者域名"})
        elif resolve_type.upper() in ["MX", "CNAME"]:
            if not Verification.is_full_domain(address):
                raise ValidationError(
                    {"code": ResponseMessage.ArgsError, "msg": "{type}必须是一个完整的域名".format(type=resolve_type.upper())})
        elif resolve_type.upper() == "TXT":
            pass
        else:
            raise ValidationError(
                {"code": ResponseMessage.ArgsError, "msg": "不支持的解析类型:{type}".format(type=resolve_type)})

    def args_handle(self, request=None, is_delete=False):
        if not is_delete:
            self.verification_handle(request)
        config = getattr(settings, "DNS_BASE_CONFIG")
        bind_obj = self.bind(
            server=config.get("server", "127.0.0.1"),
            key=config["key"],
            code=config["secret"],
            domain=request.data["domain"],
            port=int(config.get("port", 53)),
        )
        return bind_obj

    @staticmethod
    def domain_is_exists(domain):
        try:
            return models.Domain.objects.get(domain=domain)
        except models.Domain.DoesNotExist:
            return None

    @action(detail=False, methods=["POST"], url_path='create')
    def add(self, request, *args, **kwargs):
        domain_obj = self.domain_is_exists(request.data.get("domain", ""))
        if domain_obj is None:
            return Response({"code": ResponseMessage.DataNoExistsError, "msg": "域名不存在"})
        bind_obj = self.args_handle(request)
        mx = 5 if int(request.data.get("mx", 5)) < 5 else int(request.data.get("mx", 5))
        name = request.data["name"]
        ttl = request.data["ttl"]
        address = request.data["address"]
        resolve_type = request.data["type"].upper()
        if domain_obj.resolve.filter(name=name, type=resolve_type, address=address).exists():
            return Response({"code": ResponseMessage.DataExistsError, "msg": "解析已经存在"})
        if bind_obj.add(name=name, ttl=ttl, domain_type=resolve_type, host=address, mx=mx):
            domain_obj.resolve.create(name=name, type=resolve_type, address=address, mx=mx, ttl=ttl)
        else:
            return Response({"code": ResponseMessage.Failed, "msg": "添加解析失败"})
        msg = "域名:{domain}增加解析:{name}记录类型为:{type},地址:{address}!".format(**{
            "domain": domain_obj.domain,
            "name": name,
            "type": request.data["type"].upper(),
            "address": request.data["address"]
        })
        models.Log(username=str(request.user), event=LogCode.Resolve, content=msg).save()
        return Response({"code": ResponseMessage.Success, "msg": "解析添加成功"})

    @action(detail=False, methods=["GET"], url_path='list/(?P<domain>[a-z.]+)')
    def get(self, request, *args, **kwargs):
        domain_obj = self.domain_is_exists(kwargs.get("domain", ""))
        if domain_obj is None:
            return Response({"code": ResponseMessage.DataNoExistsError, "msg": "域名不存在"})
        queryset = domain_obj.resolve.all()
        page = self.paginate_queryset(self.filter_queryset(queryset))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["POST"], url_path='modify')
    def modify(self, request, *args, **kwargs):
        domain_obj = self.domain_is_exists(request.data.get("domain", ""))
        if domain_obj is None:
            return Response({
                "code": ResponseMessage.DataNoExistsError,
                "msg": "域名:{domain}不存在".format(domain=request.data["domain"])
            })
        try:
            resolve_obj = domain_obj.resolve.get(id=int(request.data.get("resolve_id", 0)))
        except (models.Resolve.DoesNotExist, KeyError):
            return Response({"code": ResponseMessage.DataNoExistsError, "msg": "解析记录不存在"})
        mx = 5 if request.data.get("mx", 5) < 5 else request.data.get("mx", 5)
        ttl = request.data["ttl"]
        new_address = request.data["address"]
        request.data["type"] = resolve_obj.type
        bind_obj = self.args_handle(request)
        if domain_obj.resolve.filter(name=resolve_obj.name, type=resolve_obj.type, address=new_address).exclude(
                id=resolve_obj.id).exists():
            return Response({"code": ResponseMessage.DataExistsError, "msg": "解析记录已存在"})
        resolves = domain_obj.resolve.filter(name=resolve_obj.name, type=resolve_obj.type).exclude(
            address=resolve_obj.address)
        address = [i.address for i in resolves]
        address.append(new_address)
        resolve_obj.address = new_address
        resolve_obj.mx = mx
        if not bind_obj.replace(*address, name=resolve_obj.name, ttl=ttl, domain_type=resolve_obj.type, mx=mx):
            return Response({"code": ResponseMessage.Failed, "msg": "解析修改失败"})
        resolve_obj.save()
        resolves.update(mx=mx, ttl=ttl)
        msg = "域名:{domain}修改解析:{name}记录类型为:{type},地址:{address}!".format(**{
            "domain": domain_obj.domain,
            "name": resolve_obj.name,
            "type": resolve_obj.type,
            "address": address
        })
        models.Log(username=str(request.user), event=LogCode.Resolve, content=msg).save()
        return Response({"code": ResponseMessage.Success, "msg": "解析修改完成"})

    def delete_or_stop(self, request):
        domain_obj = self.domain_is_exists(request.data["domain"])
        if domain_obj is None:
            return None, None, Response({
                "code": ResponseMessage.DataNoExistsError,
                "msg": "域名:{domain}不存在".format(domain=request.data["domain"])
            })
        try:
            resolve_obj = domain_obj.resolve.get(id=request.data["resolve_id"])
        except (models.Resolve.DoesNotExist, KeyError):
            return None, None, Response({"code": ResponseMessage.DataNoExistsError, "msg": "解析记录不存在"})
        return self.args_handle(request, is_delete=True), resolve_obj, None

    @action(detail=False, methods=["POST"], url_path='delete')
    def delete(self, request, *args, **kwargs):
        try:
            bind_obj, resolve_obj, msg = self.delete_or_stop(request)
        except KeyError as key:
            return Response({"code": ResponseMessage.ArgsError, "msg": "缺少参数{key}".format(key=key)})
        if bind_obj is None:
            return msg
        if not bind_obj.delete(resolve_obj.name, resolve_obj.type, resolve_obj.address, resolve_obj.ttl):
            return Response({"code": ResponseMessage.Failed, "msg": "删除解析失败"})
        msg = "域名:{domain}删除解析:{name}记录类型为:{type},地址:{address}!".format(**{
            "domain": request.data["domain"],
            "name": resolve_obj.name,
            "type": resolve_obj.type,
            "address": resolve_obj.address
        })
        models.Log(username=str(request.user), event=LogCode.Resolve, content=msg).save()
        resolve_obj.delete()
        return Response({"code": ResponseMessage.Success, "msg": "删除解析完成"})

    @action(detail=False, methods=["POST"], url_path='stop')
    def stop(self, request, *args, **kwargs):
        try:
            bind_obj, resolve_obj, msg = self.delete_or_stop(request)
            is_active = request.data["is_active"]
        except KeyError as key:
            return Response({"code": ResponseMessage.ArgsError, "msg": "缺少参数{key}".format(key=key)})
        if bind_obj is None:
            return msg
        if is_active:
            if not bind_obj.add(
                    name=resolve_obj.name,
                    ttl=resolve_obj.ttl,
                    domain_type=resolve_obj.type,
                    host=resolve_obj.address,
                    mx=resolve_obj.mx
            ):
                return Response({"code": ResponseMessage.Failed, "msg": "激活解析失败"})
        else:
            if not bind_obj.delete(resolve_obj.name, resolve_obj.type, resolve_obj.address, resolve_obj.ttl):
                return Response({"code": ResponseMessage.Failed, "msg": "停止解析失败"})
        msg = "域名:{domain}{title}解析:{name}记录类型为:{type},地址:{address}!".format(**{
            "domain": request.data["domain"],
            "title": "激活" if is_active else "停止",
            "name": resolve_obj.name,
            "type": resolve_obj.type,
            "address": resolve_obj.address
        })
        models.Log(username=str(request.user), event=LogCode.Resolve, content=msg).save()
        resolve_obj.is_active = is_active
        resolve_obj.save()
        return Response({"code": ResponseMessage.Success, "msg": "{}解析完成".format("激活" if is_active else "停止")})
