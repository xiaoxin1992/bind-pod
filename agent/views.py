from rest_framework import viewsets
from . import serializers
from rest_framework import mixins
from . import filters
from django_filters.rest_framework import DjangoFilterBackend
from .lib2.resolveViews import Resolve
from .lib2.domainViews import Domain
from . import models
from utils import permissions
from django.contrib.auth.models import User
from .lib2.userViews import UserView


class LogView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    域名管理
    """
    permission_classes = [permissions.UserPermission]
    serializer_class = serializers.LogSerializer
    queryset = models.Log.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_class = filters.LogFilter

    def get_queryset(self):
        return self.queryset.all().order_by("-create_time")


class DomainView(Domain, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    域名管理
    """
    permission_classes = [permissions.UserPermission]
    serializer_class = serializers.DomainSerializer
    queryset = models.Domain.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_class = filters.DomainFilter

    def get_serializer_class(self):
        if self.action == "delete":
            return serializers.DomainDeleteSerializer
        return serializers.DomainSerializer


class ResolveView(Resolve, viewsets.GenericViewSet):
    """
    解析记录操作
    """
    permission_classes = [permissions.UserPermission]
    serializer_class = serializers.ResolveSerializer
    queryset = models.Resolve.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_class = filters.ResolveFilter

    def get_queryset(self):
        return self.queryset.all().order_by("-create_time")

    def get_serializer_class(self):
        if self.action == "delete":
            return serializers.ResolveDeleteSerializer
        elif self.action == "modify":
            return serializers.ResolveEditSerializer
        elif self.action == "stop":
            return serializers.ResolveStopSerializer
        return serializers.ResolveSerializer


class UserView(UserView, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    解析记录操作
    """
    permission_classes = [permissions.UserPermission]
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_class = filters.UserFilter

    def get_serializer_class(self):
        if self.action == "delete":
            return serializers.UserDeleteSerializer
        if self.action == "domain":
            return serializers.UserDomainGetSerializer
        elif self.action == "active":
            return serializers.UserActiveSerializer
        elif self.action == "password":
            return serializers.UserPasswordSerializer
        elif self.action in ["add_domain", "add_remove"]:
            return serializers.UserDomainSerializer
        return serializers.UserSerializer
