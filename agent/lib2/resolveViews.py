from IPy import IP
from django.conf import settings
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
import re
from .dns_lib import Bind
from .. import models

'''
错误代码: code
801      参数错误
805      数据格式错误
810      数据已经存在
204      操作失败
200      操作成功
'''


class SerializerVerificationCheck:
    """
    检查Serializer参数是否正常
    """

    @staticmethod
    def serializer_ver(serializer):
        serializer_check = serializer.is_valid(raise_exception=False)
        if not serializer_check:
            key = [i for i in serializer.errors][0]
            raise ValidationError({"code": 801, "msg": "{field} {msg}".format(field=key, msg=serializer.errors[key])})


class VerificationResolve:
    def __init__(self, name, address):
        self.name = name
        self.address = address

    @property
    def ver_domain(self):
        pattern = re.compile(
            r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
            r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})\.$'
        )
        if pattern.match(self.address):
            return True
        else:
            return False

    def ver_address(self, version=4):
        try:
            ip_obj = IP(self.address)
            return True if ip_obj.version() == version else False
        except ValueError:
            return False

    def cname(self):
        if not self.ver_domain:
            raise ValidationError({"code": 805, "msg": "CNAME必须是一个完整的域名"})

    def ipv4(self):
        if not self.ver_address(version=4):
            raise ValidationError({"code": 805, "msg": "A类型必须是一个合法的IPV4地址"})

    def ipv6(self):
        if not self.ver_address(version=4):
            raise ValidationError({"code": 805, "msg": "AAAA类型必须是一个合法的IPV6地址"})

    def ns(self):
        if not self.ver_address(4) and not self.ver_address(6) and not self.ver_domain:
            raise ValueError({"code": 805, "msg": "ns记录必须是一个IP地址或者域名"})

    def mx(self):
        if self.name.strip() != "@":
            raise ValidationError({"code": 805, "msg": "MX类型名称必须是@"})
        if not self.ver_domain:
            raise ValidationError({"code": 805, "msg": "MX记录必须填写完整的域名"})


