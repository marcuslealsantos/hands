import calendar

from django.db import models


class Country(models.Model):
    code = models.CharField(null=False, blank=False, max_length=2)
    name = models.CharField(null=True, blank=True, max_length=1024)

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
        ordering = ['name']

    def __str__(self):
        return self.code


class StateProvince(models.Model):
    code = models.CharField(null=False, blank=False, max_length=3, default="")
    name = models.CharField(null=True, blank=True, max_length=1024)
    country = models.ForeignKey(Country)

    class Meta:
        verbose_name = 'State'
        verbose_name_plural = 'States'
        ordering = ['name']

    def __str__(self):
        return self.code


class City(models.Model):
    name = models.CharField(null=True, blank=True, max_length=1024)
    state = models.ForeignKey(StateProvince)

    latitude = models.CharField(null=True, blank=True, max_length=1024)
    longitude = models.CharField(null=True, blank=True, max_length=1024)

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Address(models.Model):
    street = models.CharField(max_length=200, null=True, blank=True)
    suburb = models.CharField(max_length=200, null=True, blank=True)
    neighborhood = models.CharField(max_length=200, null=True, blank=True)
    city = models.ForeignKey(City)
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    latitude = models.CharField(null=True, blank=True, max_length=1024)
    longitude = models.CharField(null=True, blank=True, max_length=1024)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Adresses'

    def __str__(self):
        return "{} - {}, {}".format(
            self.street, self.city.name, 
            self.city.state.code, self.city.state.country.code)
    
    @staticmethod
    def get_or_create(location, latitude=None, longitude=None):
        place = location.raw['address']
        country = Country.objects.get_or_create(
                            code=place.get('country_code'), name=place.get('country'))[0]
        state = StateProvince.objects.get_or_create(
            code=place.get('state'), country=country)[0]
        city = City.objects.get_or_create(
            name=place.get('city'), state=state)[0]

        address = Address.objects.get_or_create(
                            street=place.get('road'),
                            suburb=place.get('suburb'),
                            neighborhood=place.get('neighborhood'),
                            city=city,
                            zip_code=place.get('postcode'),
                            latitude=latitude if latitude else location.latitude,
                            longitude=longitude if longitude else location.longitude)[0]
        return address

class Category(models.Model):
    description = models.CharField(null=False, blank=False, max_length=1024)

    def __str__(self):
        return self.description


class SubCategory(models.Model):
    description = models.CharField(null=False, blank=False, max_length=1024)
    category = models.ForeignKey(Category, null=True)

    def __str__(self):
        return self.description


class PointOfSale(models.Model):
    name = models.CharField(null=True, blank=True, max_length=1024)
    fantasy_name = models.CharField(null=False, blank=False, max_length=1024)
    address = models.ForeignKey(Address)
    category = models.ForeignKey(Category)
    subcategory = models.ForeignKey(SubCategory, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Visit(models.Model):
    DAYS_OF_WEEK = ( (1, 'Sunday'), (2, 'Monday'), (3, 'Tuesday'), 
        (4, 'Wednesday'), (5, 'Thursday'), (6, 'Friday'), (7, 'Saturday'),
    )
    DAY_PERIOD = (
        ('Madrugada', '00:00:00', '05:59:59'),
        ('Manhã', '06:00:00', '11:59:59'),
        ('Almoço', '12:00:00', '13:59:59'),
        ('Tarde', '14:00:00', '17:59:59'),
        ('Noite', '18:00:00', '23:59:59'),
    )
    code = models.CharField(max_length=200, null=False, blank=False)
    user_id = models.CharField(max_length=200, null=False, blank=False)
    arrival = models.DateTimeField()
    departure = models.DateTimeField()
    total_time_in_min = models.IntegerField()
    precision = models.IntegerField()
    place = models.ForeignKey(PointOfSale, null=True)
    pdv = models.BooleanField(default=False)

    class Meta:
        ordering = ['arrival']

    def __str__(self):
        if self.place:
            return "_id{} euid{} - {} arrival:{}/departure:{}".format(
                self.code, self.user_id, self.place.name, str(self.arrival), str(self.departure))
        return "_id{} euid{} - arrival:{}/departure:{}".format(
            self.code, self.user_id, str(self.arrival), str(self.departure))
    
    @property
    def get_week_day(self):
        return calendar.day_name[self.arrival.weekday()]
