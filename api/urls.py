"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from . import views, login, viewsNews, viewsOrganization, viewsInspection
from rest_framework.routers import DefaultRouter
from .login import LoginViewSet

app_name = 'api'

router = DefaultRouter()
router.register('', LoginViewSet, basename='login')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.jwt')),
    path('healthcheck', views.healthcheck),
    path('login', login.LoginViewSet.as_view({'post': 'login'})),
    path('register', views.UserRegistrationView.as_view()),
    path('news', viewsNews.allNews),
    path('news/<int:id>', viewsNews.oneNews),
    path('organization', viewsOrganization.getOrganization),
    path('organization/new', viewsOrganization.newOrganization),
    path('organization/<int:id>', viewsOrganization.getOneOrganization),
    path('organization/<int:id>/permission', viewsOrganization.organizationPermission),
    path('organization/<int:id>/edit', viewsOrganization.editOrganization),
    path('organization/<int:id>/delete', viewsOrganization.deleteOrganization),
    path('organization/<int:id>/news', viewsNews.organizationNews),
    path('organization/<int:id>/news/new', viewsNews.newNews),
    path('organization/<int:id>/news/<int:news_id>', viewsNews.oneOrganizationNews),
    path('organization/<int:id>/news/<int:news_id>/delete', viewsNews.deleteOrganizationNews),
    path('organization/<int:id>/member', viewsOrganization.getOrganizationUsers),
    path('organization/<int:id>/member/new', viewsOrganization.addOrganizationUser),
    path('organization/<int:id>/member/<int:user_id>', viewsOrganization.getOrganizationUsersPermission),
    path('organization/<int:id>/member/<int:user_id>/delete', viewsOrganization.deleteOrganizationUser),
    path('organization/<int:id>/member/<int:user_id>/change_owner', viewsOrganization.changeOwner),
    path('organization/<int:id>/inspection', viewsInspection.inspection),
    path('organization/<int:id>/inspection/<slug:category>/<int:item_id>', viewsInspection.inspect),
]
