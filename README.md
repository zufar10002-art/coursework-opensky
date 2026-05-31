\# Coursework OpenSky



Проект для получения данных о самолетах из OpenSky API.



\## Установка



1\. Установите зависимости: `pip install -r requirements.txt`

2\. Создайте базу данных PostgreSQL `coursework`

3\. Настройте `.env` файл

4\. Запустите: `python main.py`



\## Методы DBManager



\- `get\_countries\_and\_aeroplanes\_count()` - страны и количество самолетов

\- `get\_all\_aeroplanes()` - все воздушные суда

\- `get\_avg\_speed()` - средняя скорость

\- `get\_aeroplanes\_with\_higher\_speed()` - самолеты со скоростью выше средней

\- `get\_aeroplanes\_with\_keyword(keyword)` - поиск по позывному

