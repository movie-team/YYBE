from .models import User
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer

# class UserSerializer(serializers.ModelSerializer):
#     def create(self, validated_data):
#         user = User.objects.create_user(
#             username = validated_data['username'],
#             email = validated_data['email'],
#             nickname = validated_data['nickname'],
#             password = validated_data['password'],
#         )
#         return user
#     class Meta:
#         model = User
#         fields = ['username', 'nickname', 'email', 'password']

class UserSerializer(RegisterSerializer):
    # 기본 설정 필드: username, password, email
    # 추가 설정 필드: nickname
    nickname = serializers.CharField(max_length=10)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['nickname'] = self.validated_data.get('nickname', '')

        return data