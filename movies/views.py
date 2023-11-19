from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
from .serializers import MovieSerializer, GenreSerializer, ReviewSerializer
from .models import Movie, Genre
from accounts.serializers import UserSerializer
import os

# Create your views here.

access_token = settings.ACCESS_TOKEN
api_key = settings.API_KEY


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
        
        genres = Genre.objects.values()
        genre_li = []
        for genre in genres:
            if genre['id'] not in genre_li:
                genre_li.append(genre['id'])
        
        response = requests.get(url, headers=headers).json()
        for movie in response['results']:
            if movie['genre_ids']:
                save_data = {
                    'id': movie['id'],
                    'title': movie['title'],
                    'overview': movie['overview'],
                    'poster': movie['poster_path'],
                    'created_at': movie['release_date'],
                    'genres': movie['genre_ids']
                }

                serializer = MovieSerializer(data=save_data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
    return JsonResponse({ 'message': 'okay' })


@api_view(['GET',])
def get_now_playing(request):
    url = "https://api.themoviedb.org/3/movie/now_playing?language=en-US&page=1&region=KR"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers).json()

    return Response(response['results'])


@api_view(['GET', 'POST',])
def save_review_data(request):
    url = "https://api.themoviedb.org/3/movie/872585/reviews?language=en-US&page=1"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    movies = Movie.objects.all().values_list('id', flat=True)
    for movie in movies:
        params = {
            "movie_id": movie
        }
        response = requests.get(url, headers=headers, params=params).json()
        
        if response.get('results'):
            movie_id = response.get('id')

            for result in response.get('results'):
                save_user_data = {
                    'nickname': result['author'],
                    'username': result['author_details']['username'],
                    'password1': 'rkskekfk',
                    'password2': 'rkskekfk'
                }
                url = 'http://127.0.0.1:8000/accounts/signup'
                headers = {
                    "content-type": "application/x-www-form-urlencoded",
                }
                users = get_user_model().objects.all().values_list('username', flat=True)
                if result['author_details']['username'] not in users:
                    requests.post(url, data=save_user_data, headers=headers)
    return JsonResponse({'message': 'okay'})

    #         save_data = {
    #             'movie': movie_id,
    #             'user': get_user_model().objects.get(nickname=result['author']).id,
    #             'content': result['content'],
    #             'rating': result['author_details']['rating']
    #         }
    #         serializer = ReviewSerializer(data=save_data)
    #         if serializer.is_valid(raise_exception=True):
    #             serializer.save()

    # return JsonResponse({'message': 'okay'})

