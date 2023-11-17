from django.urls import path
from . import views
app_name = 'movies'

urlpatterns = [
    path('save_genre_data/', views.save_genre_data, name='save_genre_data'),
    path('save_movie_data/', views.save_movie_data, name='save_movie_data'),
    # path('list_data', views.list_data, name='list_data'),
    path('get_now_playing/', views.get_now_playing, name='get_now_playing'),
    # path('', views.index, name='index'),
    # path('<int:movie.pk>/', views.detail, name='detail'),
    # path('review/<int:review.pk>/likes/', views.likes, name='likes'),
    # path('<int:movie.pk>/ticketing/', views.ticketing, name='ticketing'),
    # path('worldcup/', views.worldcup, name='worldcup'),
]