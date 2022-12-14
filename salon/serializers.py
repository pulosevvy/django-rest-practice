from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueValidator

from salon.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password')


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password],
                                     style={'input_type': 'password'})
    fio = serializers.RegexField(regex=r'^[а-яА-ЯёЁ\s-]+$', max_length=250, required=True)

    class Meta:
        model = User
        fields = (
            'email',
            'fio',
            'password',
        )

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            fio=validated_data['fio'],
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class LoginSerializer(ModelSerializer):
    username_field = 'email'

    username = serializers.EmailField(required=True, max_length=255)
    password = serializers.CharField(max_length=150, write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email', None),
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError('An email address is required!')
        if password is None:
            raise serializers.ValidationError('A password is required!')

        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError('A user with this email and password was not found!')
        return {
            'email': user.email,
        }

    class Meta:
        model = User
        fields = (
            'username',
            'password'
        )


# ServiceSerializer
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'name', 'description', 'price')


class CreateServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('__all__')


# CartSerializer
class CartSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(read_only=True, many=True)

    class Meta:
        model = Cart
        fields = ('id', 'services',)


class CreateCartSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('services',)


# Order
class OrderSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(read_only=True, many=True)

    class Meta:
        model = Order
        fields = ('id', 'services',)


class CreateOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('message',)
