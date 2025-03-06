from django.http import HttpRequest
from django.shortcuts import redirect, reverse

class AuthenticatedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if request.user.is_authenticated:
            if request.path == reverse('account:login') or request.path == reverse('account:register'):
                return redirect(reverse('account:accounts'))

        else:
            if request.path == reverse('account:profile') or request.path == reverse('account:logout') or request.path == reverse('account:delete'):
                return redirect(reverse('account:accounts'))

        response = self.get_response(request)
        return response