from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

# Create your models here.
class Genre(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    
class Movie(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)
    overview = models.TextField(blank=True)
    poster = models.TextField(blank=True)
    release_date = models.DateField()
    genres = models.ManyToManyField(Genre)
    review = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Review', related_name='reviewed_movie')
    # like_users = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='like_movies', on_delete=models.CASCADE)


class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    

class Review_likes(models.Model):
    user_pk = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    review_pk = models.ForeignKey(Review, on_delete=models.CASCADE)
    review_likes = models.BooleanField()

