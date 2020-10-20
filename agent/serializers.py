from rest_framework import serializers
from . import models
from django.contrib.auth.models import User


class LogSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        return {
            "username": instance.username,
            "event": instance.get_event_display(),
            "content": instance.content,
            "create_time": instance.create_time,
        }

    class Meta:
        model = models.Log
        fields = "__all__"


class DomainSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        return {
            "id": instance.id,
            "domain": instance.domain,
            "path": instance.path,
            "analysis": len(instance.resolve.all()),
            # "users": [user.username for user in instance.user.all()],
            "create_time": instance.create_time
        }

    class Meta:
        model = models.Domain
        fields = ["domain", "path"]


class DomainDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Domain
        fields = ["domain"]


class ResolveSerializer(serializers.ModelSerializer):
    domain = serializers.CharField(max_length=128, help_text="域名")
    name = serializers.CharField(max_length=128, help_text="解析名称")
    mx = serializers.IntegerField(default=0, help_text="MX值")
    ttl = serializers.IntegerField(default=3600, help_text="TTL值")
    address = serializers.CharField(max_length=128, help_text="解析地址")
    type = serializers.CharField(max_length=10, help_text="解析类型")

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "name": instance.name,
            "mx": instance.mx,
            "ttl": instance.ttl,
            "address": instance.address,
            "type": instance.type,
            "is_active": instance.is_active,
            "create_time": instance.create_time
        }

    class Meta:
        model = models.Resolve
        fields = ["domain", "name", "mx", "ttl", "address", "type"]


class ResolveEditSerializer(serializers.ModelSerializer):
    domain = serializers.CharField(max_length=128, help_text="域名")
    resolve_id = serializers.IntegerField(help_text="解析ID")
    mx = serializers.IntegerField(default=0, help_text="MX值")
    ttl = serializers.IntegerField(default=3600, help_text="TTL值")
    address = serializers.CharField(max_length=255, help_text="解析地址")

    class Meta:
        model = models.Resolve
        fields = ["domain", "resolve_id", "mx", "ttl", "address"]


class ResolveStopSerializer(serializers.ModelSerializer):
    domain = serializers.CharField(max_length=128, help_text="域名")
    resolve_id = serializers.IntegerField(help_text="解析ID")
    is_active = serializers.BooleanField(help_text="是否激活")

    class Meta:
        model = models.Resolve
        fields = ["domain", "resolve_id", "is_active"]


class ResolveDeleteSerializer(serializers.ModelSerializer):
    domain = serializers.CharField(max_length=128, help_text="域名")
    resolve_id = serializers.IntegerField(help_text="解析ID")

    class Meta:
        model = models.Resolve
        fields = ["domain", "resolve_id"]


class UserSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "username": instance.username,
            "is_superuser": instance.is_superuser,
            "first_name": instance.first_name,
            "email": instance.email,
            "is_active": instance.is_active,
            "create_time": instance.date_joined.strftime("%Y-%m-%d"),
            "domain": [{"id": domain.id, "domain": domain.domain} for domain in instance.domain.all()]
        }

    class Meta:
        model = User
        fields = ["username", "is_superuser", "first_name", "email", "password"]


class UserPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password"]


class UserDeleteSerializer(serializers.ModelSerializer):
    username = serializers.ListField(help_text="用户名列表")

    class Meta:
        model = User
        fields = ["username"]


class UserActiveSerializer(serializers.ModelSerializer):
    active = serializers.BooleanField(help_text="是否激活")

    class Meta:
        model = User
        fields = ["username", "active"]


class UserChangeSerializer(serializers.ModelSerializer):
    password = serializers.CharField(help_text="新密码")

    class Meta:
        model = User
        fields = ["username", "password"]


class UserDomainSerializer(serializers.ModelSerializer):
    domain = serializers.CharField(max_length=128, help_text="域名")

    class Meta:
        model = User
        fields = ["username", "domain"]


class UserDomainGetSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            "domain": instance.domain,
            "is_user": [user.username for user in instance.user.all()]
        }

    class Meta:
        model = models.Domain
        fields = ["username"]
