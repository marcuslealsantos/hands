import csv
import time
from datetime import datetime

from geopy.exc import GeocoderNotFound, GeocoderTimedOut, GeocoderUnavailable, GeocoderServiceError
from geopy.geocoders import Nominatim

from .models import Address, Category, PointOfSale, SubCategory, Visit


def load_visits(file, point_of_sale=None, state=None):
    reader = csv.DictReader(open(file), delimiter=",")
    
    for item in reader:
        place = item.get('place')

        if point_of_sale and point_of_sale != place:
            continue

        code = item.get('_id')
        if not Visit.objects.filter(code=code)[:1]:
            address = get_address_by_latlong(
                item.get('lat_place'), item.get('lng_place'), geolocator=Nominatim())
            
            if state and address.city.state.code != state:
                continue

            category = Category.objects.get_or_create(
                description=item.get('category'))[0]

            subcategory = item.get('subcategory')
            if subcategory:
                subcategory = SubCategory.objects.get_or_create(
                    description=subcategory, category=category)[0]

            place = PointOfSale.objects.get_or_create(
                name=item.get('place'), 
                address=address, 
                category=category,
                subcategory=subcategory if isinstance(
                    subcategory, SubCategory) else None,)[0]

            Visit.objects.get_or_create(
                code=code,
                user_id=item.get('euid'),
                arrival=item.get('arrival'),
                departure=item.get('departure'),
                total_time_in_min=item.get('totalTimeInMin'),
                precision=item.get('precision'),
                place=place,
                pdv=True if item.get('pdv') == '1' else False,
            )
    
def get_address_by_latlong(latitude, longitude, geolocator=None):
    address = Address.objects.filter(
        latitude=latitude, longitude=longitude).first()
    if not address:
        if not geolocator:
            geolocator = Nominatim()
        #location = geolocator.reverse("%s, %s" % (latitude, longitude))
        latlong = "%s, %s" % (latitude, longitude)
        location = set_location(latlong, geolocator)

        address = Address.get_or_create(location, latitude, longitude)
    return address

def set_location(latlong, geolocator):
    try:
        location = geolocator.reverse(latlong)
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        location = retrying_set_location(latlong, geolocator)

    return location

def retrying_set_location(latlong, geolocator):
    while True:
        try:
            location = set_location(latlong, geolocator)
            return location
        except (GeocoderTimedOut,GeocoderUnavailable) as e:
            print(
                'retrying_set_location: geocoder exception ({}), retrying'.format(
                    str(e)))
        time.sleep(1.25)
