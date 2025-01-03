from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # 不需要登录就能访问的URL列表
        self.exempt_urls = [
            reverse('muggle:login'),
            '/admin/',
            '/static/',
            '/media/',
        ]

    def __call__(self, request):
        # 如果用户未登录且访问的URL不在豁免列表中
        if not request.user.is_authenticated and not any(request.path.startswith(url) for url in self.exempt_urls):
            return redirect('muggle:login')
        
        response = self.get_response(request)
        return response 