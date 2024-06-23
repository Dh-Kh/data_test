from dotenv import load_dotenv
from datetime import datetime
from sklearn.cluster import KMeans
from typing import List
from numpy import insert
from time import sleep
import os
import requests
import googlemaps
import pytz

load_dotenv()

TOMTOM = os.getenv("TOMTOM")

GMAPS = os.getenv("GMAPS")

class MarketGeo(object):
        
    """
    DOCS: https://developer.tomtom.com/routing-api/api-explorer
    """

    def __init__(self, geo_data: List[List[float]]):
        self.geo_data = geo_data
        
    def merge_points(self, geo_input: List[List[float]]) -> List[List[float]]:
        #k calculated by Elbow Method 
        kmeans_kwargs = {
            "init": "random",
            "n_init": 10,
            "max_iter": 300,
            "random_state": 42,
        }
        
        kmeans = KMeans(n_clusters=4, **kmeans_kwargs)

        kmeans.fit(geo_input)
        
        centroids = kmeans.cluster_centers_

        return centroids
        
    def waypointOptimization(self, departure_time="now")  -> List[List[float]]:
        
        if len(self.geo_data) == 0:
            raise ValueError("Geodata must not be empty!")
            
        self.geo_data = self.merge_points(self.geo_data)
        
        self.geo_data = insert(self.geo_data, 0, [50.454444, 30.516667], axis=0) #Південний вокзал
        
        waypoints = [
            {"point": {"latitude": lat, "longitude": lon}, 
            "serviceTimeInSeconds": 600
            }  
            for lat, lon in self.geo_data
        ]
        
       
        waypoints_url = f"https://api.tomtom.com/routing/waypointoptimization/1/?key={TOMTOM}"
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
             "waypoints": waypoints,
             "options": {
                "waypointConstraints": {
                    "originIndex": 0,
                },
                "travelMode": "car",
                "departAt": departure_time,
                "outputExtensions": ["travelTimes"], 
             }
        }
        
        
        
        try:
            r = requests.post(waypoints_url, headers=headers, json=payload)
            
            r.raise_for_status()
            
            data = r.json()
            
            return data
        
        except requests.exceptions.RequestException as e:
            raise e
        except requests.exceptions.JSONDecodeError as e:
            raise e
            
    @staticmethod
    def convert_addresses_to_geo(input_list: List[str]) -> List[List[float]]:
        gmaps = googlemaps.Client(key=GMAPS)
        geo_data = []

        for address in input_list:
            try:
                geocode_result = gmaps.geocode(address)
                if geocode_result: 
                    lat = geocode_result[0]["geometry"]["location"]["lat"]
                    lng = geocode_result[0]["geometry"]["location"]["lng"]
                    geo_data.append([lat, lng])
                else:
                    print(f"Warning: No geocoding results found for '{address}'")
            except googlemaps.exceptions.ApiError as e:
                print(f"Error geocoding '{address}': {e}")

        return geo_data
            

def convert_hours_to_timestamp(hours: int) -> str:
    
    kiev_tz = pytz.timezone('Europe/Kiev')
    current_time = datetime.now(kiev_tz).replace(hour=hours, minute=0, second=0, microsecond=0)
    timestamp = current_time.strftime('%Y-%m-%dT%H:%M:%S%z')
    timestamp = timestamp[:-2] + ':' + timestamp[-2:]
    return timestamp

def convert_timestamp_to_hours(timestamp: str) -> str:

    dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S%z')
    dt = dt.astimezone(pytz.timezone('Europe/Kiev'))
    hours = dt.strftime('%H:%M')
    return hours


def main():
    """"
    INFO: https://epicentrk.ua/ua/addresses/
    """
    
    input_list = [
           "Київ, пр-т Степана Бандери, 36-А",       
           "Київ, пр-т Степана Бандери, 11-А",
           "Київ, Дніпровська наб., 13-В",
           "Київ, вул. Братиславська, 11",
           "Київ, вул. Полярна, 20-Д",
           "Київ, Кільцева дорога, 1-Б",
           "Київ, пр-т Петра Григоренка, 40",
           "Київ, вул. Оноре де Бальзака, 65/1",
           "Бучанський район, с. Петропавлівська Борщагівка, вул. Кришталева, 6",
           "Київ, вул. Берковецька, 6-В"
    ]
    
    geo_data = MarketGeo.convert_addresses_to_geo(input_list)
    market_geo = MarketGeo(geo_data)
    
    while True:
        try:
            start_hour = int(input("Enter the start hour (>= 8): "))
            end_hour = int(input("Enter the end hour (<= 22): "))
            if start_hour < 8 or end_hour > 22 or start_hour >= end_hour:
                raise ValueError("Invalid input. Start hour must be >= 8 and end hour must be <= 22, and start hour must be less than end hour.")
            break
        except ValueError as e:
            print(e)
    
    best_time = 0
    min_time = float('inf')

    print("sleep to avoid HTTPError: 429 Client Error")

    for i in range(start_hour, end_hour):
    
        sleep(1)
        
        total_time = 0
        departure_time = convert_hours_to_timestamp(i)
        
        result = market_geo.waypointOptimization(departure_time)
                
        if 'summary' not in result:
            raise ValueError("Invalid result!")
            
        total_time = result['summary']['routeSummary']['travelTimeInSeconds'] + \
        result['summary']['routeSummary']['serviceTimeInSeconds']
        
        if total_time < min_time:
            min_time = total_time
            best_time = departure_time
            
    if best_time:
        print(f"Optimal departure time: {convert_timestamp_to_hours(best_time)}")
        print(f"Total time (travel + service): {min_time / 60:.2f} minutes")
        

    
    
if __name__ == "__main__":
    main()     