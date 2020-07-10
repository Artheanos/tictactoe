from random import choice
from django.db import models

from mainapp.tictactoe import TicTacToe

words = [i for i in open('/usr/share/dict/american-english').read().split('\n') if len(i) > 3]


class Room(models.Model):
    state = models.CharField(max_length=9, null=False, default='0' * 9)
    player_1 = models.ForeignKey('MyUser', on_delete=models.SET_NULL, related_name='player_1', null=True)
    player_2 = models.ForeignKey('MyUser', on_delete=models.SET_NULL, related_name='player_2', null=True)
    turn = models.PositiveSmallIntegerField(null=False, default=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tictac = TicTacToe(self.state, self.turn)

    def move(self, x, y):
        result = self.tictac.move(x, y)
        self.state = self.tictac.board_as_string()
        print('before', self.turn, 'after', self.tictac.player_turn)
        self.turn = self.tictac.player_turn
        self.save()
        return result

    def is_his_turn(self, player_pk):
        players_turn = self.player_1 if self.turn == 1 else self.player_2
        return players_turn and player_pk == players_turn.pk


class MyUser(models.Model):
    name = models.CharField(max_length=100, null=False)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, related_name='users')

    def random_name(self):
        while True:
            new_name = choice(words)
            if not MyUser.objects.filter(name=new_name).exists():
                break
        self.name = new_name
