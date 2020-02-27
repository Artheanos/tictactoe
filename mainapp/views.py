from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from mainapp.models import Player, Room
from django.db.models import Q


def leave_room(request):
    if 'room_id' in request.session:
        try:
            room = Room.objects.get(pk=request.session['room_id'])
            setattr(
                room,
                f'player_{room.get_player_rid(request.session["player_id"])}',
                None
            )
            if room.empty():
                room.delete()
            else:
                room.save()
        except Room.DoesNotExist:
            pass
        del request.session['room_id']

        player = Player.objects.get(pk=request.session['player_id'])
        player.vote = None
        player.save()

    return redirect('/')


def logout(request):
    leave_room(request)
    if 'player_id' in request.session:
        del request.session['player_id']
    return redirect('/')


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    if 'username' not in request.POST:
        request.method = 'GET'
        return login(request)

    new_player = Player(username=request.POST['username'])
    new_player.save()
    request.session['player_id'] = new_player.pk

    return redirect('/')


def create_room() -> int:
    room = Room()
    room.save()

    return room.pk


def join_room_get_method(room_id: int):
    return redirect('/?room=%s' % room_id)


def tool(request):
    if 'leave' in request.GET:
        return leave_room(request)

    if 'logout' in request.GET:
        return logout(request)

    if 'create_room_and_join' in request.GET:
        room_id = create_room()
        # return redirect('/')
        return join_room_get_method(room_id)

    return HttpResponse()


def listing(request):
    if 'room' in request.GET:
        room = Room.objects.get(pk=request.GET['room'])

        if 'room_id' in request.session:

            if str(request.session['room_id']) != str(request.GET['room']):
                return HttpResponse(
                    f"You haven't left your room<br/>"
                    f"<a href='/?room={request.session['room_id']}'>Go back?</a>"
                )
            try:
                if not Room.objects.filter(pk=request.GET['room']).exists():
                    return leave_room(request)
            except ValueError:
                return redirect('/')

        else:

            preferred_rid = str(request.GET['side']) if 'side' in request.GET else '1'
            print(preferred_rid == '2')

            if room.get_player_rid(request.session['player_id']):
                return redirect('/')

            if preferred_rid == '1':
                if room.player_1:
                    return redirect('/')
                room.player_1_id = request.session['player_id']
                room.turn = '1'

            if preferred_rid == '2':
                if room.player_2:
                    return redirect('/')
                room.player_2_id = request.session['player_id']
                room.turn = '2'

            try:
                room.save()
            except IntegrityError:
                return logout(request)

            request.session['room_id'] = room.pk

        return render(request, 'game.html', {'my_id': room.get_player_rid(request.session['player_id'])})

    if 'room_id' in request.session:
        return join_room_get_method(request.session['room_id'])

    return render(request, 'listing.html', {'room_list': Room.objects.all()})


def ajax(request):
    if 'get_players' in request.GET:
        room = Room.objects.get(pk=request.session['room_id'])

        data = {'turn': room.turn}
        for player, rid in room.get_players_with_rid():
            data['player_' + rid] = player.username if player else None

        return JsonResponse(data)

    if 'get_board_state' in request.GET:
        room = Room.objects.get(pk=request.session['room_id'])
        data = {'board_state': room.state, 'winner': room.winner}

        return JsonResponse(data)

    if 'x' in request.GET:
        room = Room.objects.get(pk=request.session['room_id'])
        room.make_move(int(request.GET['x']), int(request.GET['y']))
        room.save()

        return HttpResponse()

    if 'get_rooms' in request.GET:
        data = [
            {'id': room.id,
             **{f'player_{rid}': player.username if player else None for player, rid in room.get_players_with_rid()}
             }
            for room in Room.objects.all().order_by('pk')
        ]
        return JsonResponse(data, safe=False)

    if 'create_room' in request.GET:
        create_room()
        return HttpResponse()

    if 'rematch' in request.GET:
        room = Room.objects.get(pk=request.session['room_id'])

        opponent_rid = room.opponent(room.get_player_rid(request.session['player_id']))
        opponent = getattr(room, f'player_{opponent_rid}')
        print(opponent.vote)
        print(opponent_rid)
        if opponent and opponent.vote == 1:
            room.rematch()
            for player in room.get_players():
                player.vote = None
                player.save()

            return HttpResponse('1')

        player = Player.objects.get(pk=request.session['player_id'])
        player.vote = 1
        player.save()
        return HttpResponse('')

    if 'rematch_refresh' in request.GET:
        room = Room.objects.get(pk=request.session['room_id'])

        data = {'1': room.player_1.vote, '2': room.player_2.vote, 'ready': room.winner == '0'}

        return JsonResponse(data)
