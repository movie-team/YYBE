from django.shortcuts import render, redirect      
import requests    


# code 요청
def kakao_login(request):
    app_rest_api_key = 'ea9a470844fc6ce1db188cf13bbe325a'
    # redirect_uri = "https://kauth.kakao.com/.well-known/openid-configuration"
    redirect_uri = "http://127.0.0.1:8000/account/login/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={app_rest_api_key}&redirect_uri={redirect_uri}&response_type=code"
    )
    
    
# access token 요청
def kakao_callback(request): 
    app_rest_api_key = 'ea9a470844fc6ce1db188cf13bbe325a'
    redirect_uri = "http://127.0.0.1:8000/account/login/kakao/callback"                                                                 
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
        print(response_data)
    else:
        # 요청이 실패했을 때 처리할 코드
        print("요청이 실패했습니다.")
        print(response.status_code)
        print(response.text)

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
        print(f"HTTP 요청 실패 - 상태 코드: {response.status_code}")
        print(response.text)  # 실패한 경우 응답 본문을 확인할 수 있습니다.