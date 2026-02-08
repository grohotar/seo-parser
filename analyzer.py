"""
Анализатор данных SEO-запросов
"""
from datetime import datetime


class SEOAnalyzer:
    """Класс для анализа данных SEO-запросов"""
    
    def __init__(self, all_data):
        """
        Инициализация анализатора
        
        Args:
            all_data: Словарь с данными по всем странам
        """
        self.all_data = all_data
        self.analyzed = {}
        
    def analyze_all_countries(self):
        """
        Анализирует данные по всем странам
        
        Returns:
            dict: Анализированные данные
        """
        self.analyzed = {
            "countries": {},
            "ranking": {},
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        for country_name, country_data in self.all_data.items():
            self.analyzed["countries"][country_name] = self._analyze_country(country_data)
        
        # Создаем рейтинг стран
        self._create_rankings()
        
        return self.analyzed
    
    def _analyze_country(self, country_data):
        """
        Анализирует данные одной страны
        
        Args:
            country_data: Данные по одной стране
            
        Returns:
            dict: Анализированные данные страны
        """
        analysis = {
            "country": country_data["country"],
            "periods": {}
        }
        
        for period_name, period_data in country_data["queries"].items():
            if period_data and period_data.get("max_interest", 0) > 0:
                period_analysis = {
                    "max_interest": period_data["max_interest"],
                    "top_query": period_data["top_query"],
                    "all_interests": period_data["averages"],
                    "related_queries": period_data.get("related_queries", {})
                }
                analysis["periods"][period_name] = period_analysis
        
        return analysis
    
    def _create_rankings(self):
        """
        Создает рейтинги стран по популярности
        """
        # Рейтинг за 3 месяца (основной)
        ranking_3m = []
        ranking_1m = []
        
        for country_name, analysis in self.analyzed["countries"].items():
            # Данные за 3 месяца
            if "3_months" in analysis["periods"]:
                ranking_3m.append({
                    "country": country_name,
                    "interest": analysis["periods"]["3_months"]["max_interest"],
                    "top_query": analysis["periods"]["3_months"]["top_query"]
                })
            
            # Данные за 1 месяц
            if "1_month" in analysis["periods"]:
                ranking_1m.append({
                    "country": country_name,
                    "interest": analysis["periods"]["1_month"]["max_interest"],
                    "top_query": analysis["periods"]["1_month"]["top_query"]
                })
        
        # Сортируем по убыванию интереса
        ranking_3m.sort(key=lambda x: x["interest"], reverse=True)
        ranking_1m.sort(key=lambda x: x["interest"], reverse=True)
        
        self.analyzed["ranking"]["3_months"] = ranking_3m
        self.analyzed["ranking"]["1_month"] = ranking_1m
        
        # Вычисляем изменение (рост/падение)
        self._calculate_trend()
    
    def _calculate_trend(self):
        """
        Вычисляет тренд (рост/падение) между периодами
        """
        trends = []
        
        for country_name, analysis in self.analyzed["countries"].items():
            if "1_month" in analysis["periods"] and "3_months" in analysis["periods"]:
                interest_1m = analysis["periods"]["1_month"]["max_interest"]
                interest_3m = analysis["periods"]["3_months"]["max_interest"]
                
                if interest_3m > 0:
                    change_percent = ((interest_1m - interest_3m) / interest_3m) * 100
                else:
                    change_percent = 0
                
                trends.append({
                    "country": country_name,
                    "interest_1m": interest_1m,
                    "interest_3m": interest_3m,
                    "change_percent": change_percent
                })
        
        self.analyzed["trends"] = trends
    
    def get_top_countries(self, period="3_months", limit=20):
        """
        Возвращает топ стран по популярности
        
        Args:
            period: Период анализа (1_month или 3_months)
            limit: Количество стран в топе
            
        Returns:
            list: Топ стран
        """
        return self.analyzed["ranking"].get(period, [])[:limit]
    
    def get_rising_countries(self, limit=10):
        """
        Возвращает страны с растущим спросом
        
        Args:
            limit: Количество стран
            
        Returns:
            list: Страны с ростом
        """
        rising = [t for t in self.analyzed["trends"] if t["change_percent"] > 0]
        rising.sort(key=lambda x: x["change_percent"], reverse=True)
        return rising[:limit]
    
    def get_falling_countries(self, limit=10):
        """
        Возвращает страны с падающим спросом
        
        Args:
            limit: Количество стран
            
        Returns:
            list: Страны с падением
        """
        falling = [t for t in self.analyzed["trends"] if t["change_percent"] < 0]
        falling.sort(key=lambda x: x["change_percent"])
        return falling[:limit]
    
    def get_related_queries(self, country_name, period="3_months", limit=10):
        """
        Возвращает связанные запросы для страны
        
        Args:
            country_name: Название страны
            period: Период анализа
            limit: Количество запросов
            
        Returns:
            dict: Связанные запросы (top и rising)
        """
        if country_name not in self.analyzed["countries"]:
            return None
        
        period_data = self.analyzed["countries"][country_name]["periods"].get(period)
        if not period_data:
            return None
        
        related = period_data.get("related_queries", {})
        result = {
            "top": [],
            "rising": []
        }
        
        # Top запросы
        if "top" in related and related["top"] is not None:
            top_queries = related["top"].head(limit).to_dict('records')
            result["top"] = [
                {"query": q["query"], "interest": q["value"]}
                for q in top_queries
            ]
        
        # Rising запросы
        if "rising" in related and related["rising"] is not None:
            rising_queries = related["rising"].head(limit).to_dict('records')
            result["rising"] = [
                {"query": q["query"], "interest": q["value"]}
                for q in rising_queries
            ]
        
        return result
    
    def get_all_queries_interest(self, country_name, period="3_months"):
        """
        Возвращает интерес по всем вариациям запросов для страны
        
        Args:
            country_name: Название страны
            period: Период анализа
            
        Returns:
            list: Список запросов с их интересом
        """
        if country_name not in self.analyzed["countries"]:
            return None
        
        period_data = self.analyzed["countries"][country_name]["periods"].get(period)
        if not period_data:
            return None
        
        interests = period_data.get("all_interests", {})
        result = [
            {"query": query, "interest": value if value is not None else 0}
            for query, value in interests.items()
        ]
        
        # Сортируем по убыванию интереса
        result.sort(key=lambda x: x["interest"], reverse=True)
        
        return result


if __name__ == "__main__":
    # Тест анализатора с тестовыми данными
    test_data = {
        "Турция": {
            "country": "Турция",
            "queries": {
                "3_months": {
                    "max_interest": 95,
                    "top_query": "турецкий впн",
                    "averages": {
                        "турецкий впн": 95,
                        "впн турция": 85,
                        "turkey vpn": 70
                    }
                },
                "1_month": {
                    "max_interest": 98,
                    "top_query": "турецкий впн",
                    "averages": {
                        "турецкий впн": 98,
                        "впн турция": 90,
                        "turkey vpn": 75
                    }
                }
            }
        },
        "Казахстан": {
            "country": "Казахстан",
            "queries": {
                "3_months": {
                    "max_interest": 80,
                    "top_query": "казахский впн",
                    "averages": {
                        "казахский впн": 80,
                        "впн казахстан": 75
                    }
                },
                "1_month": {
                    "max_interest": 70,
                    "top_query": "казахский впн",
                    "averages": {
                        "казахский впн": 70,
                        "впн казахстан": 65
                    }
                }
            }
        }
    }
    
    analyzer = SEOAnalyzer(test_data)
    analyzed = analyzer.analyze_all_countries()
    
    print("Топ стран за 3 месяца:")
    for country in analyzer.get_top_countries("3_months"):
        print(f"  {country['country']}: {country['interest']}")
    
    print("\nРастущие страны:")
    for country in analyzer.get_rising_countries():
        print(f"  {country['country']}: +{country['change_percent']:.1f}%")