class Resolve(SerializerVerificationCheck):

    def bind(self, server, key, code, domain, port=53):
        allow_type = getattr(settings, "ALLOW_DNS_TYPE")
        return Bind(server=server, key=key, code=code, domain=domain, port=port, allow_type=allow_type)

    def verification_handle(self, request):
        self.serializer_ver(self.get_serializer(data=request.data))
        self.verification()

    @staticmethod
    def is_mx(resolve_type, mx, address):
        if resolve_type.upper() in "MX":
            return "{mx} {address}".format(address=address, mx=5 if mx < 5 else mx)
        else:
            return address

    def verification(self):
        if self.request.data["type"].upper() == "MX":
            address = self.request.data["address"]
            self.request.data["address"] = "{address}.".format(address=address) if address[-1] != "." else address
        ver = VerificationResolve(self.request.data["name"], self.request.data["address"])
        self.verification_data(ver, self.request.data["type"])

    @staticmethod
    def verification_data(ver_obj, resolve_type):
        if resolve_type.upper() == "AAAA":
            ver_obj.ipv6()
        elif resolve_type.upper() == "A":
            ver_obj.ipv4()
        elif resolve_type.upper() == "NS":
            ver_obj.ns()
        elif resolve_type.upper() == "CNAME":
            ver_obj.cname()
        elif resolve_type.upper() == "TXT":
            pass
        elif resolve_type.upper() == "MX":
            ver_obj.mx()
        else:
            raise ValidationError({"code": 805, "msg": "不支持的解析类型:{type}".format(type=resolve_type)})

    def args_handle(self, request):
        self.verification_handle(request)
        name = request.data["name"]
        mx = int(request.data.get("mx", 0))
        ttl = request.data["ttl"]
        address = request.data["address"]
        resolve_type = request.data["type"]
        config = getattr(settings, "DNS_BASE_CONFIG")
        bind_obj = self.bind(
            server=config.get("server", "127.0.0.1"),
            key=config["key"],
            code=config["secret"],
            domain=request.data["domain"],
            port=int(config.get("port", 53)),
        )
        sub_host = self.is_mx(resolve_type, mx, address)
        return bind_obj, sub_host, name, ttl, resolve_type

    @action(detail=False, methods=["POST"], url_path='create')
    def add(self, request, *args, **kwargs):
        try:
            domain_obj = models.Domain.objects.get(domain=request.data["domain"])
        except models.Domain.DoesNotExist:
            return Response({"code": 805, "msg": "域名:{domain}不存在".format(domain=request.data["domain"])})
        bind_obj, sub_host, name, ttl, resolve_type = self.args_handle(request)
        try:
            domain_obj.resolve.get(name=name, type=resolve_type, address=sub_host)
            return Response({"code": 810, "msg": "解析已经存在"})
        except models.Resolve.DoesNotExist:
            if not bind_obj.add(name=name, ttl=ttl, domain_type=resolve_type, host=sub_host):
                return Response({"code": 204, "msg": "创建解析失败"})
            if not bind_obj.save():
                return Response({"code": 204, "msg": "保存解析到服务器失败"})
            domain_obj.resolve.create(name=name, type=resolve_type, address=request.data["address"],
                                      mx=request.data["mx"], ttl=ttl)
        msg = "域名:{domain}增加解析:{name}记录类型为:{type},地址:{address}!".format(**{
            "domain": domain_obj.resolve,
            "name": name,
            "type": request.data["mx"],
            "address": request.data["address"]
        })
        models.Log(username=str(request.user), event=2, content=msg).save()
        return Response({"code": 200, "msg": "解析添加成功"})

    @action(detail=False, methods=["GET"], url_path='list/(?P<domain>[a-z.]+)')
    def get(self, request, *args, **kwargs):
        try:
            domain_obj = models.Domain.objects.get(domain=kwargs["domain"])
            queryset = domain_obj.resolve.all()
        except (models.Domain.DoesNotExist, KeyError):
            queryset = []
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["POST"], url_path='modify')
    def modify(self, request, *args, **kwargs):
        try:
            domain_obj = models.Domain.objects.get(domain=request.data["domain"])
        except (models.Domain.DoesNotExist, KeyError):
            return Response({"code": 805, "msg": "域名:{domain}不存在".format(domain=request.data["domain"])})
        try:
            resolve_obj = domain_obj.resolve.get(id=int(request.data["resolve_id"]))
        except (models.Resolve.DoesNotExist, KeyError):
            return Response({"code": 805, "msg": "解析记录不存在"})
        resolves = domain_obj.resolve.filter(name=resolve_obj.name, type=resolve_obj.type)
        address = [i.address for i in resolves if i.address != resolve_obj.address]
        modify_address = request.data["address"]
        request.data["name"] = resolve_obj.name
        request.data["type"] = resolve_obj.type
        bind_obj, sub_host, name, ttl, resolve_type = self.args_handle(request)
        address.append(sub_host)
        if not bind_obj.replace(name, ttl, resolve_type, *address):
            return Response({"code": 1002, "msg": "当前解析修改失败"})
        if not bind_obj.save():
            return Response({"code": 1003, "msg": "保存解析到服务器失败"})
        resolve_obj.address = modify_address
        resolve_obj.save()
        resolves.update(
            mx=request.data["mx"],
            ttl=request.data["ttl"],
        )
        msg = "域名:{domain}修改解析:{name}记录类型为:{type},地址:{address}!".format(**{
            "domain": domain_obj.resolve,
            "name": name,
            "type": request.data["mx"],
            "address": request.data["address"]
        })
        models.Log(username=str(request.user), event=2, content=msg).save()
        return Response({"code": 200, "msg": "解析修改完成"})

    @action(detail=False, methods=["POST"], url_path='delete')
    def delete(self, request, *args, **kwargs):
        try:
            domain_obj = models.Domain.objects.get(domain=request.data["domain"])
        except (models.Domain.DoesNotExist, KeyError):
            return Response({"code": 805, "msg": "域名:{domain}不存在".format(domain=request.data["domain"])})
        try:
            resolve_obj = domain_obj.resolve.get(id=request.data["resolve_id"])
        except (models.Resolve.DoesNotExist, KeyError):
            return Response({"code": 805, "msg": "解析记录不存在"})
        request.data["name"] = resolve_obj.name
        request.data["ttl"] = resolve_obj.ttl
        request.data["type"] = resolve_obj.type
        request.data["mx"] = resolve_obj.mx
        request.data["address"] = resolve_obj.address
        bind_obj, sub_host, name, ttl, resolve_type = self.args_handle(request)
        if not bind_obj.delete(name, resolve_type, sub_host, ttl):
            return Response({"code": 204, "msg": "删除解析失败"})
        if not bind_obj.save():
            return Response({"code": 204, "msg": "保存解析到服务器失败"})
        msg = "域名:{domain}删除解析:{name}记录类型为:{type},地址:{address}!".format(**{
            "domain": domain_obj.resolve,
            "name": name,
            "type": request.data["mx"],
            "address": request.data["address"]
        })
        models.Log(username=str(request.user), event=2, content=msg).save()
        resolve_obj.delete()
        return Response({"code": 200, "msg": "删除解析完成"})

    @action(detail=False, methods=["POST"], url_path='stop')
    def stop(self, request, *args, **kwargs):
        try:
            domain_obj = models.Domain.objects.get(domain=request.data["domain"])
            resolve_obj = domain_obj.resolve.get(id=request.data["resolve_id"])
            is_active = request.data["is_active"]
        except models.Domain.DoesNotExist:
            return Response({"code": 805, "msg": "域名:{domain}不存在".format(domain=request.data["domain"])})
        except models.Resolve.DoesNotExist:
            return Response({"code": 805, "msg": "解析记录不存在"})
        except KeyError as key:
            return Response({"code": 801, "msg": "缺少:{key}参数".format(key=key)})
        request.data["name"] = resolve_obj.name
        request.data["ttl"] = resolve_obj.ttl
        request.data["type"] = resolve_obj.type
        request.data["mx"] = resolve_obj.mx
        request.data["address"] = resolve_obj.address
        bind_obj, sub_host, name, ttl, resolve_type = self.args_handle(request)
        if is_active:
            if not bind_obj.add(name=name, ttl=ttl, domain_type=resolve_type, host=sub_host):
                return Response({"code": 204, "msg": "激活解析失败"})
            title = "激活"
        else:
            if not bind_obj.delete(name, resolve_type, sub_host, ttl):
                return Response({"code": 204, "msg": "停止解析失败"})
            title = "停止"
        msg = "域名:{domain}{title}解析:{name}记录类型为:{type},地址:{address}!".format(**{
            "domain": domain_obj.resolve,
            "title": title,
            "name": name,
            "type": request.data["mx"],
            "address": request.data["address"]
        })
        if not bind_obj.save():
            return Response({"code": 204, "msg": "保存解析到服务器失败"})
        models.Log(username=str(request.user), event=2, content=msg).save()
        resolve_obj.is_active = is_active
        resolve_obj.save()
        return Response({"code": 200, "msg": "{title}解析完成".format(title=title)})
