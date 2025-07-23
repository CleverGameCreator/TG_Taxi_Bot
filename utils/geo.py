from geopy.distance import geodesic
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="taxi_bot")


def get_coordinates(address: str):
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    return None


def calculate_distance(point_a: str, point_b: str):
    coords_a = get_coordinates(point_a)
    coords_b = get_coordinates(point_b)

    if not coords_a or not coords_b:
        return None

    return geodesic(coords_a, coords_b).km