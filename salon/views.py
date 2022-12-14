from django.contrib.auth import login, user_logged_out
from django.http import JsonResponse
from django.shortcuts import render
from knox.models import AuthToken
from rest_framework import generics, status, permissions, viewsets
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from knox.views import LoginView as KnoxLoginView
from knox.auth import TokenAuthentication
from knox import views as knox_views

from salon.csrf import CsrfExemptSessionAuthentication
from salon.permissions import *
from salon.models import Service
from salon.serializers import *

#login po email. username change on email
class AuthTokenSerializer(AuthTokenSerializer):
    username = None
    email = serializers.EmailField(label="Email", write_only=True)
    password = serializers.CharField(label="Password", style={'input_time': "password"}, trim_whitespace=False,
                                     write_only=True)
    token = serializers.CharField(label="Token", read_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('reqeust'), email=email, password=password)

            if not user:
                msg = ('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = ('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        attrs['user'] = user
        return attrs


class UserViewSet(ListCreateAPIView):
    serializer_class = UserSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        user = User.objects.filter(**serializer.data).first()
        return Response({"token": AuthToken.objects.create(user)[1]}, status=status.HTTP_201_CREATED, headers=headers)


class LoginView(KnoxLoginView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = (TokenAuthentication,)
    serializer_class = LoginSerializer

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None)

    def get_post_response_data(self, request, token, instance):
        UserSerializer = self.get_user_serializer_class()

        data = {
            'token': token
        }

        dataReturn = {
            'token': token
        }

        if UserSerializer is not None:
            data["user"] = UserSerializer(request.user, context=self.get_context()).data

        return dataReturn


class LogoutView(knox_views.LogoutView):
    authentication_classes = (TokenAuthentication,)

    def post(self, request, format=None):
        request._auth.delete()
        user_logged_out.send(sender=request.user.__class__, request=request, user=request.user)
        return Response({"message": "Log Out"}, status=status.HTTP_204_NO_CONTENT)


class ServicesView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        services = Service.objects.all()
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)


class CreateServiceView(generics.CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAdminUser]
    queryset = Service.objects.all()
    serializer_class = CreateServiceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = serializer.save()
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response({"id": service.id, "message": "Service added"}, status=status.HTTP_201_CREATED, headers=headers)


class UpdateServiceView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = (TokenAuthentication,)
    queryset = Service.objects.all()
    serializer_class = CreateServiceSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        instance = self.get_object();
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, safe=False)

        else:
            return Response({"message": "failed", "details": serializer.errors})


class DeleteServiceView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = (TokenAuthentication,)
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Service removed"}, status=status.HTTP_200_OK)


class CartView(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return Cart.objects.filter(owner=self.request.user)

    serializer_class = CartSerializer


class CreateCartView(generics.CreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CreateServiceSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"message": '??????????????'}, status=status.HTTP_201_CREATED, headers=headers)


class AddCartView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Service add to card"})

        else:
            return Response({"message": "failed", "details": serializer.errors})


class AddServiceView(RetrieveAPIView):
    serializer_class = ServiceSerializer
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return Service.objects.all()

    def retrieve(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(owner=self.request.user, is_active=True)
        cart.services.add(self.get_object())
        return Response({"message": "Service add to card"}, status=status.HTTP_201_CREATED)


class DeleteServiceFromCart(generics.DestroyAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        cart = Cart.objects.filter(owner=self.request.user, is_active=True).first()
        return cart.services.all()

    def destroy(self, request, *args, **kwargs):
        cart = Cart.objects.filter(owner=self.request.user, is_active=True).first()
        cart.services.remove(self.get_object())
        return Response({"message": "Item removed from cart"}, status=status.HTTP_204_NO_CONTENT)


class OrderView(viewsets.ModelViewSet):

    def get_queryset(self):
        return Order.objects.filter(owner=self.request.user)

    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer



class CreateOrderView(generics.CreateAPIView):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CreateOrderSerializer
    authentication_classes = (TokenAuthentication,)

    def perform_create(self, serializer):
        cart = Cart.objects.filter(owner=self.request.user, is_active=True).first()
        if cart is not None:
            services = cart.services.all()
            cart_data = cart.services.aggregate(models.Sum('price'), models.Count('id'))
            if cart_data.get('price__sum'):
                price_sum = cart_data['price__sum']
            else:
                price_sum = 0

            serializer.save(owner=self.request.user, services=services, sum=price_sum)
            cart.is_active = False
            cart.save()

    def create(self, request, *args, **kwargs):
        cart = Cart.objects.filter(owner=self.request.user, is_active=True).first()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        if cart is None:
            return Response({"message": "Cart is empty"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY, headers=headers)
        return Response({"message": "Order is processed"}, status=status.HTTP_201_CREATED, headers=headers)


