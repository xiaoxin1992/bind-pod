from django.conf import settings
from rest_framework.decorators import action
from rest_framework.response import Response
from . import dns_lib
from .. import models
import re
import os
from utils import logs

'''
错误代码: code
801      参数错误
805      数据格式错误
810      数据已经存在
200      操作成功
'''


class Domain:
    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.Domain.objects.all().order_by("-create_time")
        else:
            return models.Domain.objects.filter(user__username=self.request.user.username).order_by("-create_time")

    @action(detail=False, methods=["GET"], url_path='info')
    def get_info(self, request, *args, **kwargs):
        domain_total = len(models.Domain.objects.all())
        analysis_active_total = len(models.Resolve.objects.filter(is_active=True))
        analysis_stop_total = len(models.Resolve.objects.filter(is_active=False))
        return Response({"code": 200, "data": {
            "domain_total": domain_total,
            "analysis_active_total": analysis_active_total,
            "analysis_stop_total": analysis_stop_total
        }})

    @action(detail=False, methods=["POST"], url_path='create')
    def add(self, request, *args, **kwargs):
        """添加域名"""
        try:
            domain = request.data['domain'].strip()
            path = request.data['path'].strip()
        except KeyError as args:
            return Response({"code": 801, "msg": "缺少: {key}".format(key=args)})
        pattern = r'^(?=^.{3,255}$)[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+$'
        if re.match(pattern, domain) is None:
            return Response({"code": 805, "msg": "域名格式错误，请输入正确的域名!"})
        if not os.path.exists(path) or not os.path.isfile(path):
            return Response({"code": 805, "msg": "区域文件路径错误，请检查文件是否存在，文件路径必须是已存在的绝对路径!"})
        try:
            resolve_obj = dns_lib.DomainResolve(path, domain, getattr(settings, "ALLOW_DNS_TYPE"))
            resolves = resolve_obj.resolve_list
        except Exception as error:
            logs.print(str(error), "error")
            return Response({"code": 805, "msg": "解析区域文件错误，请检查文件是否存在或者权限是否正确!"})
        try:
            models.Domain.objects.get(domain=domain)
            return Response({"code": 810, "msg": "域名:{domain}已经存在!".format(domain=domain)})
        except models.Domain.DoesNotExist:
            domain_obj = models.Domain.objects.create(
                domain=domain,
                path=path,
            )
            for resolve in resolves:
                if resolve["type"] == "MX":
                    mx, address = resolve["ip"].strip().split()
                else:
                    address = resolve["ip"]
                    mx = 0
                domain_obj.resolve.create(
                    name=resolve["name"],
                    type=resolve["type"],
                    mx=int(mx),
                    ttl=resolve["ttl"],  # 86400
                    address=address.strip(),
                )
        msg = "域名:{domain}创建成功!".format(domain=domain)
        models.Log(username=str(request.user), event=1, content=msg).save()
        return Response({"code": 200, "msg": msg})

    @action(detail=False, methods=["POST"], url_path='delete')
    def delete(self, request, *args, **kwargs):
        try:
            domain = request.data["domain"]
        except models.Domain.DoesNotExist:
            return Response({"code": 801, "msg": "缺少: {key}".format(key=args)})
        try:
            models.Domain.objects.get(domain=domain).delete()
        except models.Domain.DoesNotExist:
            return Response({"code": 805, "msg": "域名:{domain}不存在!".format(domain=domain)})
        msg = "域名:{domain}删除完成!".format(domain=domain)
        models.Log(username=str(request.user), event=1, content=msg).save()
        return Response({"code": 200, "msg": msg})
