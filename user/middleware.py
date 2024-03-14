from django.http import HttpResponse
from django.http import JsonResponse
import requests


class ProxyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/'):
            url = f'http://localhost:8000{request.path}'
            response = requests.request(
                method=request.method,
                url=url,
                data=request.body,
                headers={header: value for (header, value) in request.headers.items()},
                params=request.GET,
                cookies=request.COOKIES,
            )
            return JsonResponse(response.json(), status=response.status_code)
        return self.get_response(request)
