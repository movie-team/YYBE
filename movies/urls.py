from django.urls import path
from . import views
app_name = 'movies'

urlpatterns = [
    path('save_genre_data/', views.save_genre_data, name='save_genre_data'),
    path('save_movie_data/', views.save_movie_data, name='save_movie_data'),
    path('save_review_data/', views.save_review_data, name='save_review_data'),
    # path('list_data', views.list_data, name='list_data'),
    path('get_now_playing/', views.get_now_playing, name='get_now_playing'),
    # path('', views.index, name='index'),
    path('get_popular_movies/', views.get_popular_movies, name='get_popular_movies'),
    path('<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('<int:movie_id>/likes/', views.movie_likes, name='movie_likes'),
    path('<int:movie_id>/review/<int:review_id>/', views.review_detail, name='review_detail'),
    path('<int:movie_id>/review/<int:review_id>/likes/', views.review_likes, name='review_likes'),
    # path('<int:movie.pk>/ticketing/', views.ticketing, name='ticketing'),
    # path('worldcup/', views.worldcup, name='worldcup'),
]