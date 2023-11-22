from rest_framework import serializers
from .models import Movie, Genre, Review
from django.db.models import Avg

class GenreSerializer(serializers.ModelSerializer):
    class Meta():
        model = Genre
        fields = '__all__'

class MovieSerializer(serializers.ModelSerializer):
    # serializer의 SerializerMethodField를 이용하여 rate의 평균값을 구한다
    average_rate = serializers.SerializerMethodField()
    review_count = serializers.IntegerField(source='movie_reviews.count', read_only=True)

    class Meta():
        model = Movie
        fields = '__all__'
    
    def get_average_rate(self, obj):
        av = Review.objects.filter(movie=obj.id).aggregate(Avg('rating')).get('rating__avg')

        if av is None:
            return 0
        return round(av, 1)

class ReviewSerializer(serializers.ModelSerializer):
    class Meta():
        model = Review
        fields = '__all__'
        # read_only_fields = ('movie', 'user',)
