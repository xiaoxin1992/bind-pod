from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Domain(models.Model):
    domain = models.CharField(max_length=128, unique=True, help_text="域名")
    path = models.CharField(max_length=255, help_text="域名区域文件路径")
    create_time = models.DateField(auto_now=True, help_text="添加时间")
    user = models.ManyToManyField(User, related_name="domain", verbose_name="用户")


class Resolve(models.Model):
    name = models.CharField(max_length=128, help_text="名称")
    type = models.CharField(max_length=20, help_text="解析类型")
    mx = models.IntegerField(default=0, help_text="MX优先级")
    ttl = models.IntegerField(default=600, help_text="TTL值")
    address = models.CharField(max_length=128, help_text="地址")
    is_active = models.BooleanField(max_length=128, help_text="域名状态", default=True)
    domain = models.ForeignKey(Domain, related_name="resolve", on_delete=models.CASCADE)
    create_time = models.DateField(auto_now=True, help_text="添加时间")


class Log(models.Model):
    CHOICES_EVENT = (
        (0, "登陆"),
        (1, "域名"),
        (2, "解析"),
        (3, "用户")
    )
    username = models.CharField(max_length=128, help_text="操作账号")
    event = models.IntegerField(choices=CHOICES_EVENT, default=0, help_text="操作事件")
    create_time = models.DateField(auto_now=True, help_text="操作时间")
    content = models.CharField(max_length=256, help_text="事件内容")