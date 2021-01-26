from rest_framework.decorators import action
from rest_framework.response import Response
from ..lib2 import named
from ..lib2.codes import ResponseMessage, LogCode
from ..lib2.verification_tools import Verification
from .. import models
import os


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
        return Response({"code": ResponseMessage.Success, "data": {
            "domain_total": domain_total,
            "analysis_active_total": analysis_active_total,
            "analysis_stop_total": analysis_stop_total}})

    @action(detail=False, methods=["POST"], url_path='create')
    def add(self, request, *args, **kwargs):
        """添加域名"""
        try:
            domain = request.data['domain'].strip()
            path = request.data['path'].strip()
        except KeyError as args:
            return Response({"code": ResponseMessage.ArgsError, "msg": "缺少: {key}".format(key=args)})
        if not Verification.is_domain(domain):
            return Response({"code": ResponseMessage.DataError, "msg": "域名格式错误，请输入正确的域名!"})
        if not os.path.exists(path) or not os.path.isfile(path):
            return Response({"code": ResponseMessage.DataError, "msg": "区域文件路径错误，请检查文件是否存在，文件路径必须是已存在的绝对路径!"})
        resolves_data = named.Zone.read(path, domain)
        if len(resolves_data) == 0:
            return Response({"code": ResponseMessage.DataError, "msg": "解析区域文件错误，请检查文件是否存在或者权限是否正确!"})
        try:
            models.Domain.objects.get(domain=domain)
            return Response({"code": ResponseMessage.DataExistsError, "msg": "域名:{domain}已经存在!".format(domain=domain)})
        except models.Domain.DoesNotExist:
            domain_obj = models.Domain.objects.create(domain=domain, path=path)
            for resolve in resolves_data:
                domain_obj.resolve.create(
                    name=resolve["name"],
                    type=resolve["type"],
                    mx=int(resolve["mx"]),
                    ttl=resolve["ttl"],  # 86400
                    address=resolve["ip"])
        msg = '域名:"{domain}"创建成功!'.format(domain=domain)
        models.Log(username=str(request.user), event=LogCode.Domain, content=msg).save()
        return Response({"code": ResponseMessage.Success, "msg": msg})

    @action(detail=False, methods=["POST"], url_path='delete')
    def delete(self, request, *args, **kwargs):
        delete_obj = models.Domain.objects.filter(domain__in=request.data["domain"])
        if not delete_obj.exists():
            return Response({
                "code": ResponseMessage.DataError,
                "msg": "请选择域名!"
            })
        for domain in delete_obj:
            msg = '域名:"{domain}"删除成功!'.format(domain=domain)
            models.Log(username=str(request.user), event=1, content=msg).save()
        delete_obj.delete()
        return Response({"code": ResponseMessage.Success, "msg": "域名删除完成!"})
