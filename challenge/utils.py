from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from challenge.redis_client import publish_event
import requests


def send_email(data: dict) -> bool:
    template, email_txt = "inbound_parser.html", "inbound_parser.txt"
    html_content = render_to_string(template, data)
    plain_content = render_to_string(email_txt, data)
    email = EmailMultiAlternatives(
        data["subject"],
        plain_content,
        settings.SENDER_EMAIL,
        [settings.EMAIL_HOST_USER],
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)


def inbound_notify(data: dict):

    ip = data.get("ip")

    geo_info = get_geo_info(ip)
    weather_info = get_weather_info(
        geo_info.get("latitude"), geo_info.get("longitude")
    )

    data.update(geo_info=geo_info, weather_info=weather_info)

    publish_event("notification", {"event": "inbound_notify", "data": data})


def get_geo_info(ip: str) -> dict:
    url = "https://api.ipgeolocation.io/ipgeo"
    res = requests.get(
        url, params={"apiKey": settings.IPGEO_API_KEY, "ip": ip}
    )

    if res.status_code == 200:
        data = res.json()
        return {
            "ip": ip,
            "continent_name": data.get("continent_name"),
            "country": data.get("country_name"),
            "state_prov": data.get("state_prov"),
            "country_emoji": data.get("country_flag_emoji", "🌍"),
            "city": data.get("city"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
        }

    return {}


def get_weather_info(lat: str, lon: str) -> dict:
    weather_info = []

    url = "http://api.openweathermap.org/data/2.5/air_pollution"
    for_url = "http://api.openweathermap.org/data/2.5/air_pollution/forecast"

    res = requests.get(
        url, params={"appid": settings.WEATHER_API_KEY, "lat": lat, "lon": lon}
    )

    if res.status_code == 200:
        data = res.json()
        aqi = data.get("list")[0].get("main").get("aqi")
        compenents = data.get("list")[0].get("components")

        weather_info.append({"current": [aqi, compenents]})
    else:
        weather_info.append({"current": {}})

    
    res = requests.get(
        for_url, params={"appid": settings.WEATHER_API_KEY, "lat": lat, "lon": lon}
    )
    if res.status_code == 200:
        data = res.json()
        for info in enumerate(data.get("list")):
            index, info = info[0], info[-1]
            if index == 5:
                break
            aqi = info.get("main").get("aqi")
            compenents = info.get("components")
            forcast = f"forecast_{index}"
            weather_info.append({forcast: [aqi, compenents]})
    else:
        weather_info.append({"forecast": {}})

    return weather_info
