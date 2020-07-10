import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from mainapp.models import MyUser, Room
from mainapp.tictactoe import CellNotEmpty, TicTacToe

ROOM_LIST_GROUP_NAME = 'room_list'

room_db = {}


class RoomListConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.channel_layer.group_add(
            ROOM_LIST_GROUP_NAME,
            self.channel_name
        )
        await self.accept()

    async def send_event(self, event):
        await self.send(text_data=json.dumps(event))

    async def receive(self, text_data=None, bytes_data=None):
        await self.refresh_loop()

    async def refresh_loop(self):
        await self.channel_layer.group_send(ROOM_LIST_GROUP_NAME, {'type': 'send_event', 'message': 'yo'})

    @database_sync_to_async
    def get_room_list(self):
        return [[i.id, f'{i.users.count()}/2'] for i in Room.objects.all()]


class TableConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = 'chat_%s' % self.room_name

    async def connect(self):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.set_user()
        await self.send_with_username('joined', 'send_event__broadcast')
        role = await self.get_room_role()

        if role:
            await self.send_with_username(
                {
                    'role': role,
                    'your_turn': await self.is_it_your_turn(),
                    'user_list': await self.get_user_list(),
                    'state': self.user.room.state,
                }
            )
        else:
            await self.send_with_username(
                {
                    'role': role,
                    'user_list': await self.get_user_list(),
                    'state': self.user.room.state,
                },
                'send_event__secret'
            )

        await self.channel_layer.group_send(
            ROOM_LIST_GROUP_NAME,
            {
                'type': 'send_event',
                'message': 'dupa',
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.unset_user()
        await self.send_with_username('quit')

    async def send_with_username(self, text_data, message_type='send_event'):
        data = {
            'type': message_type,
            'message': text_data,
            'username': self.user.name
        }

        if message_type == 'send_event__secret':
            await self.send_event(data)
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            data
        )

    async def receive(self, text_data=None, bytes_data=None):
        print('received')
        if text_data == 'dupa':
            await self.send_with_username(await self.get_user_list())
            return

        data = json.loads(text_data)

        if data.get('header') == 'move':
            is_your_turn = await self.is_it_your_turn()
            if is_your_turn:
                try:
                    winner = await database_sync_to_async(
                        lambda: self.user.room.move(*data['message'])
                    )()
                    if winner:
                        await self.send_with_username({'move': data['message'], 'winner': winner})
                    else:
                        await self.send_with_username({'move': data['message']})
                except CellNotEmpty:
                    await self.send_with_username({'move': 'CellNotEmpty'}, 'send_event__secret')

    async def send_event(self, event):
        await self.send(text_data=json.dumps(event))

    async def send_event__secret(self, event):
        if self.user.name == event['username']:
            await self.send_event(event)

    async def send_event__broadcast(self, event):
        if self.user.name != event['username']:
            await self.send_event(event)

    @database_sync_to_async
    def is_it_your_turn(self):
        # self.user.room.refresh_from_db()
        return self.user.room.is_his_turn(self.user.pk)

    @database_sync_to_async
    def get_room_role(self):
        # self.user.room.refresh_from_db()
        if not self.user.room.player_1:
            self.user.room.player_1 = self.user
            self.user.room.save()
            return 1

        if not self.user.room.player_2:
            self.user.room.player_2 = self.user
            self.user.room.save()
            return 2

        return 0

    @database_sync_to_async
    def set_user(self):
        self.user = MyUser.objects.get(pk=self.scope['session'].get('user_id'))
        room = room_db.get(self.room_name)
        if room:
            self.user.room = room
        else:
            room = Room.objects.get_or_create(pk=self.room_name)[0]
            room_db[self.room_name] = room
            self.user.room = room

        self.user.save()

    @database_sync_to_async
    def unset_user(self):
        # self.user.room.refresh_from_db()
        if self.user.room.player_1 and self.user.room.player_1.pk == self.user.pk:
            self.user.room.player_1 = None
        elif self.user.room.player_2 and self.user.room.player_2.pk == self.user.pk:
            self.user.room.player_2 = None

        if not (self.user.room.player_1 or self.user.room.player_2):
            self.user.room.state = '0' * 9
            self.user.room.turn = 1
            self.user.room.tictac = TicTacToe()
            del room_db[self.room_name]

        self.user.room.save()

        self.user.room = None
        self.user.save()

    @database_sync_to_async
    def get_user_list(self):
        return [i.name for i in self.user.room.users.all()]
