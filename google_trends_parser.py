"""
Парсер Google Trends для получения данных о поисковых запросах
"""
import time
import random
from pytrends.request import TrendReq
import pandas as pd
from config import GEO, CATEGORY, REQUEST_DELAY, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX, TIMEFRAMES

# Список user-agent заголовков для ротации
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
]


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
        self.request_count = 0
        self.current_user_agent = random.choice(USER_AGENTS)
        self.reinit_pytrends()
        
    def get_random_delay(self):
        """Возвращает случайную задержку между delay_min и delay_max"""
        return random.uniform(self.delay_min, self.delay_max)
    
    def reinit_pytrends(self):
        """Переинициализация pytrends с новым user-agent"""
        self.pytrends = TrendReq(hl='ru-RU', tz=180, requests_args={'headers': {'User-Agent': self.current_user_agent}})
    
    def retry_with_backoff(self, func, max_retries=3, initial_delay=30):
        """
        Выполняет функцию с экспоненциальной задержкой при ошибках
        
        Args:
            func: Функция для выполнения
            max_retries: Максимальное количество повторов
            initial_delay: Начальная задержка в секундах
            
        Returns:
            Результат функции или None при неудаче
        """
        for attempt in range(max_retries):
            try:
                result = func()
                if result is not None:
                    return result
            except Exception as e:
                print(f"    Попытка {attempt + 1}/{max_retries} не удалась: {e}")
                
                if attempt < max_retries - 1:
                    # Экспоненциальная задержка с jitter
                    delay = initial_delay * (2 ** attempt) + random.uniform(0, 10)
                    print(f"    Ждем {delay:.1f} сек перед повторной попыткой...")
                    
                    # Меняем user-agent при каждой повторной попытке
                    self.current_user_agent = random.choice(USER_AGENTS)
                    self.reinit_pytrends()
                    print(f"    Новый User-Agent: {self.current_user_agent[:50]}...")
                    
                    time.sleep(delay)
                else:
                    print(f"    Все {max_retries} попыток исчерпаны")
                    
        return None
        
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
    
    def get_average_interest(self, queries, timeframe, use_retry=True):
        """
        Получает средний интерес к запросам за период
        
        Args:
            queries: Список запросов
            timeframe: Период времени
            use_retry: Использовать ли механизм ретраев
            
        Returns:
            dict: {query: average_interest} или None если ошибка
        """
        def _get_data():
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
        
        if use_retry:
            return self.retry_with_backoff(_get_data)
        else:
            return _get_data()
    
    def parse_country_queries(self, country_name, queries, timeframes):
        """
        Парсит все запросы для одной страны за все периоды
        
        Args:
            country_name: Название страны
            queries: Список запросов для страны
            timeframes: Словарь с периодами {name: value}
            
        Returns:
            dict: Данные по всем запросам и периодам или None если ошибка
        """
        country_data = {
            "country": country_name,
            "queries": {}
        }
        
        has_valid_data = False
        
        # Получаем данные для каждого периода
        for period_name, period_value in timeframes.items():
            period_data = {}
            
            # Получаем средний интерес для всех запросов (с ретраями)
            averages = self.get_average_interest(queries, period_value, use_retry=True)
            
            if averages:
                # Проверяем что есть хотя бы один запрос с положительным значением
                valid_values = [v for v in averages.values() if v is not None and v > 0]
                
                if valid_values:
                    has_valid_data = True
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
        
        # Если нет валидных данных ни в одном периоде, возвращаем None
        if not has_valid_data:
            print(f"    ❌ {country_name}: не удалось получить данные (все запросы с 0)")
            return None
        
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
            
            # Проверяем, есть ли данные
            if country_data is None:
                # Сообщение уже выведено в parse_country_queries
                pass
            elif any(period_data for period_data in country_data["queries"].values()):
                print(f"    ✓ {country_name} успешно распаршена")
            else:
                print(f"    ⚠ {country_name}: нет данных (возможно, заблокировано)")
            
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