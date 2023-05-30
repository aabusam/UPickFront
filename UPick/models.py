from django.db import models

# Create your models here.

# -------------------- FARM --------------------#

class Farm(models.Model):
    title = models.CharField(max_length=255)
    image_url = models.CharField(max_length = 2000, null = True)
    description = models.TextField(null=True)
    entrance_fee = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    phone = models.CharField(max_length=255, null = True)
    email = models.EmailField(unique=True, null = True)
    website = models.CharField(max_length = 2000, null=True)
    last_updated = models.DateTimeField(auto_now=True)

class Address(models.Model):
    # 1315 Castlemont Ave San Jose CA 95128 
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    lat = models.FloatField()
    long = models.FloatField()
    farm = models.OneToOneField(Farm, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.street} {self.city} {self.state} {self.country} {self.zip_code}"

class WorkingHour(models.Model):
    DAYS_OF_WEEK = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]
    day = models.CharField(max_length=3, choices=DAYS_OF_WEEK)
    opening_time = models.TimeField(null= True)
    closing_time = models.TimeField(null=True)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name= 'working_hours')

# -------------------- PLANT --------------------#

class PlantCategory(models.Model):
    name = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Plant(models.Model):
    title = models.CharField(max_length=255)
    scientific_name = models.CharField(max_length=255, null=True)
    country_of_origin = models.CharField(max_length=255, null=True)
    category = models.ForeignKey(PlantCategory, on_delete=models.PROTECT, related_name='plant')
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

# -------------------- Connection Models --------------------#

class FarmPlants(models.Model):
    farm = models.ForeignKey(Farm,on_delete=models.CASCADE, related_name= 'plants')
    plant = models.ForeignKey(Plant,on_delete=models.CASCADE, related_name= 'farms')
    image_url = models.CharField(max_length=2000, null = True)
    season_start = models.DateField()
    season_end = models.DateField()
    organic = models.BooleanField() 
    description = models.TextField(null=True)
