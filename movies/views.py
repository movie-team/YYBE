from django.shortcuts import render
import requests
import json


# Create your views here.
def get_movie_data():
    total_data = []
    API_KEY = 'a5652a4c9a3b598372e418a3b9c37371'
    for i in range(1, 11):
        request_url = f'https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=ko-KR&page={i}'
        movies = requests.get(request_url).json()

        for movie in movies['results']:
            if movie['release_date']:
                fields = {
                    'movie_id': movie['id'],
                    'title': movie['title'],
                    'overview': movie['overview'],
                    'poster': movie['poster_path'],
                    'created_at': movie['release_date'],
                    'genres': movie['genre_ids']
                }
                data = {
                    'pk': movie['id'],
                    'model': 'movies.movie',
                    'fields': fields
                }
                total_data.append(data)
    with open("movie_data.json", "w", encoding="utf-8") as w:
        json.dump(total_data, w, indent=2, ensure_ascii=False)

# get_movie_data() 

def get_genre_data():
    url = 'https://api.themoviedb.org/3/genre/movie/list'
    params = {
        'language': 'en',
    }
    access_token = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhNTY1MmE0YzlhM2I1OTgzNzJlNDE4YTNiOWMzNzM3MSIsInN1YiI6IjY1M2I2NDYxNTE5YmJiMDBlMThiOTY1MyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.oz5MIcA6_UvndsC4rMGZ_8VAwFmkuvwXsFEDx1ufojI'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'accept': 'application/json'
    } 
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        total_data = []
        genres_json = response.json()
        for genre in genres_json['genres']:
            fields = {
                'genre_id': genre['id'],
                'name': genre['name']
            }
            data = {
                'pk': genre['id'],
                'model': 'movies.genre',
                'fields': fields
            }
            total_data.append(data)
        with open("genre_data.json", "w", encoding="utf-8") as w:
            json.dump(total_data, w, indent=2, ensure_ascii=False)
    return ""

get_genre_data()
