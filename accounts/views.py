from django.shortcuts import render, redirect      
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import requests    


# code 요청
@api_view(['GET',])
def kakao_login(request):
    app_rest_api_key = 'ea9a470844fc6ce1db188cf13bbe325a'
    # redirect_uri = "https://kauth.kakao.com/.well-known/openid-configuration"
    redirect_uri = "http://127.0.0.1:8000/accounts/login/kakao/callback"
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


        