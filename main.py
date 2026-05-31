# -*- coding: utf-8 -*-
import time
from src.api import NominatimAPI, OpenSkyAPI
from src.db_manager import DBManager

def get_country_by_coordinates(lat, lon, nominatim_api):
    """Определяет страну по координатам через обратный геокодинг"""
    try:
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json',
            'zoom': 3
        }
        response = requests.get("https://nominatim.openstreetmap.org/reverse", params=params, headers={'User-Agent': 'Coursework/1.0'})
        if response.status_code == 200:
            data = response.json()
            return data.get('address', {}).get('country')
    except:
        pass
    return None

def main():
    import requests
    
    # Список стран для отслеживания (минимум 4)
    countries = [
        "United States",
        "Germany", 
        "France",
        "United Kingdom",
        "Russia"
    ]
    
    # Инициализация API
    nominatim = NominatimAPI()
    opensky = OpenSkyAPI()
    
    # Инициализация БД
    db = DBManager()
    
    # Создание таблиц
    db.create_tables()
    print("[OK] Tables created")
    
    # Получение данных о странах и вставка в БД
    country_ids = {}
    for country_name in countries:
        print(f"[INFO] Getting data for country: {country_name}")
        country_data = nominatim.get_data(country_name)
        if country_data:
            country_id = db.insert_country(country_data)
            country_ids[country_name] = country_id
            print(f"[OK] Country added: {country_name}")
        else:
            print(f"[ERROR] Failed to get data for {country_name}")
        time.sleep(1)
    
    # Получение данных о самолётах
    print("\n[INFO] Getting aircraft data...")
    aeroplanes = opensky.get_data()
    print(f"[INFO] Received {len(aeroplanes)} aircraft")
    
    # Вставка самолётов в БД с определением страны
    inserted = 0
    for aeroplane in aeroplanes[:100]:
        lat = aeroplane.get('latitude')
        lon = aeroplane.get('longitude')
        
        country_id = None
        if lat and lon:
            # Простое определение по приблизительным границам (быстрее)
            if 24.5 < lat < 49.4 and -124.8 < lon < -66.9:
                country_id = country_ids.get("United States")
            elif 47.3 < lat < 55.1 and 5.9 < lon < 15.0:
                country_id = country_ids.get("Germany")
            elif 41.3 < lat < 51.1 and -5.1 < lon < 9.6:
                country_id = country_ids.get("France")
            elif 49.9 < lat < 59.4 and -8.2 < lon < 1.8:
                country_id = country_ids.get("United Kingdom")
            elif 41.2 < lat < 82.1 and 19.6 < lon < 190.1:
                country_id = country_ids.get("Russia")
        
        db.insert_aeroplane(aeroplane, country_id)
        inserted += 1
    
    print(f"[OK] Inserted {inserted} aircraft")
    
    # Демонстрация методов DBManager
    print("\n" + "="*50)
    print("STATISTICS")
    print("="*50)
    
    countries_count = db.get_countries_and_aeroplanes_count()
    print("\nCountries and aircraft count:")
    for country, count in countries_count:
        print(f"   {country}: {count}")
    
    avg_speed = db.get_avg_speed()
    if avg_speed:
        print(f"\nAverage aircraft speed: {avg_speed:.2f} m/s")
    else:
        print("\nNo speed data available")
    
    high_speed = db.get_aeroplanes_with_higher_speed()
    print(f"\nAircraft with speed above average: {len(high_speed)}")
    for aero in high_speed[:5]:
        callsign = aero[1] if aero[1] else "Unknown"
        origin = aero[2] if aero[2] else "Unknown"
        speed = aero[3] if aero[3] else 0
        print(f"   {callsign} ({origin}): {speed:.2f} m/s")
    
    db.close()
    print("\n[OK] Work completed")

if __name__ == "__main__":
    main()
