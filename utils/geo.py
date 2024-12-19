from geopy.geocoders import Nominatim

def get_address(latitude, longitude):

    geolocator = Nominatim(user_agent="Civiclink")
    

    location = geolocator.reverse((latitude, longitude), exactly_one=True)
    

    if location:

        return location.raw['address']
    else:
        return None

