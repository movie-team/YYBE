from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import numpy as np
import requests
from .serializers import MovieSerializer, GenreSerializer, ReviewSerializer
from .models import Movie, Genre, Review
from accounts.serializers import UserSerializer
from recommendation import MatrixFactorization
import os, re


# Create your views here.


class MatrixFactorization():
    def __init__(self, R, k, learning_rate, reg_param, epochs, verbose=False):
        """
        :param R: rating matrix
        :param k: latent parameter
        :param learning_rate: alpha on weight update
        :param reg_param: beta on weight update
        :param epochs: training epochs
        :param verbose: print status
        """

        self._R = R
        self._num_users, self._num_items = R.shape
        self._k = k
        self._learning_rate = learning_rate
        self._reg_param = reg_param
        self._epochs = epochs
        self._verbose = verbose


    def fit(self):
        """
        training Matrix Factorization : Update matrix latent weight and bias

        참고: self._b에 대한 설명
        - global bias: input R에서 평가가 매겨진 rating의 평균값을 global bias로 사용
        - 정규화 기능. 최종 rating에 음수가 들어가는 것 대신 latent feature에 음수가 포함되도록 해줌.

        :return: training_process
        """

        # init latent features
        self._P = np.random.normal(size=(self._num_users, self._k))
        self._Q = np.random.normal(size=(self._num_items, self._k))

        # init biases
        self._b_P = np.zeros(self._num_users)
        self._b_Q = np.zeros(self._num_items)
        self._b = np.mean(self._R[np.where(self._R != 0)])

        # train while epochs
        self._training_process = []
        for epoch in range(self._epochs):

            # rating이 존재하는 index를 기준으로 training
            for i in range(self._num_users):
                for j in range(self._num_items):
                    if self._R[i, j] > 0:
                        self.gradient_descent(i, j, self._R[i, j])
            cost = self.cost()
            self._training_process.append((epoch, cost))

            # print status
            if self._verbose == True and ((epoch + 1) % 10 == 0):
                print("Iteration: %d ; cost = %.4f" % (epoch + 1, cost))


    def cost(self):
        """
        compute root mean square error
        :return: rmse cost
        """

        # xi, yi: R[xi, yi]는 nonzero인 value를 의미한다.
        # 참고: http://codepractice.tistory.com/90
        xi, yi = self._R.nonzero()
        predicted = self.get_complete_matrix()
        cost = 0
        for x, y in zip(xi, yi):
            cost += pow(self._R[x, y] - predicted[x, y], 2)
        return np.sqrt(cost) / len(xi)


    def gradient(self, error, i, j):
        """
        gradient of latent feature for GD

        :param error: rating - prediction error
        :param i: user index
        :param j: item index
        :return: gradient of latent feature tuple
        """

        dp = (error * self._Q[j, :]) - (self._reg_param * self._P[i, :])
        dq = (error * self._P[i, :]) - (self._reg_param * self._Q[j, :])
        return dp, dq


    def gradient_descent(self, i, j, rating):
        """
        graident descent function

        :param i: user index of matrix
        :param j: item index of matrix
        :param rating: rating of (i,j)
        """

        # get error
        prediction = self.get_prediction(i, j)
        error = rating - prediction

        # update biases
        self._b_P[i] += self._learning_rate * (error - self._reg_param * self._b_P[i])
        self._b_Q[j] += self._learning_rate * (error - self._reg_param * self._b_Q[j])

        # update latent feature
        dp, dq = self.gradient(error, i, j)
        self._P[i, :] += self._learning_rate * dp
        self._Q[j, :] += self._learning_rate * dq


    def get_prediction(self, i, j):
        """
        get predicted rating: user_i, item_j
        :return: prediction of r_ij
        """
        return self._b + self._b_P[i] + self._b_Q[j] + self._P[i, :].dot(self._Q[j, :].T)


    def get_complete_matrix(self):
        """
        computer complete matrix PXQ + P.bias + Q.bias + global bias

        - PXQ 행렬에 b_P[:, np.newaxis]를 더하는 것은 각 열마다 bias를 더해주는 것
        - b_Q[np.newaxis:, ]를 더하는 것은 각 행마다 bias를 더해주는 것
        - b를 더하는 것은 각 element마다 bias를 더해주는 것

        - newaxis: 차원을 추가해줌. 1차원인 Latent들로 2차원의 R에 행/열 단위 연산을 해주기위해 차원을 추가하는 것.

        :return: complete matrix R^
        """
        return self._b + self._b_P[:, np.newaxis] + self._b_Q[np.newaxis:, ] + self._P.dot(self._Q.T)


    def print_results(self):
        """
        print fit results
        """

        print("User Latent P:")
        print(self._P)
        print("Item Latent Q:")
        print(self._Q.T)
        print("P x Q:")
        print(self._P.dot(self._Q.T))
        print("bias:")
        print(self._b)
        print("User Latent bias:")
        print(self._b_P)
        print("Item Latent bias:")
        print(self._b_Q)
        print("Final R matrix:")
        print(self.get_complete_matrix())
        print("Final RMSE:")
        print(self._training_process[self._epochs-1][1])


def recommend(request, user_id):
    movies = Movie.objects.all().values_list('id', flat=True)
    movie_len = len(movies)
    User = get_user_model()
    user_count = User.objects.count()
    users = User.objects.all().order_by('id')
    
    watched_movies = []
    tmp = [[0] * movie_len for _ in range(user_count)]
    for i in range(movie_len):
        movie = movies[i]
        reviews = Review.objects.filter(movie_id=movie)
        for review in reviews:
            for j in range(user_count):
                if review.user == users[j]:
                    tmp[j][i] = review.rating
                if users[j] == user_id:
                    watched_movies.append(i)

    R = np.array(tmp)

    # P, Q is (M X k), (k X N) matrix
    factorizer = MatrixFactorization(R, k=2, learning_rate=0.01, reg_param=0.01, epochs=300, verbose=True)
    factorizer.fit()
    factorizer.print_results()
    user_rec_list = factorizer.get_complete_matrix()[user_id]

    rec_data = []
    top_movies_indices = []
    unwatched_indices = [i for i in range(len(user_rec_list)) if i not in watched_movies]
    top_movies_indices = sorted(unwatched_indices, key=lambda i: user_rec_list[i], reverse=True)[:10]
    for i in top_movies_indices:
        rec_data.append(Movie.objects.get(pk=movies[i]))

    return Response(rec_data)



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
    

@api_view(['POST'])
def movie_likes(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    if request.user in movie.like_users.all():
        movie.like_users.remove(request.user)
        is_like = False
    else:
        movie.like_users.add(request.user)
        is_like = True
        
    like_count = movie.like_users.all().count()

    return Response({'is_like': is_like, 'like_count': like_count})


@api_view(['POST'])
def review_likes(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if request.user in review.like_users.all():
        review.like_users.remove(request.user)
        is_like = False
    else:
        review.like_users.add(request.user)
        is_like = True
        
    like_count = review.like_users.all().count()

    return Response({'is_like': is_like, 'like_count': like_count})



