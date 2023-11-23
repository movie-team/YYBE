"""PJT URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # 사용자 관련 api 경로
    path('accounts/', include('dj_rest_auth.urls')),
    # path('accounts/', include('allauth.urls')),
    path('accounts/signup/', include('dj_rest_auth.registration.urls')),
    path('accounts/<int:user_id>/', views.user_info, name='user_info'),
    path('', include('django.contrib.auth.urls')),
    # 소셜 로그인
    path('accounts/google/login', views.google_login, name='google_login'),
    path('accounts/google/callback/', views.google_callback, name='google_callback'),  
    path('accounts/google/login/finish/', views.GoogleLogin.as_view(), name='google_login_todjango'),
    path('accounts/login/kakao/', views.kakao_login, name='kakao_login'),
    path('accounts/login/kakao/callback/', views.kakao_callback, name='kakao_callback'),
    # 영화 관련 api 경로
    path('movies/', include('movies.urls')),
    # 정적 파일 설정
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
