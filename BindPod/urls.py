"""BindPod URL Configuration

The `urlpatterns` list routes URLs to views_lib. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views_lib
    1. Add an import:  from my_app import views_lib
    2. Add a URL to urlpatterns:  path('', views_lib.home, name='home')
Class-based views_lib
    1. Add an import:  from other_app.views_lib import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from rest_framework import routers

from BindPod.login_view import LoginView, LogoutView
from agent import views

agent_router = routers.DefaultRouter()
api_router = routers.DefaultRouter()

agent_router.register(r'domain', views.DomainView)
agent_router.register(r'resolve', views.ResolveView)

agent_router.register(r'log', views.LogView)
agent_router.register(r'user', views.UserView)


api_router.register(r'domain', views.DomainView)
api_router.register(r'log', views.LogView)
api_router.register(r'resolve', views.ResolveView)
api_router.register(r'user', views.UserView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('agent/', include(agent_router.urls)),
    path('api/', include(api_router.urls)),
    path('docs/', include_docs_urls(title='BindPod', authentication_classes=[], permission_classes=[])),
    path(r'login/', LoginView.as_view(), name='token_obtain_pair'),
    path(r'logout/', LogoutView.as_view(), name='token_obtain_pair'),
]
