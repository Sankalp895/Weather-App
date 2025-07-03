import requests
from dotenv import load_dotenv
import os
from dataclasses import dataclass

load_dotenv()
api_key = os.getenv('API_KEY')

@dataclass
class WeatherData:
     main: str
     description: str
     icon: str
     temperature: float

def get_lat(city_name, state_code, country_code, API_key):
    resp = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city_name},{state_code},{country_code}&appid={API_key}').json()
    if not resp:
        raise ValueError(f"Location not found for: {city_name}, {state_code}, {country_code}")
    data = resp[0] #since it is a list we take the first item.
    lat = data.get('lat')
    return lat

def get_lon(city_name, state_code, country_code, API_key):
    resp = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city_name},{state_code},{country_code}&appid={API_key}').json()
    data = resp[0] #since it is a list we take the first item.
    lon = data.get('lon')
    return lon

def get_current_weather(lat, lon, API_key):
    resp = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_key}&units=metric').json()
    data = WeatherData(
        main=resp.get('weather')[0].get('main'),
        description=resp.get('weather')[0].get('description'),
        icon=resp.get('weather')[0].get('icon'),
        temperature=resp.get('main').get('temp')
    )
    return data
def main(city_name, state_name, country_name):
    lat = get_lat(city_name, state_name, country_name, api_key)
    lon = get_lon(city_name, state_name, country_name, api_key)
    current = get_current_weather(lat, lon, api_key)
    forecast = get_5_day_forecast(lat, lon, api_key)
    return {
        'current': current,
        'forecast': forecast
    }

def get_5_day_forecast(lat, lon, API_key):
    url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_key}&units=metric' # here the api 40 entries. 40*3 = 120, 120 / 24 = 5(days)
    resp = requests.get(url).json()
    
    # Extract one forecast per day (every 8th result in 3-hour interval data)
    forecast_list = []
    for i in range(0, len(resp['list']), 8): # 24/3 = 8( her 8 is 8 forecasts perday)
        item = resp['list'][i]
        forecast_list.append({
            'date': item['dt_txt'].split()[0],
            'temp': item['main']['temp'],
            'main': item['weather'][0]['main'],
            'desc': item['weather'][0]['description'],
            'icon': item['weather'][0]['icon']
        })
    
    return forecast_list    
if __name__== "__main__": #for testing
    lat = get_lat('Toronto', 'ON', 'CANADA', api_key)
    lon = get_lon('Toronto', 'ON', 'CANADA', api_key)
    print(get_current_weather(lat, lon, api_key))
    print(get_5_day_forecast(lat, lon, api_key))

print("API Key Loaded:", api_key)