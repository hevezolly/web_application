from django.http import HttpResponse, HttpRequest, Http404, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.shortcuts import render, redirect
from .models import SubmitPictureForm, Picture
from django.contrib.auth.models import User
from .imageHandler import shrink_image
from photoGalerey.settings import MEDIA_ROOT, MEDIA_URL
from django.core.files import File
import os

INDEX_HTML = os.path.join('galleryApp', 'index.html')
LOGIN_HTML = os.path.join('galleryApp', 'login.html')
REGISTER_HTML = os.path.join('galleryApp', 'register.html')
UPLOAD_HTML =os.path.join('galleryApp', 'photo_upload.html')


def index(request):
    authed = request.user.is_authenticated
    images = Picture.objects.values()
    return render(request, INDEX_HTML, {'unauthorised': not authed, 'image_list': images})


def login_user(request):
    if request.user.is_authenticated:
        logout(request)
    incorrect = False
    if request.POST:
        log = request.POST['username']
        pas = request.POST['password']

        user = authenticate(username=log, password=pas)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(reverse('index'))
        incorrect = True

    return render(request, LOGIN_HTML, {'incorrect_data': incorrect})


def logout_user(request):
    logout(request)
    return redirect(reverse('index'))


def register(request):
    if request.user.is_authenticated:
        logout(request)
    if request.POST:
        log = request.POST['username']
        pas1 = request.POST['password1']
        pas2 = request.POST['password2']

        num_results = User.objects.filter(username=log).count()
        if num_results != 0:
            return render(request, REGISTER_HTML,
                          {'incorrect_password_match': False,
                           'incorrect_password': False,
                           'incorrect_username': True})

        if pas1 != pas2:
            return render(request, REGISTER_HTML,
                   {'incorrect_password_match': True,
                    'incorrect_password': False,
                    'incorrect_username': False})

        user = User.objects.create_user(username=log, password=pas1)
        login(request, user)
        return redirect(reverse('index'))
    return render(request, REGISTER_HTML,
           {'incorrect_password_match': False,
            'incorrect_password': False,
            'incorrect_username': False})


def upload_picture(request):
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
    form = SubmitPictureForm()
    if request.POST:
        form = SubmitPictureForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.publisher = request.user
            item.likes = 0
            item.save()
            tail = os.path.join(MEDIA_ROOT, 'pictures_preview')
            name = item.main_image.name.split('/')[1]
            shrink_image(item.main_image, os.path.join(tail, name))
            item.preview_image = f'/pictures_preview/{name}'
            item.save()
            return render(request, UPLOAD_HTML, {'form': form})
    return render(request, UPLOAD_HTML, {'form': form})
