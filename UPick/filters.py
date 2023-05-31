from django_filters import rest_framework as filters
from django.db.models import Q, DecimalField, ExpressionWrapper, F, Value
from django.utils import timezone
from django.db.models.functions import Coalesce
from rest_framework.exceptions import ValidationError
from .models import Farm
from math import cos, radians
import math

class FarmFilter(filters.FilterSet):
    
    is_open = filters.BooleanFilter(method='filter_is_open', label='Is Open')
    radius = filters.NumberFilter(method='filter_radius_long_lat', label='Radius')
    address__lat = filters.NumberFilter(method='filter_radius_long_lat', label='Latitude')
    address__long = filters.NumberFilter(method='filter_radius_long_lat', label='Longitude')
    entrance_fee = filters.RangeFilter(method='filter_entrance_fee', label='Entrance Fee')


    class Meta:
        model = Farm
        
        fields = ['radius', 'address__lat', 'address__long','is_open', 'entrance_fee']

    #  ------------ filtering based on who is open ------------------- #

    def filter_is_open(self, queryset, name, value):
        current_day = timezone.now().strftime('%a').lower()[0:3]
        current_time = timezone.now().time()
        
        if value is True:
            # Filter farms that are open at the current day and time
            queryset = queryset.filter(
                working_hours__day=current_day,
                working_hours__opening_time__lte=current_time,
                working_hours__closing_time__gte=current_time
            )
        elif value is False:
            # Filter farms that are not open at the current day and time
            queryset = queryset.filter(
                Q(working_hours__day=current_day) &
                (Q(working_hours__opening_time__gt=current_time) | Q(working_hours__closing_time__lt=current_time))
            )
    
        return queryset

    #  ------------ filtering based on location radius ------------------- #

    def filter_radius_long_lat(self, queryset, name, value):
        client_radius = self.request.query_params.get('radius')
        client_latitude = self.request.query_params.get('address__lat')
        client_longitude = self.request.query_params.get('address__long')

        if not client_radius or not client_latitude or not client_longitude:
            raise ValidationError('Please provide values for radius, address__lat, and address__long.')

        radius = float(client_radius)
        latitude = float(client_latitude)
        longitude = float(client_longitude)

        # Calculate the latitude and longitude ranges based on the given radius
        lat_diff = radius / 69.0  # Approximate latitude degrees per mile
        lon_diff = radius / (69.0 * abs(math.cos(math.radians(latitude))))  # Approximate longitude degrees per mile

        min_latitude = latitude - lat_diff
        max_latitude = latitude + lat_diff
        min_longitude = longitude - lon_diff
        max_longitude = longitude + lon_diff

        # Filter farms within the latitude and longitude ranges
        queryset = queryset.filter(
            Q(address__lat__gte =  min_latitude) & 
            Q(address__lat__lte =  max_latitude) &
            Q(address__long__gte =  min_longitude) & 
            Q(address__long__lte =  max_longitude) 
        )

        return queryset
    
    #  ------------ filtering based on entrance fee------------------- #

    def filter_entrance_fee(self, queryset, name, value):
        entrance_fee_min = value.start if value.start is not None else 0
        entrance_fee_max = value.stop if value.stop is not None else 999999999

        # Handle null values by considering them as zero
        entrance_fee_coalesce = ExpressionWrapper(
            Coalesce(F('entrance_fee'), Value(0, output_field=DecimalField())),
            output_field=DecimalField()
        )

        # Filter farms with entrance fees within the specified range
        queryset = queryset.annotate(entrance_fee_coalesce=entrance_fee_coalesce)
        queryset = queryset.filter(
            entrance_fee_coalesce__gte=entrance_fee_min,
            entrance_fee_coalesce__lte=entrance_fee_max
        )
        
        return queryset
