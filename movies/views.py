from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
from .serializers import MovieSerializer, GenreSerializer, ReviewSerializer
from .models import Movie, Genre, Review
from accounts.serializers import UserSerializer
import os, re

# Create your views here.

access_token = settings.ACCESS_TOKEN
api_key = settings.API_KEY

def clean_username(username):
    # 허용되는 문자 (알파벳, 숫자, 밑줄)를 제외한 모든 문자를 제거
    cleaned_username = re.sub(r'[^a-zA-Z0-9_]', '', username)
    
    # 생성된 유저네임이 빈 문자열인지 확인
    if not cleaned_username:
        raise ValueError("Username is empty after removing special characters.")
    
    return cleaned_username

@api_view(['GET'])
def save_genre_data(request):

    url = "https://api.themoviedb.org/3/genre/movie/list?language=en"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers).json()

    for genre in response['genres']:
        save_data = {
            'id': genre['id'],
            'name': genre['name']
        }
        serializer = GenreSerializer(data=save_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
    
    return JsonResponse({ 'message': 'okay' })


@api_view(['GET'])
def save_movie_data(request):
    for i in range(1, 11):
        url = f"https://api.themoviedb.org/3/movie/popular?language=en-US&page={i}&region=KR"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        params = {
            "language": "ko-KR"
        }

        genres = Genre.objects.values()
        genre_li = []
        for genre in genres:
            if genre['id'] not in genre_li:
                genre_li.append(genre['id'])
        
        response = requests.get(url, headers=headers, params=params).json()
        for movie in response['results']:
            if movie['genre_ids']:
                save_data = {
                    'id': movie['id'],
                    'title': movie['title'],
                    'overview': movie['overview'],
                    'poster': movie['poster_path'],
                    'release_date': movie['release_date'],
                    'genres': movie['genre_ids']
                }

                serializer = MovieSerializer(data=save_data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
    return JsonResponse({ 'message': 'okay' })


@api_view(['GET',])
def get_now_playing(request):
    url = "https://api.themoviedb.org/3/movie/now_playing?language=ko-KR&page=1&region=KR"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers).json()

    return Response(response['results'])



@api_view(['GET', 'POST',])
def save_review_data(request):
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    movies = Movie.objects.all().values_list('id', flat=True)

    for movie in movies:

        db_url = f"https://api.themoviedb.org/3/movie/{movie}/reviews?language=en-US&page=1"
        response = requests.get(db_url, headers=headers).json()

        if response.get('results'):

            for result in response.get('results'):
                # username 사이의 공백, 특수문자 등 제거
                username = clean_username(result['author_details']['username'])

                save_user_data = {
                    'nickname': result['author'],
                    'username': username,
                    'password1': 'rkskekfk',
                    'password2': 'rkskekfk'
                }
                
                url = 'http://127.0.0.1:8000/accounts/signup/'

                users = get_user_model().objects.all().values_list('username', flat=True)

                if username not in users:
                    requests.post(url, data=save_user_data, headers=headers)

                if not result['author_details']['rating']:
                    result['author_details']['rating'] = 7.0

                save_data = {
                    'movie': movie,
                    'user': get_user_model().objects.get(nickname=result['author']).id,
                    'content': result['content'],
                    'rating': result['author_details']['rating']
                }

                serializer = ReviewSerializer(data=save_data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()

    return JsonResponse({'message': 'okay'})
                

@api_view(['GET',])
def get_popular_movies(request):
    movies = Movie.objects.all()
    serializer = MovieSerializer(movies, many=True)

    return Response(serializer.data)



@api_view(['GET', 'POST'])
def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    serializer = MovieSerializer(movie)
    if request.method == 'GET':
        return Response(serializer.data)
    
    elif request.method == 'POST':
        review_serializer = ReviewSerializer(data=request.data)
        if review_serializer.is_valid(raise_exception=True):
            review_serializer.save(user=request.user, movie=movie)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE',])
def review_detail(request, movie_id, review_id):
    review = get_object_or_404(Review, pk=review_id)
    serializer = ReviewSerializer(review)
    if request.method == 'GET':
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        review_serializer = ReviewSerializer(review, data=request.data)
        if review_serializer.is_valid(raise_exception=True):
            review_serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
    elif request.method == 'DELETE':
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)