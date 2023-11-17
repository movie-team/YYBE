from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
from .serializers import MovieSerializer, GenreSerializer
from .models import Movie, Genre


# Create your views here.

access_token = settings.ACCESS_TOKEN
api_key = settings.API_KEY


@api_view(['GET'])
def save_genre_data(request):
    url = 'https://api.themoviedb.org/3/genre/movie/list'

    params = {
        'api_key' : api_key,
        'language' : 'ko',
    }

    response = requests.get(url, params=params).json()

    for genre in response['genres']:
        save_data = {
            'genre_id': genre['id'],
            'name': genre['name']
        }
        serializer = GenreSerializer(data=save_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
    
    return JsonResponse({ 'message': 'okay' })


@api_view(['GET'])
def save_movie_data(request):
    for i in range(1, 51):
        url = f"https://api.themoviedb.org/3/movie/popular?language=en-US&page={i}&region=KR"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        genres = Genre.objects.values()
        genre_li = []
        for genre in genres:
            if genre['genre_id'] not in genre_li:
                genre_li.append(genre['genre_id'])
        
        response = requests.get(url, headers=headers).json()
        for movie in response['results']:
            if set(movie['genre_ids']).issubset(set(genre_li)):
                # for genre_id in movie['genre_ids']:
                print(movie['genre_ids'])
                for idx, genre_id in enumerate(movie['genre_ids']):
                    # genre_id = int(genre_id)
                    movie['genre_ids'][idx] = int(genre_id)
                    print(genre_id)
                    # print(type(genre_id))
                save_data = {
                    'movie_id': movie['id'],
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

