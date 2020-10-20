import django_filters
from . import models
from django.contrib.auth.models import User


class DomainFilter(django_filters.FilterSet):
    domain = django_filters.CharFilter(field_name="domain", lookup_expr='icontains')

    class Meta:
        models = models.Domain
        fields = ["domain"]


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name="username", lookup_expr='icontains')

    class Meta:
        models = User
        fields = ["username"]


class ResolveFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        models = models.Resolve
        fields = ["name"]


class LogFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name="username", lookup_expr='icontains')
    event = django_filters.CharFilter(field_name="event")
    start_time = django_filters.DateTimeFilter(field_name="create_time", lookup_expr="gte")
    end_time = django_filters.DateTimeFilter(field_name="create_time", lookup_expr="lte")

    class Meta:
        models = models.Log
        fields = ["username", "event", "start_time", "end_time"]
