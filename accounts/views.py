from django.shortcuts import render, redirect      
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import requests    
from django.conf import settings
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework import status
from json.decoder import JSONDecodeError



BASE_URL = 'http://127.0.0.1:8000/'
GOOGLE_CALLBACK_URI = BASE_URL + 'accounts/google/callback/'

client_id = settings.GOOGLE_CLI_ID
client_secret = settings.GOOGLE_CLI_PW

def google_login(request):
    """
    Code Request
    """
    scope = "https://www.googleapis.com/auth/userinfo.email"

    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")



def google_callback(request):
    # client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    # client_secret = getattr(settings, "SOCIAL_AUTH_GOOGLE_SECRET")
    code = request.GET.get('code')
    state = request.GET.get('state')
    """
    Access Token Request
    """
    token_req = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}")
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get('access_token')
    """
    Email Request
    """
    email_req = requests.get(
        f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    email_req_status = email_req.status_code
    if email_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
    email_req_json = email_req.json()
    email = email_req_json.get('email')
    """
    Signup or Signin Request
    """
    try:
        user = get_user_model().objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 google이 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        if social_user.provider != 'google':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        # 기존에 Google로 가입된 유저
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}accounts/google/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)
    except get_user_model().DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}accounts/google/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)
    


class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client


# code 요청
@api_view(['GET',])
def kakao_login(request):
    app_rest_api_key = 'ea9a470844fc6ce1db188cf13bbe325a'
    # redirect_uri = "https://kauth.kakao.com/.well-known/openid-configuration"
    redirect_uri = "http://127.0.0.1:8000/accounts/login/kakao/callback/"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={app_rest_api_key}&redirect_uri={redirect_uri}&response_type=code"
    )
    
    
# access token 요청
@api_view(['GET',])
def kakao_callback(request): 
    app_rest_api_key = 'ea9a470844fc6ce1db188cf13bbe325a'
    redirect_uri = "http://127.0.0.1:8000/accounts/login/kakao/callback"                                                                 
    code = request.GET.get('code')

    # POST 요청을 보낼 엔드포인트 URL
    url = "https://kauth.kakao.com/oauth/token"

    # POST 요청의 데이터 설정
    data = {
        "grant_type": "authorization_code",
        "client_id": app_rest_api_key,
        "redirect_uri": redirect_uri,
        "code": code,
    }

    # Content-Type 헤더 설정
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # POST 요청 보내기
    response = requests.post(url, data=data, headers=headers)

    if response.status_code == 200:
        # 요청이 성공했을 때 처리할 코드
        response_data = response.json()
        access_token = response_data.get("access_token")
        # access_token을 사용하거나 처리하는 로직을 작성합니다.
        user_url = "https://kapi.kakao.com/v2/user/me"
        auth = f'Bearer {access_token}'
        HEADER = {
            "Authorization": auth,
            "Content-type": "application/x-www-form-urlencoded"
        }
        res = requests.get(user_url, headers=HEADER)

        save_url = "https://kapi.kakao.com/v1/user/update_profile"
        save_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {access_token}"
        }

        properties_json = res.json()['properties']

        # 데이터를 urlencode
        data = {
            'properties': properties_json
        }

        # POST 요청 보내기
        response = requests.post(save_url, headers=save_headers, data=data)

        return JsonResponse({ "message": "요청을 완료했습니다." })


    else:
        # 요청이 실패했을 때 처리할 코드
        return JsonResponse({ "message": "요청이 실패했습니다." })



def kakao_logout(request):
    ACCESS_TOKEN = request.GET.get('access_token')
    # 요청을 보낼 URL
    url = "https://kapi.kakao.com/v1/user/logout"

    # 요청 헤더
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {ACCESS_TOKEN}"  # ACCESS_TOKEN 변수에 본인의 액세스 토큰을 넣어주세요.
    }

    # POST 요청 보내기
    response = requests.post(url, headers=headers)

    # 응답 확인
    if response.status_code == 200:
        # 성공적인 응답
        print("로그아웃이 완료되었습니다.")
        return redirect('articles: index')
    else:
        # 요청이 실패한 경우
        return JsonResponse({ "message": "요청이 실패했습니다." })


        