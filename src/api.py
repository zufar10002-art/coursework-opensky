# -*- coding: utf-8 -*-
import requests
from abc import ABC, abstractmethod

class BaseAPI(ABC):
    """Абстрактный базовый класс для API"""
    
    @abstractmethod
    def get_data(self, **kwargs):
        pass

class NominatimAPI(BaseAPI):
    """API для получения координат стран"""
    
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            'User-Agent': 'Coursework/1.0'
        }
    
    def get_data(self, country_name: str, **kwargs) -> dict:
        """
        Получает координаты страны по её названию
        
        Args:
            country_name: Название страны на английском
            
        Returns:
            Словарь с данными о стране (bounding box, координаты)
        """
        params = {
            'q': country_name,
            'format': 'json',
            'limit': 1
        }
        
        response = requests.get(self.base_url, params=params, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        if data:
            return {
                'name': country_name,
                'lat': float(data[0]['lat']),
                'lon': float(data[0]['lon']),
                'bounding_box': data[0].get('boundingbox', [])
            }
        return None

class OpenSkyAPI(BaseAPI):
    """API для получения данных о самолётах в воздухе"""
    
    def __init__(self):
        self.base_url = "https://opensky-network.org/api/states/all"
    
    def get_data(self, bounding_box: tuple = None, **kwargs) -> list:
        """
        Получает данные о самолётах в воздухе
        
        Args:
            bounding_box: Ограничивающий прямоугольник (lat_min, lat_max, lon_min, lon_max)
            
        Returns:
            Список самолётов с их данными
        """
        params = {}
        if bounding_box:
            params['lamin'] = bounding_box[0]
            params['lamax'] = bounding_box[1]
            params['lomin'] = bounding_box[2]
            params['lomax'] = bounding_box[3]
        
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        states = data.get('states', [])
        
        aeroplanes = []
        for state in states:
            if state[5] is not None and state[6] is not None:
                aeroplane = {
                    'icao24': state[0],
                    'callsign': state[1].strip() if state[1] else None,
                    'origin_country': state[2],
                    'longitude': state[5],
                    'latitude': state[6],
                    'altitude': state[7],
                    'velocity': state[9],
                    'heading': state[10],
                    'vertical_rate': state[11],
                    'on_ground': state[8]
                }
                aeroplanes.append(aeroplane)
        
        return aeroplanes
