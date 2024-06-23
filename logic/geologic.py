from dotenv import load_dotenv
from typing import List
import os
import requests

load_dotenv()

TOMTOM = os.getenv("TOMTOM")

class MarketGeo(object):
    
    """
    DOCS: https://developer.tomtom.com/routing-api/api-explorer
    """

    def __init__(self, geo_data: List[List[float]]):
        self.geo_data = geo_data
        
    def waypointOptimization(self)  -> List[List[float]]:
        
        waypoints = [
            {"point": {"latitude": lat, "longitude": lon}, "serviceTimeInSeconds": 600}  
            for lat, lon in self.geo_data
        ]
        
        waypoints_url = f"https://api.tomtom.com/routing/waypointoptimization/1/?key={TOMTOM}"
        
        headers = {
            'Content-Type': 'application/json'
            }
        
        payload = {
             "waypoints": waypoints,
             "options": {
                "waypointConstraints": {
                    "originIndex": 1,
                },
                "travelMode": "car",
                "departAt": "now",
                "outputExtensions": ["travelTimes"], 
             }
        }
        
        try:
            r = requests.post(waypoints_url, headers=headers, json=payload)
            
            r.raise_for_status()
            
            data = r.json()
            
            optimized_waypoint = [self.geo_data[i] for i in data['optimizedOrder']]

            return optimized_waypoint
        
        except requests.exceptions.RequestException as e:
            raise e
        except requests.exceptions.JSONDecodeError as e:
            raise e
        
if __name__ == "__main__":
    
    def main():
        m = MarketGeo(geo_data=[])
        return m.waypointOptimization()
    
    main()     