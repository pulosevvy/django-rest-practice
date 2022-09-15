from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(max_length=128, null=True, blank=True)
    fio = models.CharField(max_length=128, null=False, verbose_name='ФИО')
    email = models.EmailField('email', unique=True, null=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Service(models.Model):
    name = models.CharField(max_length=100, null=False)
    description = models.TextField(null=False)
    price = models.IntegerField(null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Услуги'
        verbose_name_plural = 'Услуги'


class Cart(models.Model):
    owner = models.ForeignKey('User', on_delete=models.CASCADE, null=False)
    services = models.ManyToManyField(Service, blank=True, related_name='cart')
    is_active = models.BooleanField(default=True, null=False)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class Order(models.Model):
    owner = models.ForeignKey('User', on_delete=models.CASCADE, null=False)
    services = models.ManyToManyField(Service, blank=True, null=False, related_name='order')
    message = models.TextField(null=True, blank=True)
    sum = models.IntegerField(null=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'