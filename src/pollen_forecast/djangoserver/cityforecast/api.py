from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import City
from django.db import connection

class CityAutocompleteAPI(APIView):
    """API endpoint to return city autocomplete suggestions."""

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "")
        if query:
            if connection.vendor == 'postgresql':
                # Use TrigramSimilarity for PostgreSQL
                from django.contrib.postgres.search import TrigramSimilarity
                cities = City.objects.annotate(
                    similarity=TrigramSimilarity('official_city_name', query)
                ).filter(similarity__gt=0.3).order_by('-similarity')[:10]
            else:
                # Fallback for SQLite or other databases
                cities = City.objects.filter(official_city_name__icontains=query)[:10]
            
            city_names = list(cities.values_list("official_city_name", flat=True))
            return Response(city_names, status=status.HTTP_200_OK)
        return Response([], status=status.HTTP_200_OK)