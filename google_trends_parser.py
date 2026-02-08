"""
Парсер Google Trends для получения данных о поисковых запросах
"""
import time
import random
from pytrends.request import TrendReq
import pandas as pd
from config import GEO, CATEGORY, REQUEST_DELAY, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX, TIMEFRAMES


class GoogleTrendsParser:
    """Класс для парсинга данных из Google Trends"""
    
    def __init__(self, geo="RU", category=CATEGORY, delay_min=REQUEST_DELAY_MIN, delay_max=REQUEST_DELAY_MAX):
        """
        Инициализация парсера
        
        Args:
            geo: Код страны для геолокации (RU - Россия)
            category: Категория поиска (13 - IT/Интернет)
            delay_min: Минимальная задержка между запросами в секундах
            delay_max: Максимальная задержка между запросами в секундах
        """
        self.geo = geo
        self.category = category
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.pytrends = TrendReq(hl='ru-RU', tz=180)
        self.request_count = 0
        
    def get_random_delay(self):
        """Возвращает случайную задержку между delay_min и delay_max"""
        return random.uniform(self.delay_min, self.delay_max)
        
    def get_interest_over_time(self, queries, timeframe):
        """
        Получает интерес к запросам во времени
        
        Args:
            queries: Список запросов (максимум 5 за раз)
            timeframe: Период времени (например, "today 3-m")
            
        Returns:
            DataFrame: Данные интереса во времени
        """
        try:
            self.pytrends.build_payload(
                queries,
                cat=self.category,
                timeframe=timeframe,
                geo=self.geo
            )
            data = self.pytrends.interest_over_time()
            
            self.request_count += 1
            if self.request_count > 1:
                delay = self.get_random_delay()
                print(f"    Задержка: {delay:.1f} сек...")
                time.sleep(delay)
                
            return data
        except Exception as e:
            print(f"Ошибка при получении данных для {queries}: {e}")
            return None
    
    def get_interest_by_region(self, queries, timeframe):
        """
        Получает интерес к запросам по регионам
        
        Args:
            queries: Список запросов (максимум 5 за раз)
            timeframe: Период времени
            
        Returns:
            DataFrame: Данные интереса по регионам
        """
        try:
            self.pytrends.build_payload(
                queries,
                cat=self.category,
                timeframe=timeframe,
                geo=self.geo
            )
            data = self.pytrends.interest_by_region(resolution='COUNTRY')
            
            self.request_count += 1
            if self.request_count > 1:
                delay = self.get_random_delay()
                time.sleep(delay)
                
            return data
        except Exception as e:
            print(f"Ошибка при получении региональных данных для {queries}: {e}")
            return None
    
    def get_related_queries(self, query, timeframe):
        """
        Получает связанные запросы
        
        Args:
            query: Поисковый запрос
            timeframe: Период времени
            
        Returns:
            dict: Связанные запросы (rising и top)
        """
        try:
            self.pytrends.build_payload(
                [query],
                cat=self.category,
                timeframe=timeframe,
                geo=self.geo
            )
            data = self.pytrends.related_queries()
            
            self.request_count += 1
            if self.request_count > 1:
                delay = self.get_random_delay()
                time.sleep(delay)
                
            return data.get(query, {})
        except Exception as e:
            print(f"Ошибка при получении связанных запросов для {query}: {e}")
            return {}
    
    def get_average_interest(self, queries, timeframe):
        """
        Получает средний интерес к запросам за период
        
        Args:
            queries: Список запросов
            timeframe: Период времени
            
        Returns:
            dict: {query: average_interest} или None если ошибка
        """
        try:
            data = self.get_interest_over_time(queries[:5], timeframe)
            
            if data is None or data.empty:
                return None
            
            # Удаляем столбец isPartial если есть
            if 'isPartial' in data.columns:
                data = data.drop(columns=['isPartial'])
            
            # Вычисляем среднее значение для каждого запроса
            averages = {}
            for query in queries[:5]:
                if query in data.columns:
                    averages[query] = data[query].mean()
                else:
                    averages[query] = 0
                    
            return averages
        except Exception as e:
            print(f"Ошибка при вычислении среднего интереса: {e}")
            return None
    
    def parse_country_queries(self, country_name, queries, timeframes):
        """
        Парсит все запросы для одной страны за все периоды
        
        Args:
            country_name: Название страны
            queries: Список запросов для страны
            timeframes: Словарь с периодами {name: value}
            
        Returns:
            dict: Данные по всем запросам и периодам
        """
        country_data = {
            "country": country_name,
            "queries": {}
        }
        
        # Получаем данные для каждого периода
        for period_name, period_value in timeframes.items():
            period_data = {}
            
            # Получаем средний интерес для всех запросов
            averages = self.get_average_interest(queries, period_value)
            
            if averages:
                # Находим запрос с максимальным интересом
                max_query = max(averages.items(), key=lambda x: x[1] if x[1] is not None else 0)
                
                period_data = {
                    "averages": averages,
                    "max_interest": max_query[1] if max_query[1] is not None else 0,
                    "top_query": max_query[0],
                    "all_queries": queries
                }
                
                # Получаем связанные запросы для топ запроса
                related = self.get_related_queries(max_query[0], period_value)
                if related:
                    period_data["related_queries"] = related
            
            country_data["queries"][period_name] = period_data
        
        return country_data
    
    def parse_all_countries(self, all_queries, timeframes):
        """
        Парсит данные для всех стран
        
        Args:
            all_queries: Словарь {country_name: [queries]}
            timeframes: Словарь с периодами
            
        Returns:
            dict: Данные по всем странам
        """
        all_data = {}
        total_countries = len(all_queries)
        
        print(f"Начинаем парсинг {total_countries} стран...")
        print("=" * 60)
        
        for idx, (country_name, queries) in enumerate(all_queries.items(), 1):
            print(f"[{idx}/{total_countries}] Парсим {country_name}...")
            
            country_data = self.parse_country_queries(country_name, queries, timeframes)
            all_data[country_name] = country_data
            
            # Задержка между странами со случайным значением
            if idx < total_countries:
                delay = self.get_random_delay()
                print(f"    Задержка между странами: {delay:.1f} сек...")
                time.sleep(delay)
        
        print("=" * 60)
        print(f"Парсинг завершен! Всего запросов: {self.request_count}")
        
        return all_data


if __name__ == "__main__":
    from query_builder import generate_all_queries
    from config import COUNTRIES
    
    # Тест парсера
    parser = GoogleTrendsParser()
    
    # Генерируем запросы
    all_queries = generate_all_queries(COUNTRIES)
    
    # Тестируем на одной стране
    test_country = "Турция"
    print(f"Тест парсера для {test_country}")
    print("-" * 60)
    
    queries = all_queries[test_country]
    data = parser.parse_country_queries(test_country, queries, TIMEFRAMES)
    
    print(f"\nРезультаты для {test_country}:")
    for period, period_data in data["queries"].items():
        if period_data:
            print(f"\nПериод {period}:")
            print(f"  Топ запрос: {period_data['top_query']}")
            print(f"  Макс. интерес: {period_data['max_interest']}")
        else:
            print(f"\nПериод {period}: Нет данных")