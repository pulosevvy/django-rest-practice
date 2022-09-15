"""rest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from salon.views import *
from rest_framework.routers import DefaultRouter
from knox import views as knox_views

router = DefaultRouter()
router.register(r'user', UserViewSet, basename='User')

urlpatterns = [
    # admin
    path('admin/', admin.site.urls),

    # register/login/logout
    path('api/register/', RegisterView.as_view()),
    path('api/login/', LoginView.as_view()),
    path('api/logout/', LogoutView.as_view()),

    # Services
    path('api/services/', ServicesView.as_view()),
    path('api/createservices/', CreateServiceView.as_view()),
    path('api/updateservices/<int:pk>/', UpdateServiceView.as_view()),
    path('api/deleteservices/<int:pk>/', DeleteServiceView.as_view()),

    # Cart
    path('api/cart/', CartView.as_view({'get': 'list'})),
    path('api/cart/<int:pk>/', AddServiceView.as_view()),
    path('api/deletecart/<int:pk>/', DeleteServiceFromCart.as_view()),

    # Order
    path('api/orders/', OrderView.as_view({'get': 'list'})),
    path('api/createorders/', CreateOrderView.as_view()),

]
