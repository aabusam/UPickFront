from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
from .models import Farm, WorkingHour, Plant, PlantCategory, FarmPlants, Address

# Helper Serializers

class WorkingHoursSerializer(serializers.ModelSerializer):
    is_open = serializers.SerializerMethodField()

    class Meta:
        model = WorkingHour
        fields = ['day', 'opening_time', 'closing_time', 'is_open']
    
    def get_is_open(self, obj):
        current_day = timezone.now().strftime('%A').lower()[0:3]  # Get the current day of the week (e.g., "monday")
        if obj.day == current_day:
            now = timezone.now().time()
            print(obj.opening_time, now, obj.closing_time)
            if obj.opening_time <= now <= obj.closing_time:
                return True
            return False
        return None
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        day = representation.pop('day')
        opening_time = representation.pop('opening_time')
        closing_time = representation.pop('closing_time')
        is_open = representation.pop('is_open')
        return [{day: {'opening_hours': opening_time, 'closing_hours': closing_time, 'is_open': is_open}}]

class ListWorkingHoursSerializer(serializers.ModelSerializer):
    is_open = serializers.SerializerMethodField()

    class Meta:
        model = WorkingHour
        fields = ['day', 'opening_time', 'closing_time', 'is_open']

    def get_is_open(self, obj):
        current_day = timezone.now().strftime('%A').lower()[0:3]
        if obj.day == current_day:
            now = timezone.now().time()
            if obj.opening_time <= now <= obj.closing_time:
                return True
            return False
        return None

    def to_representation(self, instance):
        current_day = timezone.now().strftime('%a').lower()[0:3]
        if instance.day == current_day:
            representation = {
                'day': instance.day,
                'opening_time': instance.opening_time,
                'closing_time': instance.closing_time,
                'is_open': self.get_is_open(instance),
            }
            return representation
        return None

class ListFarmAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['lat', 'long']
    

class FarmAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'country', 'zip_code', 'lat', 'long']


class PlantCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantCategory
        fields = ['id','name']

class FarmPlantSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='plant.id')
    title = serializers.CharField(source='plant.title')
    category = PlantCategorySerializer(source = 'plant.category')

    plant = serializers.HyperlinkedRelatedField(
        view_name='plant-detail',
        read_only=True,
    )

    class Meta:
        model = FarmPlants
        fields = ['id', 'title', 'category', 'image_url', 'season_start', 'season_end', 'organic', 'plant']

# Main Serilaizers 

class FarmDetailSerializer(serializers.ModelSerializer):
    working_hours= WorkingHoursSerializer(many=True)
    address = FarmAddressSerializer()
    farm_plants = FarmPlantSerializer(source='plants',many=True)

    class Meta:
        model = Farm 
        fields = ['id', 'image_url', 'title', 'description', 'address', 'working_hours','entrance_fee',
                  'phone', 'email', 'website', 'farm_plants']
        
class FarmListSerializer(serializers.ModelSerializer):
    working_hours= ListWorkingHoursSerializer(many=True)
    address = ListFarmAddressSerializer()

    farm = serializers.HyperlinkedIdentityField(
        view_name='farm-detail',
        read_only=True,
    )
    class Meta:
        model = Farm 
        fields = ['id', 'image_url', 'title', 'farm', 'working_hours', 'address']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        working_hours = representation['working_hours']
        non_null_working_hours = [wh for wh in working_hours if wh is not None]
        representation['working_hours'] = non_null_working_hours
        return representation

class PlantSerializer(serializers.ModelSerializer):
    category = PlantCategorySerializer()
    class Meta:
        model = Plant
        fields = ['id','title', 'scientific_name', 'country_of_origin', 
                   'last_updated', 'category']