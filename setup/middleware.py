from django.http import HttpResponseForbidden, HttpRequest, HttpResponse
from django.shortcuts import reverse, redirect
from django.utils.deprecation import MiddlewareMixin

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if request.path.startswith('/admin/'):
            if not request.user.is_authenticated or not request.user.is_superuser:
                return HttpResponseForbidden('Você não tem permissão para acessar essa área')

        response = self.get_response(request)
        return response

class Redirect404Middleware(MiddlewareMixin):
    def process_response(self, request: HttpRequest, response: HttpResponse):
        if response.status_code == 404:
            return redirect(reverse('account:accounts'))
        
        return response