import json

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core import serializers

from mainapp.models import MyUser, Room


def main_foo(request):
    return render(request, 'arch/main_page.html')


def room_page(request, room_id):
    if 'user_id' not in request.session:
        return login_page(request)
    return render(request, 'room_page.html', {'room_id': room_id, 'username': request.session['user_name']})


def room_list(request):
    x = [{'id': i.id, 'dis': f'{i.users.count()}/2'} for i in Room.objects.order_by('id')]

    return render(request, 'room_list.html', {'rooms': x})


def login_page(request):
    if request.session.get('user_id'):
        if 'force' not in request.GET:
            return redirect('/rooms')

    if request.method == 'POST':
        username = request.POST.get('login')
        if username:
            m = MyUser.objects.get_or_create(name=username)[0]
            request.session['user_id'] = m.id
            request.session['user_name'] = username
            return redirect('/rooms')

    return render(request, 'login_page.html')


def my_api(request):
    if 'users' in request.GET:
        x = json.loads(serializers.serialize('json', MyUser.objects.all()))
        return JsonResponse(x, safe=False)

    return HttpResponse(request.path)
