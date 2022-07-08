
from django.urls import path
from .views import index, user_login, user_logout

urlpatterns = [
    path('', index, name='index'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
]