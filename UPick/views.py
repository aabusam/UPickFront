from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Farm, FarmPlants
from .serializers import FarmListSerializer, FarmDetailSerializer, PlantFarmsSerializer
from .filters import FarmFilter

class UPickPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class FarmViewSet(ModelViewSet):
    http_method_names = ['get']
    pagination_class = UPickPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = FarmFilter

    def get_queryset(self):
        if self.action == 'list':
            # Adjust the queryset for the list view
            return Farm.objects.prefetch_related('working_hours', 'address').all()
        elif self.action == 'retrieve':
            # Adjust the queryset for the detail view
            return Farm.objects.prefetch_related(
                'address',
                'working_hours',
                'plants__plant',
                'plants__plant__category'
            )

    def get_serializer_class(self):
        if self.action == 'list':
            return FarmListSerializer
        elif self.action == 'retrieve':
            return FarmDetailSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        results_count = self.paginator.page.paginator.count if page is not None else 0
        results_per_page = len(serializer.data) if page is not None else 0
        info = {
            'count': results_count,
            'next': self.paginator.get_next_link(),
            'previous': self.paginator.get_previous_link(),
            'results_per_page': results_per_page
        }
        response_data = {
            'info': info,
            'results': serializer.data
        }
        return Response(response_data)


class PlantViewSet(ModelViewSet):
    pagination_class = UPickPagination

    http_method_names = ['get']
    queryset = FarmPlants.objects.prefetch_related('plant', 'plant__category','farm','farm__working_hours', 'farm__address').all()
    serializer_class = PlantFarmsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['plant__category', 'farm', 'plant']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        results_count = self.paginator.page.paginator.count if page is not None else 0
        results_per_page = len(serializer.data) if page is not None else 0
        info = {
            'count': results_count,
            'next': self.paginator.get_next_link(),
            'previous': self.paginator.get_previous_link(),
            'results_per_page': results_per_page
        }
        response_data = {
            'info': info,
            'results': serializer.data
        }
        return Response(response_data)