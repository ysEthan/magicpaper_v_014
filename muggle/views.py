from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.decorators.http import require_http_methods

def login_view(request):
    """用户登录视图"""
    if request.user.is_authenticated:
        return redirect('muggle:home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"欢迎回来，{username}！")
                return redirect('muggle:home')
        else:
            messages.error(request, "用户名或密码错误。")
    else:
        form = AuthenticationForm()
    return render(request, 'muggle/login.html', {'form': form})

def register_view(request):
    """用户注册视图"""
    if request.user.is_authenticated:
        return redirect('muggle:home')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"账号创建成功！欢迎 {username}！")
            login(request, user)
            return redirect('muggle:home')
        else:
            messages.error(request, "注册过程中出现错误。")
    else:
        form = UserCreationForm()
    return render(request, 'muggle/register.html', {'form': form})

def logout_view(request):
    """用户登出视图"""
    logout(request)
    messages.info(request, "您已成功登出。")
    return redirect('muggle:login')

@login_required
def profile_view(request):
    """用户个人资料视图"""
    if request.method == 'POST':
        # 更新用户基本信息
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # 更新用户配置文件
        profile = user.profile
        profile.phone = request.POST.get('phone', '')
        profile.department = request.POST.get('department', '')
        profile.position = request.POST.get('position', '')
        
        # 处理头像上传
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        messages.success(request, '个人资料已更新。')
        return redirect('muggle:profile')
        
    return render(request, 'muggle/profile.html', {'user': request.user})

@login_required
def home_view(request):
    """主页视图"""
    return render(request, 'home_page.html', {
        'user': request.user,
    })
