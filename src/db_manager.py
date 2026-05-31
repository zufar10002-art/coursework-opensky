# -*- coding: utf-8 -*-
import psycopg2
from src.config import Config

class DBManager:
    """Класс для работы с базой данных PostgreSQL"""
    
    def __init__(self):
        """Инициализация подключения к БД"""
        self.conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        self.cur = self.conn.cursor()
    
    def create_tables(self):
        """Создание таблиц countries и aeroplanes"""
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS countries (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                latitude FLOAT,
                longitude FLOAT,
                bounding_box TEXT
            )
        """)
        
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS aeroplanes (
                id SERIAL PRIMARY KEY,
                icao24 VARCHAR(10) NOT NULL,
                callsign VARCHAR(20),
                origin_country VARCHAR(100),
                longitude FLOAT,
                latitude FLOAT,
                altitude FLOAT,
                velocity FLOAT,
                heading FLOAT,
                vertical_rate FLOAT,
                on_ground BOOLEAN,
                country_id INTEGER REFERENCES countries(id),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        self.conn.commit()
    
    def insert_country(self, country_data: dict):
        """Вставка данных о стране"""
        self.cur.execute("""
            INSERT INTO countries (name, latitude, longitude, bounding_box)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE SET
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                bounding_box = EXCLUDED.bounding_box
            RETURNING id
        """, (country_data['name'], country_data.get('lat'), country_data.get('lon'), 
              str(country_data.get('bounding_box', []))))
        self.conn.commit()
        return self.cur.fetchone()[0]
    
    def insert_aeroplane(self, aeroplane_data: dict, country_id: int = None):
        """Вставка данных о самолёте"""
        self.cur.execute("""
            INSERT INTO aeroplanes (
                icao24, callsign, origin_country, longitude, latitude,
                altitude, velocity, heading, vertical_rate, on_ground, country_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            aeroplane_data.get('icao24'),
            aeroplane_data.get('callsign'),
            aeroplane_data.get('origin_country'),
            aeroplane_data.get('longitude'),
            aeroplane_data.get('latitude'),
            aeroplane_data.get('altitude'),
            aeroplane_data.get('velocity'),
            aeroplane_data.get('heading'),
            aeroplane_data.get('vertical_rate'),
            aeroplane_data.get('on_ground'),
            country_id
        ))
        self.conn.commit()
    
    def get_countries_and_aeroplanes_count(self):
        """Получает список всех стран и количество самолётов в их воздушных пространствах"""
        self.cur.execute("""
            SELECT c.name, COUNT(a.id) as aeroplanes_count
            FROM countries c
            LEFT JOIN aeroplanes a ON c.id = a.country_id
            GROUP BY c.name
            ORDER BY aeroplanes_count DESC
        """)
        return self.cur.fetchall()
    
    def get_all_aeroplanes(self):
        """Получает список всех воздушных судов"""
        self.cur.execute("""
            SELECT icao24, callsign, origin_country, latitude, longitude, velocity
            FROM aeroplanes
            WHERE on_ground = FALSE
        """)
        return self.cur.fetchall()
    
    def get_avg_speed(self):
        """Получает среднюю скорость по самолётам"""
        self.cur.execute("SELECT AVG(velocity) FROM aeroplanes WHERE velocity IS NOT NULL")
        return self.cur.fetchone()[0]
    
    def get_aeroplanes_with_higher_speed(self):
        """Получает список всех самолётов, у которых скорость выше средней"""
        avg_speed = self.get_avg_speed()
        self.cur.execute("""
            SELECT icao24, callsign, origin_country, velocity
            FROM aeroplanes
            WHERE velocity > %s AND velocity IS NOT NULL
            ORDER BY velocity DESC
        """, (avg_speed,))
        return self.cur.fetchall()
    
    def get_aeroplanes_with_keyword(self, keyword: str):
        """Получает список всех самолётов, в позывном которых содержатся переданные символы"""
        self.cur.execute("""
            SELECT icao24, callsign, origin_country, velocity
            FROM aeroplanes
            WHERE callsign ILIKE %s
        """, (f'%{keyword}%',))
        return self.cur.fetchall()
    
    def close(self):
        """Закрывает соединение с БД"""
        self.cur.close()
        self.conn.close()
