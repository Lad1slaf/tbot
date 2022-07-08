from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from asgiref.sync import sync_to_async

from tauth.forms import UserLoginForm, UserRegisterForm
from tauth.models import TelegramUser


@sync_to_async
def is_user(username):
    if User.objects.filter(username=username).count() > 0:
        return True


@sync_to_async
def register(username, password, name, user_id, link):
    new_user = User.objects.create_user(username=username, password=password, first_name=name)
    new_user.set_password(password)
    new_user.save()
    new_tg_user = TelegramUser(user=new_user, tg_user_id=user_id, link=link)
    new_tg_user.save()


def index(request):
    user = request.user
    tg_user = User.objects.select_related('td_user').filter(pk=user.pk).first()
    return render(request, 'index.html', context={'current_user': tg_user})


# @sync_to_async
# def register(username, first_name, password1, password2):
#     form = UserRegisterForm(username=username, password1=password1, password2=password2, first_name=first_name)
#     if form.is_valid():
#         user = form.save()
#         return user
#     else:
#         return ValueError('Data is false')


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')
