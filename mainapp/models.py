from django.db import models
from django.db.models import Q


class Player(models.Model):
    username = models.CharField(max_length=30)
    # TODO last_request = models.DateTimeField()
    vote = models.SmallIntegerField(null=True)


class Room(models.Model):
    state = models.CharField(max_length=9, default='0' * 9)
    player_1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_1', null=True)
    player_2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_2', null=True)
    turn = models.CharField(max_length=1, default='0')
    winner = models.CharField(max_length=1, default='0')

    def get_players(self) -> tuple:
        return self.player_1, self.player_2

    def get_players_with_rid(self):
        return (self.player_1, '1'), (self.player_2, '2')

    def get_player_rid(self, player_id):
        if player_id == self.player_1_id:
            return '1'
        if player_id == self.player_2_id:
            return '2'
        return None

    def empty(self):
        return not (self.player_1 or self.player_2)

    @staticmethod
    def opponent(player_rid):
        return {'1': '2', '2': '1'}[player_rid]

    def change_turns(self):
        self.turn = Room.opponent(self.turn)

    def rematch(self):
        self.state = '0' * 9
        self.player_1, self.player_2 = self.player_2, self.player_1
        print('self.winner =', self.winner)
        if self.winner == '3':
            self.change_turns()
        else:
            self.turn = self.winner
        self.winner = '0'
        self.save()

    def make_move(self, x, y):
        i = x + (y * 3)

        if self.state[i] != '0':
            return

        self.state = self.state[:i] + self.turn + self.state[i + 1:]

        def check_set(s: set):
            if len(s) == 1 and next(iter(s)) != '0':
                self.winner = s.pop()
                self.save()

        for i in range(0, 3):
            check_set(set(self.state[i * 3:(i + 1) * 3]))
            check_set({self.state[j + i] for j in range(0, 9, 3)})

        check_set({self.state[i] for i in range(0, 9, 4)})
        check_set({self.state[i] for i in range(2, 7, 2)})

        if '0' not in self.state and self.winner == '0':
            self.winner = '3'

        self.change_turns()

    @staticmethod
    def find_by_player_id(player_id):
        return Room.objects.get(
            Q(player_1_id=player_id) | Q(player_2_id=player_id)
        )
