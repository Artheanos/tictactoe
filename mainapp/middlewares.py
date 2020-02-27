from django.core.handlers.wsgi import WSGIRequest
from django.utils.deprecation import MiddlewareMixin

from django.http import HttpResponseRedirect
from django.shortcuts import redirect

no_user_whitelist = ['/login/']


class AuthRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request: WSGIRequest):

        if request.path == '/ajax/':
            return

        if 'player_id' not in request.session:
            if request.path not in no_user_whitelist:
                return HttpResponseRedirect('/login')

        # if 'room_id' in request.session and not request.build_absolute_uri().split('/')[3].startswith('?room'):
        #     return redirect('/?room=%s' % request.session['room_id'])
