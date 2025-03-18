import requests
import geoip2.database

def get_location(ip):
    reader = geoip2.database.Reader(r"C:\Users\antoi\Documents\projets\pollen-forecast\GeoLite2-City_20250311\GeoLite2-City.mmdb")
    try:
        response = reader.city(ip)
        return {
            "city": response.city.name,
            "country": response.country.name,
            "latitude": response.location.latitude,
            "longitude": response.location.longitude,
        }
    except geoip2.errors.AddressNotFoundError:
        return {"error": "IP not found"}



def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # In case there are multiple IP addresses, take the first one
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    if ip == "127.0.0.1":
        return "195.254.160.193"
    return ip

