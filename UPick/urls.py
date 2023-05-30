from django.urls import path , include
from . import views
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('farms', views.FarmViewSet, basename='farm')
router.register('plants', views.PlantViewSet)

urlpatterns = [
    path('', include(router.urls)),
]