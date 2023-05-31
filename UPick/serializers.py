from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
from .models import Farm, WorkingHour, Plant, PlantCategory, FarmPlants, Address

# Helper Serializers

# ------------------- Woking Hours Serializers ----------------------------#
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

# ------------------- Farm Address Serializer ----------------------------#

class FarmAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'country', 'zip_code', 'lat', 'long']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        lat = representation.pop('lat')
        long = representation.pop('long')

        street = representation.pop('street')
        city = representation.pop('city')
        state = representation.pop('state')
        country = representation.pop('country')
        zip_code = representation.pop('zip_code')

        return {'street':street,'city':city,'state':state,'country':country,'zip_code':zip_code,'geo_location': {'lat': lat, 'long': long}}

# ------------------- Plant Category Serializer ----------------------------#

class PlantCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantCategory
        fields = ['id','name']

class PlantSerializer(serializers.ModelSerializer):
    
    category = PlantCategorySerializer()
    class Meta:
        model = Plant
        fields = ['id','title', 'category', 'scientific_name', 'country_of_origin']

# ------------------- Farm Plant Serializer ----------------------------#

class FarmPlantSerializer(serializers.ModelSerializer):

    plant = PlantSerializer()

    class Meta:
        model = FarmPlants
        fields = ['image_url', 'season_start', 'description' ,'season_end', 'organic', 'plant']


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        plant = representation.pop('plant')
        representation = {
            'id': instance.id,
            'title': plant['title'],
            'category': plant['category'],
            'image_url': instance.image_url,
            'description': instance.description,
            'season_start': instance.season_start,
            'season_end' : instance.season_end,
            'organic' : instance.organic,
            'scientific_name': plant['scientific_name'],
            'country_of_origin': plant['country_of_origin'],
            'plant_farm': {}
        }
        return representation


# Main Serilaizers 

# ------------------- Farm Serializers ----------------------------#

class FarmDetailSerializer(serializers.ModelSerializer):
    working_hours= WorkingHoursSerializer(many=True)
    address = FarmAddressSerializer()
    farm_plants = FarmPlantSerializer(source='plants',many=True)

    class Meta:
        model = Farm 
        fields = ['id', 
                  'image_url', 
                  'title', 
                  'working_hours', 
                  'description', 
                  'address',
                  'entrance_fee',
                  'phone', 
                  'email', 
                  'website', 
                  'farm_plants']
    
    
        
class FarmListSerializer(serializers.ModelSerializer):
    working_hours= ListWorkingHoursSerializer(many=True)
    address = FarmAddressSerializer()

    class Meta:
        model = Farm 
        fields = ['id', 
                  'image_url', 
                  'title', 
                  'working_hours', 
                  'description', 
                  'address',
                  'entrance_fee',
                  'phone', 
                  'email', 
                  'website', 
                  ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        working_hours = representation['working_hours']
        address = representation['address']
        non_null_working_hours = [wh for wh in working_hours if wh is not None]
        representation = {
            'id': instance.id,
            'image_url': instance.image_url,
            'title': instance.title,
            'working_hours': non_null_working_hours,
            'description': instance.description,
            'address': address,
            'entrance_fee': instance.entrance_fee,
            'phone': instance.phone,
            'email': instance.email,
            'website': instance.website,
            'farm_plants': []
        }
        return representation


# ------------------- Plant Serializers ----------------------------#

class PlantFarmsSerializer(serializers.ModelSerializer):
    plant = PlantSerializer()
    farm = FarmListSerializer()
    class Meta:
        model = FarmPlants
        fields = ['plant','farm']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        plant = representation.pop('plant')
        farm = representation.pop('farm')
        representation = {
            'id': instance.id,
            'title': plant['title'],
            'category': plant['category'],
            'image_url': instance.image_url,
            'description': instance.description,
            'season_start': instance.season_start,
            'season_end' : instance.season_end,
            'organic' : instance.organic,
            'scientific_name': plant['scientific_name'],
            'country_of_origin': plant['country_of_origin'],
            'plant_farm': farm
        }
        return representation
