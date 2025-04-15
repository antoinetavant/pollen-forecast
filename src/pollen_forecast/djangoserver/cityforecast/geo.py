import requests
import geoip2.database
from pathlib import Path
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os

def get_location(ip):
    
    reader = load_reader()
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

def load_reader():
    filename = Path("/tmp/GeoLite2-City.mmdb")
    if filename.exists():
        return geoip2.database.Reader(filename)
    s3 = boto3.client(
        "s3",
        endpoint_url=os.environ["MINIO_URL"],
        aws_access_key_id=os.environ["MINIO_ACCESS_KEY"],
        aws_secret_access_key=os.environ["MINIO_SECRET_KEY"],
    )
    try:
        s3.download_file(
            "pollendata",
            "GeoLite2-City.mmdb",
            "/tmp/GeoLite2-City.mmdb",
        )
        reader = geoip2.database.Reader("/tmp/GeoLite2-City.mmdb")
    except NoCredentialsError:
        raise Exception("Could not authenticate with MinIO server")
    except ClientError:
        url = "https://git.io/GeoLite2-City.mmdb"
        response = requests.get(url)
        if response.status_code == 200:
            with open("/tmp/GeoLite2-City.mmdb", "wb") as f:
                f.write(response.content)
            reader = geoip2.database.Reader("/tmp/GeoLite2-City.mmdb")
            #upload to MinIO
            try:
                s3.upload_file(
                    "/tmp/GeoLite2-City.mmdb",
                    "pollendata",
                    "GeoLite2-City.mmdb",
                )
            except ClientError as e:
                raise Exception(f"Failed to upload GeoLite2-City.mmdb to MinIO: {e}")
        else:
            raise Exception(f"Failed to download GeoLite2-City.mmdb, status code: {response.status_code}")
    return reader



def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # In case there are multiple IP addresses, take the first one
        print(x_forwarded_for)
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    if ip in ["127.0.0.1", "172.17.0.1"]:
        return "195.254.160.193"
    print(ip)
    return ip

